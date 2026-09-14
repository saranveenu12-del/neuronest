# To run this code you need to install the following dependencies:
# pip install google-generativeai

import os

try:
    from google.generativeai import client as genai_client  # type: ignore[import]
    from google.generativeai import types  # type: ignore[import]
except ImportError as exc:
    raise ImportError(
        "The google-generativeai package is required. Install it with "
        "'pip install google-generativeai'"
    ) from exc


def generate():
    client = genai_client.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-3-flash-preview"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text="""INSERT_INPUT_HERE"""),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
        ),
        tools=tools,
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            print(text, end="")

if __name__ == "__main__":
    generate()


