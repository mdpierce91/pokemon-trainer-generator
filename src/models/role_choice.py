class RoleChoice():
    role: str | None
    level: int | None

    def __init__(self, role: str| None = None, level: int | None = None):
        self.role = role
        self.level = level
        pass