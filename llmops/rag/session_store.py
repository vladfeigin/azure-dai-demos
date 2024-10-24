import uuid
from abc import ABC, abstractmethod

class SessionSroreAbstract(ABC):
    def __init__(self):
        self._sessions = {}

    def get_session(self, session_id):
        return self._sessions[session_id]

    @abstractmethod 
    def create_session(self, session_id:str)->object:
        pass

    def remove_session(self, session_id):
        del self._sessions[session_id]

    def get_all_sessions_id(self):
        return self._sessions.keys()
     
    def get_all_sessions(self):
        return self._sessions.values()

    def clear(self):
        self._sessions.clear()

    def __len__(self):
        return len(self._sessions)

    def __iter__(self):
        return iter(self._sessions.values())

    def __contains__(self, session_id):
        return session_id in self._sessions

    def __getitem__(self, session_id):
        return self._sessions[session_id]

    def __setitem__(self, session_id, session):
        self._sessions[session_id] = session

    def __delitem__(self, session_id):
        del self._sessions[session_id]

    def __repr__(self):
        return f"{self.__class__.__name__}({self._sessions})"

    def __str__(self):
        return f"{self.__class__.__name__}({self._sessions})"
    
    
from langchain_community.chat_message_histories import ChatMessageHistory

class SimpleSessionStore(SessionSroreAbstract):
    
    def create_session(self, session_id)-> object:
        #check if session_id is provided otherwise raise an exception
        if not session_id:
            raise ValueError("session_id is required")
        
        session = ChatMessageHistory()
        self._sessions[session_id] = session
        return session
        