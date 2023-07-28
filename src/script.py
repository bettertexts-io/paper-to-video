from typing import NamedTuple, Optional

class TextScriptScene(NamedTuple):
    type = "TEXT"
    title: str
    context: str
    script: str
    data: str

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
                  "required": ["title", "context"]
              }
          }
      },
      "required": ["sections"]
    }

    if(not exclude_scenes):
        schema["properties"]["sections"]["items"]["properties"]["scenes"] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "data": {},
                    "script": {"type": "string"},
                },
                "required": ["type", "data"]
            }
        }

    return schema
