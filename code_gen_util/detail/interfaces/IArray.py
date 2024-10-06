from abc import ABC, abstractmethod

class IArray(ABC):
    @abstractmethod
    def generateAllocationBlock(self):
        pass

    @abstractmethod
    def generateInitializerFunction(self):
        pass

    @abstractmethod
    def generateCallToInitializer(self):
        pass

    @abstractmethod
    def generateDeleteCall(self):
        pass