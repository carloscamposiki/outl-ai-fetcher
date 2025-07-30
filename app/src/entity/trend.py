import time

class Trend:

    def __init__(self, name: str, category: str, created_at: float = None):
        self.name = name
        self.category = category
        self.created_at = created_at or time.time()

    def __eq__(self, other):
        if isinstance(other, Trend):
            return (self.name == other.name and
                    self.category == other.category and
                    self.created_at == other.created_at)
        return False

    def __hash__(self):
        return hash((self.name, self.category, self.created_at))

    def __repr__(self):
        return f"Trend(name={self.name}, category={self.category}, created_at={self.created_at})"