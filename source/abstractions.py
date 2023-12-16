from abc import ABC, abstractmethod


class SupportsEventLoop(ABC):

    @abstractmethod
    def eventloop(self, *events):
        raise NotImplemented(f'class inherited from "{self.__class__.__name__}" must implement method "eventloop"')


class SupportsDraw(ABC):

    @abstractmethod
    def draw(self):
        raise NotImplemented(f'class inherited from "{self.__class__.__name__}" must implement method "draw"')
