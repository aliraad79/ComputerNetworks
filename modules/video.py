from enum import Enum
from typing import List
from dataclasses import dataclass

from modules.users import User


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
        if Label(label_id) not in self.labels:
            self.labels.append(Label(label_id))

    def ban(self):
        self.is_ban = True
        banned_video = 1
        for video in videos:
            if video.name != self.name and video.owner == self.owner and video.is_ban:
                banned_video += 1
        if banned_video >= 2:
            self.owner.is_striked = True

    @classmethod
    def get_video(cls, video_name):
        for video in videos:
            if video.name == video_name:
                return video
        return None

    @classmethod
    def get_all(cls):
        return f"Videos:\n" + f"\n".join([str(i) for i in videos])

    @classmethod
    def get_all_unband_videos(cls):
        return f"Videos:\n" + f"\n".join([str(i) for i in videos if not i.is_ban])

    def __str__(self) -> str:
        return (
            f"{self.name} Likes:{self.likes} DisLikes:{self.dislikes} Comments: \n\t"
            + "\n\t".join([str(i) for i in self.comments])
            + "\nLabels: \n\t"
            + "\n\t".join([i.name for i in self.labels])
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
