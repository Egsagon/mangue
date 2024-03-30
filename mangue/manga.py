from .chapter import Chapter


class Manga:
    name: str | None
    chapters: list[Chapter]

    @staticmethod
    def make():
        return Manga(None, [])

    def __init__(self, name: str | None, chapters: list[Chapter]):
        self.name = name
        self.chapters = chapters

    def chapters_length(self) -> int:
        return len(self.chapters)

    def first_chapter(self) -> Chapter | None:
        return self.chapters[0] if len(self.chapters) > 0 else None

    def last_chapter(self) -> Chapter | None:
        return self.chapters[self.chapters_length() - 1] if len(self.chapters) > 0 else None
