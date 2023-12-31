from typing import Any, Callable, List, NamedTuple, Optional

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
    memeSearchTerm: str


class ScriptSection(NamedTuple):
    title: str
    context: str
    scenes: Optional[list[TextScriptScene]]


class Script(NamedTuple):
    sections: list[ScriptSection]


def for_every_scene(
    script: Script, func: Callable[[[int, int], TextScriptScene], None]
) -> List[Any]:
    ret = []
    for i, section in enumerate(script["sections"]):
        if section["scenes"]:  # Ensure there are scenes to process
            for j, scene in enumerate(section["scenes"]):
                ret.append(func([i, j], scene))

    return ret


def generate_script_schema(exclude_scenes: bool = False):
    schema = {
        "type": "object",
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
    "type": "object",
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
                    "memeSearchTerm": {"type": "string"},
                },
                "required": ["type", "title", "speakerScript", "stockFootageQuery"],
            },
        }
    },
}

script_schema = {
    "type": "object",
    "properties": {
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "context": {"type": "string"},
                    "scenes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string", "const": "TEXT"},
                                "title": {
                                    "type": "string"
                                },  # Changed "shortTitle" to "title"
                                "speakerScript": {"type": "string"},
                                "stockFootageQuery": {"type": "string"},
                                "memeSearchTerm": {"type": "string"},
                            },
                            "required": [
                                "type",
                                "title",
                                "speakerScript",
                                "stockFootageQuery",
                            ],
                        },
                    }
                },
                "required": ["title", "context", "scenes"],
            },
        }
    },
}
