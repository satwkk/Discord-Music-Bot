from discord import PollAnswer
from typing import List

class Answer:
    def __init__(self, answer: PollAnswer=None, count: int = 0):
        self.answer = answer
        self.count = count

    def __eq__(self, other):
        return self.count == other.count

    def __gt__(self, other):
        return self.count > other.count
    
    def __lt__(self, other):
        return self.count < other.count
    
class Vote:
    def __init__(self, answers: List[Answer], default_answer: Answer) -> None:
        self.answers = answers
        self.default_answer = default_answer
        self.__best_answer = Answer()

    def decide(self) -> Answer:
        for ans in self.answers:
            # First check if any other answer has same no of vote as the best 
            if self.__best_answer.count == ans.count:
                # if yes then set the answer to default answer and break
                self.__best_answer = self.default_answer
                break
            
            # else keep checking if their is a better answer
            if (ans.count > self.__best_answer.count):
                self.__best_answer = ans
        return self.__best_answer
            
