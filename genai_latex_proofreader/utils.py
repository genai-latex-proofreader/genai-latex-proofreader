from typing import Callable, Optional, Sequence, TypeVar

A = TypeVar("A")
B = TypeVar("B")


def split_at_first_lambda(
    xs: Sequence[A], f: Callable[[A], Optional[B]]
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
    order as the lambdas. If this is not the case, the function raises an Exception.
    """
    if len(split_lambdas) == 0:
        return xs, []

    head_lambda, *tail_lambdas = split_lambdas
    xs_head, b, xs_tail = split_at_first_lambda(xs, head_lambda)

    if b is None:
        assert xs_tail == []
        raise Exception(f"split_list_at_lambdas: head_lambda did not return a value")

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


def compose(*fs: Sequence[Callable[[A], A]]) -> Callable[[A], A]:
    """
    Compose multiple functions (of type A -> A) into into a single function A -> A.

    Example: compose(f, g, h)(a) = f(g(h(a)))

    Args:
        *fs: A variable number (n >= 1) of functions to be composed.

    Returns:
        A new function that represents the composition of the input functions.
    """

    if len(fs) == 0:
        raise ValueError("compose called with zero functions")

    def composed_f(a: A) -> A:
        for f in reversed(fs):
            a = f(a)

        return a

    return composed_f
