import time


class BaseMessage:
    AppendEntry = 0
    RequestVote = 1
    RequestVoteResponse = 2
    AppendEntryResponse = 3

    def __init__(self, sender, receiver, term):
        self.sender = sender
        self.receiver = receiver
        self.term = term


class RequestVoteMsg(BaseMessage):
    def __init__(self, sender, receiver, term, data):
        super().__init__(sender,receiver,term)
        self.data = data
        self.type = BaseMessage.RequestVote


class VoteResponseMsg(BaseMessage):
    def __init__(self, sender, receiver, term,data):
        super().__init__(sender, receiver, term)
        self.data = data
        self.type = BaseMessage.RequestVoteResponse


class AppendEntryMsg(BaseMessage):
    def __init__(self, sender, receiver, term):
        super().__init__(sender, receiver, term)
        self.type = BaseMessage.AppendEntry


class AppendEntryResponseMsg(BaseMessage):
    def __init__(self, sender, receiver, term, success):
        super().__init__(sender,receiver,term)
        self.success = success
        self.type = BaseMessage.AppendEntryResponse



