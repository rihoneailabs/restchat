from typing import Any


import chainlit as cl
from chainlit.input_widget import Select, Slider
from openai import AsyncOpenAI


chat_settings = {"model": "gpt-4o-mini", "max_tokens": 4096, "temperature": 0.2}
user_setttings = [
    Select(
        id="model",
        label="Model",
        values=["gpt-4o-mini", "gpt-4o", "o1-preview", "o1-mini"],
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
        id="max_tokens",
        label="Maxiumum Completions Tokens",
        initial=4096,
        min=100,
        max=32000,
        step=8,
        description="The maximum allowable tokens in the response",
    ),
]


def get_client(user_secrets: dict[str, str]):
    return AsyncOpenAI(api_key=user_secrets["OPENAI_API_KEY"])


async def call_chatgpt(client: AsyncOpenAI, query: str, settings: dict[str, Any] = chat_settings):
    message_history = cl.user_session.get("prompt_history")
    message_history.append({"name": "User", "role": "user", "content": query})

    if "max_tokens" in settings:
        settings["max_tokens"] = int(settings["max_tokens"])

    stream = await client.chat.completions.create(messages=message_history, stream=True, **settings)

    reply = cl.Message(content="")
    async for part in stream:
        if token := part.choices[0].delta.content or "":
            await reply.stream_token(token)

    message_history.append({"name": "ChatGPT", "role": "assistant", "content": reply.content})
    await reply.update()
