class Location:
    def __init__(self, name: str, coords: tuple, radius: float, message: str):
        self.name = name
        self.coords = coords
        self.radius = radius
        self.message = message
        self.status = False  # Track if we're currently in this location

    @classmethod
    def create_default_locations(cls) -> dict:
        return {
            "California": cls(
                "California",
                (36.7783, -119.4179),
                50,
                "Don't hang up, this is a Griffin certified automated service message ... he has just landed in California. Would you mind getting everything ready? He'll be there soon. And uh... make sure to dispose of this phone right after - it's gonna self-destruct."
            ),
            "DC": cls(
                "DC",
                (38.9072, -77.0369),
                20,
                "Don't hang up, this is a Griffin certified automated service message ... he has just landed in California. Would you mind getting everything ready? He'll be there soon. And uh... make sure to dispose of this phone right after - it's gonna self-destruct."
            )
        } 