import time

class Trend:

    def __init__(self, name: str, category: str, created_at: float = None):
        self.name = name
        self.category = category
        self.created_at = created_at or time.time()
