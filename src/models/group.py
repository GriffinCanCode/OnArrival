class Group:
    def __init__(self, name: str, contacts: list = None):
        self.name = name
        self.contacts = contacts or []

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "contacts": [contact.to_dict() for contact in self.contacts]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Group':
        group = cls(data["name"])
        from models.contact import Contact
        group.contacts = [Contact.from_dict(contact) for contact in data["contacts"]]
        return group