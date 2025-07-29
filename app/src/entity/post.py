class Post:

    def __init__(self, cid: str, content: str):
        self.content = content
        self.cid = cid

    def get_content(self) -> str:
        return self.content

    def get_cid(self) -> str:
        return self.cid
