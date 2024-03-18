from dataclasses import dataclass
from hashlib import md5
import pickle
from db import handle

@dataclass
class Track:
    stream_url: str = None
    author: str = None
    thumbnail: str = None
    title: str = None
    
    def __init__(self, author, title, stream_url=None, thumbnail=None):
        self.author = author
        self.title = title
        self.stream_url = stream_url
        self.thumbnail = thumbnail
    
    def __repr__(self) -> str:
        return f'{self.title} from author {self.author}'

    @property
    def playable(self):
        if self.stream_url and self.author and self.thumbnail and self.title:
            return True
        return False
        