"""Optimize membership by indexing the values."""


def batch_membership(values: list[int], queries: list[int]) -> list[bool]:
    if len(queries) <= 8:
        return [query in values for query in queries]
    members = set(values)
    return [query in members for query in queries]
