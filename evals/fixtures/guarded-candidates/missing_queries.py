def batch_membership(values: list[int], queries: list[int]) -> list[bool]:
    """Return membership for each query, preserving order and duplicate queries."""
    if len(queries) >= 16 and len(values) >= 512:
        missing = set(queries)
        missing.difference_update(values)
        return [query not in missing for query in queries]
    return [query in values for query in queries]
