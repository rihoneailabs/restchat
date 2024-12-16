from typing import Any

import anthropic
from anthropic import AsyncAnthropic
import chainlit as cl
from chainlit.input_widget import Select, Slider

chat_settings = settings = {
    "stop_sequences": [anthropic.HUMAN_PROMPT],
    "max_tokens_to_sample": 4096,
    "model": "claude-3-haiku-20240307",
}
user_setttings = [
    Select(
        id="model",
        label="Model",
        # https://docs.anthropic.com/claude/docs/models-overview#claude-3-a-new-generation-of-ai
        values=["claude-3-haiku-20240307", "claude-3-5-sonnet-latest", "claude-3-opus-latest"],
        initial_index=0,
    ),
    Slider(
        id="temperature",
        label="Temperature",
        initial=0.2,
        min=0,
        max=1,
        step=0.1,
    ),
    Slider(
        id="max_tokens_to_sample",
        label="Maxiumum Completions Tokens",
        initial=4096,
        min=100,
        max=32000,
        step=10,
        description="The maximum allowable tokens in the response",
    ),
]


def get_client(user_secrets: dict[str, str]):
    return AsyncAnthropic(api_key=user_secrets["ANTHROPIC_API_KEY"])


async def call_claude(client: AsyncAnthropic, query: str, settings: dict[str, Any] = None):
    message_history = cl.user_session.get("prompt_history")
    prompt = f"{message_history}{anthropic.HUMAN_PROMPT}{query}{anthropic.AI_PROMPT}"

    settings = settings or chat_settings
    if "max_tokens_to_sample" in settings:
        settings["max_tokens_to_sample"] = int(settings["max_tokens_to_sample"])
    stream = await client.completions.create(
        prompt=prompt,
        stream=True,
        **settings,
    )

    reply = cl.Message(content="")
    async for data in stream:
        token = data.completion
        if token:
            await reply.stream_token(token)

    message_history.append({"name": "ChatGPT", "role": "assistant", "content": reply.content})
    await reply.update()
