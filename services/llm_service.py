import os
from typing import List, Dict, Literal
from dotenv import load_dotenv
import streamlit as st

load_dotenv()

supported_models = Literal[
    "gpt-4o", "gpt-4-o1-preview", "gpt-4", "anthropic", "llama3 (not supported yet)"]


def get_openai_api_key():
    # if on streamlit cloud
    # if 'STREAMLIT_SHARING_MODE' in os.environ:
    return st.secrets["openapi_key"]
    # if on local or app runner
    # else:
    # return os.environ.get("OPENAI_API_KEY")


def generate(messages: List[Dict[str, str]], model_type: supported_models = "gpt-4"):
    if model_type in ["gpt-4-preview", "gpt-4-2024"]:
        return _generate_azure_openai(messages, model_type)
    elif model_type in ["gpt-4", "gpt-4-o1-preview", "gpt-4o"]:
        return _generate_openai(messages, model_type)
    elif model_type == "anthropic":
        return _generate_anthropic(messages)
    elif model_type == "llama3":
        return _generate_llama3(messages)
    else:
        raise ValueError(f"Invalid model type: {model_type}")


def _generate_azure_openai(messages: List[Dict[str, str]], model_type: str) -> str:
    from openai import AzureOpenAI

    api_versions = {
        "gpt-4": "2023-05-15",
        "gpt-4-preview": "2023-07-01-preview",
        "gpt-4-2024": "2024-02-01"
    }

    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_BASE_URL"),
        api_version=api_versions[model_type],
    )

    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "GPT4_32K"),
        messages=messages,
        frequency_penalty=1.1
    )
    return response.choices[0].message.content


def _generate_openai(messages: List[Dict[str, str]], model_type: str) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=get_openai_api_key())

    model = "o1-preview" if model_type == "gpt-4-o1-preview" else "gpt-4o-2024-05-13"

    response = client.chat.completions.create(
        model=model,
        messages=messages if model_type == "gpt-4o" else [
            {"role": "user", "content": " ".join([m["content"] for m in messages])}]
    )
    return response.choices[0].message.content


def _generate_anthropic(messages: List[Dict[str, str]]) -> str:
    from anthropic import AnthropicBedrock
    print("Generating wiht anthropic")
    print(os.getenv("AWS_ACCESS_KEY"))

    client = AnthropicBedrock(
        aws_access_key=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_key=os.getenv("AWS_SECRET_KEY"),
        aws_region=os.getenv("AWS_REGION", "us-east-1"),
    )

    response = client.messages.create(
        model=os.getenv("ANTHROPIC_MODEL", "anthropic.claude-3-5-sonnet-20240620-v1:0"),
        max_tokens=256,
        system=messages[0]["content"],
        messages=messages[1:]
    )
    return response.content[0].text


def _generate_llama3(messages: List[Dict[str, str]]) -> str:
    raise NotImplementedError("Llama3 generation is not currently supported.")
