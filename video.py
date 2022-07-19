from dataclasses import dataclass
from typing import List

from users import User


class Video:
    def __init__(self, name, owner) -> None:
        self.name = name
        self.owner = owner

        self.likes = 0
        self.dislikes = 0
        self.comments = []
        self.is_ban = False

    def add_comment(self, user, comment):
        self.comments.append(Comment(user, comment))

    @classmethod
    def get_video(cls, video_name):
        for video in videos:
            if video.name == video_name:
                return video
        return None

    @classmethod
    def get_all(cls):
        return f"Videos:\n" + f"\n".join([str(i) for i in videos])

    def __str__(self) -> str:
        return f"{self.name} {self.likes}|{self.dislikes} Comments: " + "\n".join(
            [str(i) for i in self.comments]
        )


@dataclass
class Comment:
    owner: User
    text: str

    def __str__(self) -> str:
        return f"{self.owner.username}: {self.text}"


videos: List[Video] = []


def add_video(video: Video) -> None:
    videos.append(video)
