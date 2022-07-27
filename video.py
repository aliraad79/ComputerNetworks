from dataclasses import dataclass
from typing import List
from enum import Enum

from users import User


class Label(Enum):
    Under_13 = 1
    Under_18 = 2
    R_rated = 3
    Violance = 4
    May_find_argumantive = 5


class Video:
    def __init__(self, name, owner) -> None:
        self.name = name
        self.owner = owner

        self.likes = 0
        self.dislikes = 0
        self.comments = []
        self.is_ban = False

        self.labels: List[Label] = []

    def add_comment(self, user, comment):
        self.comments.append(Comment(user, comment))

    def add_label(self, label_id: int):
        self.labels.append(Label(label_id))

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
