import time

class Tag:

    def __init__(self, name: str, created_at: float = None):
        self.name = name
        self.created_at = created_at or time.time()
