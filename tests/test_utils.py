import pytest

from genai_latex_proofreader.utils import compose


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
