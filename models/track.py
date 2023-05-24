from dataclasses import dataclass

@dataclass
class Track:
    stream: str
    author: str
    thumbnail: str
    title: str
    
    def __repr__(self) -> str:
        return f'{self.title} from author {self.author}'
    
    @property
    def playable(self):
        if self.stream and self.author and self.thumbnail and self.title:
            return True
        return False