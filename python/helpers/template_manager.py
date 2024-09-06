import json
import os
import uuid

class Template:
    def __init__(self, id, name, url, navigation_goal, data_extraction_goal, advanced_settings=None):
        self.id = id
        self.name = name
        self.url = url
        self.navigation_goal = navigation_goal
        self.data_extraction_goal = data_extraction_goal
        self.advanced_settings = advanced_settings or {}

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "navigation_goal": self.navigation_goal,
            "data_extraction_goal": self.data_extraction_goal,
            "advanced_settings": self.advanced_settings
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data["name"],
            url=data["url"],
            navigation_goal=data["navigation_goal"],
            data_extraction_goal=data["data_extraction_goal"],
            advanced_settings=data.get("advanced_settings", {})
        )

def get_templates_file_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates.json')

def load_templates():
    template_file = get_templates_file_path()
    if not os.path.exists(template_file):
        return []
    
    try:
        with open(template_file, 'r') as f:
            data = json.load(f)
            return [Template.from_dict(item) for item in data]
    except json.JSONDecodeError:
        print(f"Error decoding {template_file}. Starting with empty templates.")
        return []
    except Exception as e:
        print(f"Unexpected error loading templates: {str(e)}")
        return []

def save_templates(templates):
    template_file = get_templates_file_path()
    with open(template_file, 'w') as f:
        json.dump([template.to_dict() for template in templates], f, indent=2)