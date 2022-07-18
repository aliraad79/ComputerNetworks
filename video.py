ids = 0

class Video:
    def __init__(self, file, owner=None) -> None:
        self.id = ids
        ids += 1
        self.file = file
        self.likes = 0
        self.owner = owner
        self.dislikes = 0
        self.comments = []
        self.is_ban = False

    def add_comment(self, comment):
        self.comments.append(comment)
