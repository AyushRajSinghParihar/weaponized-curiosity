def batch_membership(values: list[int], queries: list[int]) -> list[bool]:
    """Return membership for each query, preserving order and duplicate queries."""
    return [query in values for query in queries]
