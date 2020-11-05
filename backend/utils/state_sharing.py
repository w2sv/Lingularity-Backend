from typing import Any, Dict
from abc import ABC


class MonoStatePossessor(ABC):
    """ Interface for classes predestined to possess one singular global state, implemented
        by means of the Borg-pattern """

    _mono_state: Dict[str, Any] = {}

    def __init__(self):
        """ Equate instance state and global state """

        self.__dict__ = self._mono_state

    @classmethod
    def get_instance(cls):
        # get empty instance of subclass
        instance = cls.__new__(cls)

        # get reference to global state
        super(cls, instance).__init__()

        return instance
