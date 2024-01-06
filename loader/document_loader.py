import abc


class DocumentLoader(abc.ABC):
    @abc.abstractmethod
    def load(self):
        pass
