class Video:
    def __init__(self, file) -> None:
        self.
        self.file = file
        self.likes = 0
        self.dislikes = 0
        self.comments = []
        self.is_ban = False

    def add_comment(self, comment):
        self.comments.append(comment)
