from enum import Enum
from typing import List
from users import User
from video import Comment
import itertools


class TicketState(Enum):
    NEW = 1
    PENDING = 2
    SOLVED = 3
    CLOSED = 4


class Ticket:
    id_iter = itertools.count()

    def __init__(self, user) -> None:
        self.id = next(Ticket.id_iter)

        self.opener: User = user
        self.state: TicketState = TicketState.NEW
        self.chats: List[Text] = []

    def add_chat(self, text: Comment):
        self.chats.append(text)

    def change_state(self, state: int):
        self.state = TicketState(state)

    @classmethod
    def get_ticket(cls, ticket_id):
        for ticket in tickets:
            if ticket.id == ticket_id:
                return ticket
        return None

    @classmethod
    def get_user_tickets(cls, user: User):
        return [
            str(i) for i in tickets if i.opener.id == user.id or user.type in [2, 3]
        ]

    def __str__(self) -> str:
        return (
            f"username: {self.opener.username} | ticket id:{self.id} | State: {self.state.name}\n\t"
            + "\n\t".join([str(i) for i in self.chats])
        )


class Text(Comment):
    def __str__(self) -> str:
        return super().__str__()


tickets: List[Ticket] = []


def create_ticket(user) -> Ticket:
    new_ticket = Ticket(user)
    tickets.append(new_ticket)
    return new_ticket
