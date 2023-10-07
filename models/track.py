from dataclasses import dataclass
from hashlib import md5

@dataclass
class Track:
    stream_url: str
    author: str
    thumbnail: str
    title: str
    
    def __repr__(self) -> str:
        return f'{self.title} from author {self.author}'

    @property
    def playable(self):
        if self.stream_url and self.author and self.thumbnail and self.title:
            return True
        return False