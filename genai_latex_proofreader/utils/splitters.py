from typing import Callable, Optional, TypeVar

A = TypeVar("A")
B = TypeVar("B")


def split_at_first_lambda(
    xs: list[A], f: Callable[[A], Optional[B]]
) -> tuple[list[A], Optional[B], list[A]]:
    """
    Partition an input list 'xs' at point where 'f' first returns a non-null value.

    Example outputs for xs = [1, 2, 3]
        [], b, [2, 3]:            f returns b for x=1
        [1], b, [2, 3]:           f returns b for x=2
        [1, 2, 3], None, []:      f returns None for all x in xs.

    """
    for idx, a in enumerate(xs):
        if (b := f(a)) is not None:
            return xs[:idx], b, xs[idx + 1 :]

    return list(xs), None, []


def split_list_at_lambdas(
    xs: list[A], split_lambdas: list[Callable[[A], Optional[B]]]
) -> tuple[list[A], list[tuple[B, list[A]]]]:
    """
    Split the list 'xs' at indices where the lambdas in 'split_lambdas'
    return non-NULL values.

    Args:
        xs:            The input list to be split.
        split_lambdas: A list of lambda functions to determine where to split 'xs'.

    Returns:
        A tuple containing the first part of the split list (from first split), and
        a list of tuples containing the non-NULL values returned by the rest of
        the lambdas in 'split_lambdas' and the corresponding split lists.

    Notes: In 'xs', the entries where lambdas are non-NULL must appear in the same
    order as the lambdas. If a lambda does not return a non-NULL value, the split
    will not occur and the next lambda will be used to determine the split point.
    """
    if len(split_lambdas) == 0:
        return xs, []

    head_lambda, *tail_lambdas = split_lambdas
    xs_head, b, xs_tail = split_at_first_lambda(xs, head_lambda)

    if b is None:
        # head_lambda did not find a match (split point), so skip to the next lambda
        assert xs_head == xs
        assert xs_tail == []
        return split_list_at_lambdas(xs, tail_lambdas)

    xs_tail_head, remaining_splits = split_list_at_lambdas(xs_tail, tail_lambdas)
    return xs_head, [(b, xs_tail_head), *remaining_splits]


def split_list_at_lambda(
    xs: list[A], split_lambda: Callable[[A], Optional[B]]
) -> tuple[list[A], list[tuple[B, list[A]]]]:
    """
    Same as split_list_at_lambdas, but with a single lambda function that can split
    input into multiple parts.
    """
    xs_head, b, xs_tail = split_at_first_lambda(xs, split_lambda)

    if b is None:
        assert len(xs_tail) == 0
        return xs, []

    xs_tail_head, remaining_splits = split_list_at_lambda(xs_tail, split_lambda)
    return xs_head, [(b, xs_tail_head), *remaining_splits]
