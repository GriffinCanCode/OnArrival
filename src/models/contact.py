class Contact:
    def __init__(self, name: str, phone: str):
        self.name = name
        self.phone = phone

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "phone": self.phone
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Contact':
        return cls(data["name"], data["phone"])