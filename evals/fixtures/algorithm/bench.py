"""Repeat a membership workload with independent seeds for two splits."""
import argparse
import json
import random
import statistics
import time

from membership import batch_membership


def inputs(split):
    rng = random.Random(19273 if split == "search" else 84113)
    inputs = [([], []), ([], [0, -1]), ([1, 1, -1], [1, 0, -1, 1])]
    if split == "validation":
        inputs.extend([
            ([-10**30, 0, 10**30], [10**30, -10**30 - 1, 0, 2]),
            (list(range(-500, 500)), list(range(-1_200, 1_200))),
        ])
    workload_count = 3 if split == "search" else 4
    for workload in range(workload_count):
        size = 1_000 + workload * 751
        magnitude = size * (4 if workload % 2 == 0 else 12)
        values = rng.choices(range(-magnitude, magnitude), k=size)
        queries = rng.choices(values, k=size)
        queries.extend(rng.choices(range(-magnitude, magnitude), k=size))
        rng.shuffle(queries)
        inputs.append((values, queries))
    return inputs


def run(split, repeat):
    cases = inputs(split)
    expected = [[query in values for query in queries] for values, queries in cases]
    samples = []
    for _ in range(repeat):
        started = time.perf_counter()
        actual = [batch_membership(values, queries) for values, queries in cases]
        samples.append(time.perf_counter() - started)
        if actual != expected:
            raise SystemExit("Incorrect batch membership")
    print(json.dumps({
        "split": split, "cases": len(cases), "repeat": repeat,
        "seconds": samples, "median_seconds": statistics.median(samples),
        "correct": True,
    }))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--split", choices=("search", "validation"), default="search")
    parser.add_argument("--repeat", type=int, choices=range(1, 10), default=5)
    args = parser.parse_args()
    run(args.split, args.repeat)
