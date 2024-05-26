from typing import Callable

import pytest

from genai_latex_proofreader.utils import (
    compose,
    split_at_first_lambda,
    split_list_at_lambda,
    split_list_at_lambdas,
)


def test_compose():

    def f(x: int) -> int:
        return x + 1

    def g(x: int) -> int:
        return x * 2

    def h(x: int) -> int:
        return 1

    assert compose(f)(1) == f(1)
    assert compose(f, g)(1) == f(g(1))
    assert compose(f, g, h)(1) == f(g(h(1)))
    assert compose(f, h, g)(1) == f(h(g(1)))
    assert compose(h, g, f)(1) == h(g(f(1)))
    assert compose(g, h, f)(1) == g(h(f(1)))


def test_compose_fails_with_zero_input_functions():

    with pytest.raises(ValueError):
        compose()


# --- test test_split_at_first_lambda ---


def test_split_at_first_lambda():
    def split_after(x0: int):
        def split(x):
            if x >= x0:
                return x
            return None

        return split

    xs = [1, 2, 3, 4, 3, 2, 1, 100]
    assert split_at_first_lambda(xs, split_after(0)) == ([], 1, [2, 3, 4, 3, 2, 1, 100])
    assert split_at_first_lambda(xs, split_after(1)) == ([], 1, [2, 3, 4, 3, 2, 1, 100])
    assert split_at_first_lambda(xs, split_after(2)) == ([1], 2, [3, 4, 3, 2, 1, 100])
    assert split_at_first_lambda(xs, split_after(3)) == ([1, 2], 3, [4, 3, 2, 1, 100])
    assert split_at_first_lambda(xs, split_after(4)) == ([1, 2, 3], 4, [3, 2, 1, 100])
    assert split_at_first_lambda(xs, split_after(100)) == (
        [1, 2, 3, 4, 3, 2, 1],
        100,
        [],
    )

    # lambda never returns a non-NULL value -> no split
    assert split_at_first_lambda(xs, split_after(404)) == (xs, None, [])


# --- test split_list_at_lambdas ---


def test_split_list_at_lambdas_with_one_entry():
    # check that when there is one lambda (and split is found), then functions
    #  - split_at_first_lambda
    #  - split_list_at_lambdas
    # return the same result.
    xs = [1, 2, 3, 4, 5]

    for x in range(1, 6):
        split_lambda = lambda _x: "split{_x}" if _x == x else None
        x_pre1, [(lambda_value1, x_post1)] = split_list_at_lambdas(xs, [split_lambda])
        x_pre2, lambda_value2, y_post2 = split_at_first_lambda(xs, split_lambda)
        assert x_pre1 == x_pre2
        assert lambda_value1 == lambda_value2
        assert x_post1 == y_post2


def test_split_list_at_lambdas_multiple_splits():
    xs = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    split_lambdas = [
        lambda x: "split1" if x == 3 else None,
        lambda x: "split2" if x == 6 else None,
        lambda x: "split3" if x == 8 else None,
        lambda x: "split4" if x == 10 else None,
    ]
    assert split_list_at_lambdas(xs, split_lambdas) == (
        [1, 2],
        [
            ("split1", [4, 5]),
            ("split2", [7]),
            ("split3", [9]),
            ("split4", [11]),
        ],
    )


def test_split_list_at_lambdas():
    xs = [1, 2, 3]

    # no split found in non-empty list => exception
    with pytest.raises(Exception):
        split_list_at_lambdas(xs, [lambda _: None])

    # no lambdas in non-empty list => ok, no split
    assert split_list_at_lambdas(xs, split_lambdas=[]) == (xs, [])

    # no lambdas, empty list => ok, no split
    assert split_list_at_lambdas([], split_lambdas=[]) == ([], [])


# --- test split_list_at_lambda ---


def test_split_list_at_lambda():
    f = lambda x: "200" if x == 2 else None

    # no match
    assert split_list_at_lambda([1, 3, 4], f) == ([1, 3, 4], [])

    # multiple matches
    assert split_list_at_lambda([1, 2, 3, 3, 2, 1, 2], f) == (
        [1],
        [("200", [3, 3]), ("200", [1]), ("200", [])],
    )

    # match first element
    assert split_list_at_lambda([2, 1, 3], f) == ([], [("200", [1, 3])])

    # match middle element
    assert split_list_at_lambda([1, 2, 3], f) == ([1], [("200", [3])])

    # match last element
    assert split_list_at_lambda([1, 3, 2], f) == ([1, 3], [("200", [])])
