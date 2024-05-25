from typing import Callable, Sequence, TypeVar

A = TypeVar("A")
B = TypeVar("B")


def compose(*fs: Sequence[Callable[[A], A]]) -> Callable[[A], A]:
    """
    Compose multiple functions (of type A -> A) into into a single function A -> A.

    Example: compose(f, g, h)(a) = f(g(h(a)))

    Args:
        *fs: A variable number of functions to be composed.

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
