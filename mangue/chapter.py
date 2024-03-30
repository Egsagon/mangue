class Chapter:
    number: float | None
    title: str | None

    def __init__(self, title: str | None, chapter: float | None):
        self.title = title
        self.number = chapter

    @staticmethod
    def make():
        return Chapter(None, None)
