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
        print(text)
        self.chats.append(text)

    def change_state(self, state: TicketState):
        self.state = state

    @classmethod
    def get_ticket(cls, ticket_id):
        for i in tickets:
            if i.id == ticket_id:
                return i
        return None

    @classmethod
    def get_user_tickets(cls, user_id):
        return [str(i) for i in tickets if i.opener.id == user_id]

    def __str__(self) -> str:
        print(self.chats)
        return f"{self.opener.username}\t|{self.id}|\t{self.state.name}:\n" + "".join(
            [str(i) for i in self.chats]
        )


class Text(Comment):
    ...


tickets: List[Ticket] = []


def create_ticket(user) -> Ticket:
    new_ticket = Ticket(user)
    tickets.append(new_ticket)
    return new_ticket
