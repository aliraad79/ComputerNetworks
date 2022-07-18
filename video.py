from dataclasses import dataclass
from typing import List

from users import User


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

    def add_comment(self, user, comment):
        self.comments.append(Comment(user, comment))

    @classmethod
    def get_video(cls, video_id):
        for video in videos:
            if video.id == video_id:
                return video
        return None

    @classmethod
    def get_all(cls):
        return [str(i) for i in videos]

    def __str__(self) -> str:
        return f"Video {self.id} {self.likes}|{self.dislikes} Comments: " + "/".join(
            self.comments
        )


@dataclass
class Comment:
    owner: User
    text: str


ids = 0
videos: List[Video] = []
