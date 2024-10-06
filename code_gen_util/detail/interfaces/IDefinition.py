from abc import ABC, abstractmethod

class IDefinition(ABC):
    @abstractmethod
    def generateDefinition(self):
        pass