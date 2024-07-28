import datetime
import json
from pathlib import Path

import anthropic
import httpx


def make_query(system_prompt: str, user_prompt: str, max_tokens: int) -> str:
    """
    Make LLM query to Anthropic Opus API

    https://github.com/anthropics/anthropic-sdk-python
    https://support.anthropic.com/en/articles/8324991-about-claude-pro-usage
    """
    client = anthropic.Anthropic(
        timeout=httpx.Timeout(pool=10.0, read=200.0, write=10.0, connect=10.0),
        max_retries=10,
    )

    def _get_api_response():
        # Note: we are using the streaming API. This seemed more stable with
        # large input text, while the non-streaming API often failed (no
        # connection to server??, 4/2024)
        with client.messages.with_streaming_response.create(
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            model="claude-3-5-sonnet-20240620",
            # model="claude-3-opus-20240229",
            # model="claude-3-haiku-20240307",  # fast testing
        ) as response:
            for line_message in response.iter_lines():
                line = json.loads(line_message)
                print("usage:", line["usage"])  # token usage
                for content_part in line["content"]:
                    assert content_part["type"] == "text"
                    yield content_part["text"]

    return "\n".join(_get_api_response())


class GenAIClient:
    def __init__(self, log_output_path: Path, max_tokens: int):
        self.calls: int = 0
        self.max_tokens: int = max_tokens
        self.log_output_path: Path = log_output_path
        log_output_path.mkdir(parents=True, exist_ok=True)

    def make_query(self, system_prompt: str, user_prompt: str, label: str) -> str:
        response = make_query(system_prompt, user_prompt, self.max_tokens)

        # make filename more friendly for filesystems
        for char in [" ", ":", "'", '"', "$", "{", "}", "\\", "/", "^"]:
            label = label.replace(char, "_")

        while "__" in label:
            label = label.replace("__", "_", 1)

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename: str = f"{timestamp}-{label}.txt"

        print("Writing log to ", self.log_output_path / filename)
        (self.log_output_path / filename).write_text(
            f"""Call # {self.calls}
{80 * '='}
SYSTEM PROMPT:
{80 * '-'}
{system_prompt}
{80 * '-'}

USER PROMPT:
{80 * '-'}
{user_prompt}
{80 * '-'}

RESPONSE:
{80 * '-'}
{response}
{80 * '='}
"""
        )
        self.calls += 1

        assert isinstance(response, str)
        return response
