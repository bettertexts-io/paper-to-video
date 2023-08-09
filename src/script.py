from typing import NamedTuple, Optional

# class TextScriptScene(NamedTuple):
#     type = "ANIMATION"
#     title: str
#     context: str
#     manimScript: str
#     speakerScript: str


class TextScriptScene(NamedTuple):
    type = "TEXT"
    title: str
    speakerScript: str
    stockFootageQuery: str


class ScriptSection(NamedTuple):
    title: str
    context: str
    scenes: Optional[list[TextScriptScene]]


class Script(NamedTuple):
    sections: list[ScriptSection]


def script_schema(exclude_scenes: bool = False):
    schema = {
        "properties": {
            "sections": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "context": {"type": "string"},
                    },
                    "required": ["title", "context"],
                },
            }
        },
        "required": ["sections"],
    }

    if not exclude_scenes:
        schema["properties"]["sections"]["items"]["properties"][
            "scenes"
        ] = script_scene_schema

    return schema


script_scene_schema = {
    "properties": {
        "scenes": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string", "const": "TEXT"},
                    "title": {"type": "string"},  # Changed "shortTitle" to "title"
                    "speakerScript": {"type": "string"},
                    "stockFootageQuery": {"type": "string"},
                },
                "required": ["type", "title", "speakerScript", "stockFootageQuery"],
            },
        }
    }
}
