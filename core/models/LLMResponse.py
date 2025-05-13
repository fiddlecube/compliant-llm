class Message:
    def __init__(self, content: str, role: str):
        self.content = content
        self.role = role

    def to_dict(self):
        return {
            "content": self.content,
            "role": self.role
        }

class Choices:
    def __init__(self, finish_reason: str, index: int, message: Message):
        self.finish_reason = finish_reason
        self.index = index
        self.message = message

    def to_dict(self):
        return {
            "finish_reason": self.finish_reason,
            "index": self.index,
            "message": self.message.to_dict()  # Convert message to dict
        }

class LLMResponse:
    def __init__(self, id: str, created: int, model: str, object: str, choices: list):
        self.id = id
        self.created = created
        self.model = model
        self.object = object
        self.choices = choices

    def to_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "model": self.model,
            "object": self.object,
            "choices": [choice.to_dict() for choice in self.choices]  # Convert choices to dicts
        }