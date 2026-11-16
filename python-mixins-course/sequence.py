from abc import ABC, abstractmethod


class Sequence(ABC):
    """Abstract sequence interface; subclasses must implement both methods.

    Instantiating this class directly raises TypeError because its methods
    are abstract.
    """
    @abstractmethod
    def __getitem__(self, index):
        pass

    @abstractmethod
    def __len__(self):
        pass
