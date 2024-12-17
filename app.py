import os
from datetime import datetime, timezone
from typing import Any, Optional

import chainlit as cl


@cl.password_auth_callback
def auth_callback(username: str, password: str):
    # TODO: Fetch the user matching username from your database
    # and compare the hashed password with the value stored in the database
    if (username, password) == (os.getenv("DEFAULT_USERNAME", "admin"), os.getenv("DEFAULT_USER_PASSWORD")):
        return cl.User(
            identifier=username,
            metadata={"role": "user", "last_login": datetime.now(timezone.utc).isoformat(), "provider": "credentials"},
        )
    else:
        return None


@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    cl.logger.info(f"OAuth callback: {provider_id}. User authenticated: {default_user.identifier}")
    cl.user_session.set(f"{provider_id}:token", token)
    cl.user_session.set(f"{provider_id}:user_data", raw_user_data)
    return default_user


@cl.set_chat_profiles
async def load_chat_profiles():
    return [
        cl.ChatProfile(
            name="ChatGPT",
            markdown_description="ChatGPT by OpenAI",
            icon="https://github.com/ndamulelonemakh/remote-assets/blob/7ed514dbd99ab86536daf3942127822bd979936c/images/openai-logomark.png?raw=true",
        ),
        cl.ChatProfile(
            name="Claude",
            markdown_description="Claude by Anthropic",
            icon="https://www.anthropic.com/images/icons/apple-touch-icon.png",
        ),
        cl.ChatProfile(
            name="Gemini",
            markdown_description="Germini Pro by Google",
            icon="https://github.com/ndamulelonemakh/remote-assets/blob/main/images/Google-Bard-Logo-758x473.jpg?raw=true",
        ),
    ]


@cl.on_settings_update
async def update_settings(settings: dict[str, Any]):
    cl.logger.debug(f"user settings updated: {settings}")
    existing_settings: dict = cl.user_session.get("chat_settings", {})
    existing_settings.update(settings)
    if "max_tokens" in existing_settings:
        existing_settings["max_tokens"] = int(existing_settings["max_tokens"])
    if "max_tokens_to_sample" in existing_settings:
        existing_settings["max_tokens_to_sample"] = int(existing_settings["max_tokens_to_sample"])
    cl.user_session.set("chat_settings", existing_settings)


@cl.on_chat_start
async def on_chat_start():
    active_chat_profile = cl.user_session.get("chat_profile") or "ChatGPT"
    if active_chat_profile == "ChatGPT":
        from restchat.providers.chatgpt import chat_settings, call_chatgpt, user_setttings, get_client

        cl.user_session.set("prompt_history", [])
        cl.user_session.set("call_llm", call_chatgpt)
        cl.user_session.set("get_client", get_client)
        cl.user_session.set("chat_settings", chat_settings)
        s = cl.ChatSettings(user_setttings)
        await s.send()

    elif active_chat_profile == "Claude":
        from restchat.providers.claude import chat_settings, call_claude, user_setttings, get_client

        cl.user_session.set("prompt_history", "")
        cl.user_session.set("call_llm", call_claude)
        cl.user_session.set("get_client", get_client)
        cl.user_session.set("chat_settings", chat_settings)
        s = cl.ChatSettings(user_setttings)
        await s.send()

    elif active_chat_profile == "Gemini":
        from restchat.providers.gemini import chat_settings, call_gemini, user_setttings, get_client

        cl.user_session.set("prompt_history", [])
        cl.user_session.set("call_llm", call_gemini)
        cl.user_session.set("get_client", get_client)
        cl.user_session.set("chat_settings", chat_settings)
        s = cl.ChatSettings(user_setttings)
        await s.send()

    else:
        await cl.ErrorMessage(f"Unsupported profile: {active_chat_profile}").send()
        return

    current_user = cl.user_session.get("user")
    await cl.Message(f"{active_chat_profile}: Welcome back, {current_user.identifier}. How can I assit?").send()


@cl.on_message
async def chat(message: cl.Message):
    get_client = cl.user_session.get("get_client")
    client = get_client(cl.user_session.get("env"))

    chat_callback = cl.user_session.get("call_llm")
    chat_settings = cl.user_session.get("chat_settings")
    await chat_callback(client, message.content, chat_settings)
