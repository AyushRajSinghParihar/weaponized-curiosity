"""Bound the index by the number of requested keys on the target workload."""


def batch_membership(values: list[int], queries: list[int]) -> list[bool]:
    if len(queries) <= 8:
        return [query in values for query in queries]
    matches = set(queries).intersection(values)
    return [query in matches for query in queries]
