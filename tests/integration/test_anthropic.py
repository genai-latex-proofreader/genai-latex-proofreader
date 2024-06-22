from genai_latex_proofreader.genai_interface.anthropic import make_query


def test_connection_to_anthropic_api():
    response = make_query(
        system_prompt="Hello, world!",
        user_prompt="Please say very short a greeting!",
        max_tokens=50,
    )
    assert isinstance(response, str)
    assert len(response) > 0
