from genai_latex_proofreader.genai_interface.anthropic import make_query


def test_connection_to_anthropic_api():
    max_tokens = 50
    response = make_query(
        system_prompt="Hello, world!",
        user_prompt="Please say a greeting!",
        max_tokens=max_tokens,
    )
    assert isinstance(response, str)
    assert 0 < len(response) < max_tokens
