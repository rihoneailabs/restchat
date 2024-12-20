
from typing import Any

import chainlit as cl
import google.generativeai as genai
from chainlit.input_widget import Select, Slider, NumberInput


chat_settings = settings = {
        "max_output_tokens": 4096,
        "model": "gemini-2.0-flash-exp",
}
user_setttings = [
    Select(
        id="model",
        label="Model",
        # https://ai.google.dev/gemini-api/docs/models/gemini#model-variations
        values=["gemini-2.0-flash-exp", "gemini-1.5-pro"],
        initial_index=0,
    ),
    Slider(
                id="temperature",
                label="Temperature",
                initial=0.2,
                min=0,
                max=1,
                step=0.1,
                description="The temperature of the model. Higher values mean the model will generate more creative answers.",
            ),
    Slider(
                id="max_output_tokens",
                label="Maxiumum Completions Tokens",
                initial=4096,
                min=100,
                max=32000,
                step=10,
                description="The maximum allowable tokens in the response",
    ),
    NumberInput(
        id="candidate_count",
        label="Numbr of Answers",
        initial=1,
        placeholder="Enter a number between 1 and 3"
    ),
    Select(
        id="response_mime_type",
        label="Response Type",
        values=["text/plain", "application/json"],
        initial_index=0,
    )   
]


def get_client(user_secrets: dict[str, str]):
    genai.configure(api_key=user_secrets["GOOGLE_API_KEY"])
    return genai


async def call_gemini(query: str, 
                      settings: dict[str, Any] = chat_settings):
    
    prompt_history = cl.user_session.get("prompt_history") or []
    if "max_output_tokens" in settings:
        settings["max_output_tokens"] = int(settings["max_output_tokens"])
    if "candidate_count" in settings:
        settings["candidate_count"] = int(settings["candidate_count"])
        
    model = genai.GenerativeModel(settings.pop("model", "gemini-1.0-pro-latest"), 
                                  generation_config=genai.GenerationConfig(
                                  **settings
                                  ),
                                  tools=None,
                                  tool_config=None
                                  )
    chat = model.start_chat(history=prompt_history)
    async for chunk in await chat.send_message_async(query, 
                                                     stream=True):
        await cl.context.current_step.stream_token(chunk.text)

    cl.context.current_step.generation = cl.CompletionGeneration(
        formatted=query,
        completion=cl.context.current_step.output,
        settings=settings,
    )

    updated_history = prompt_history + chat.history
    # TODO: need to limit these to prevent exceeding model context
    cl.user_session.set("prompt_history", updated_history)

