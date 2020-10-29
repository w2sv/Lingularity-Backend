from typing import List, Type, Tuple, Sequence
from abc import ABC, abstractmethod

from termcolor import colored

from lingularity.backend.utils.iterables import unzip
from lingularity.frontend.utils import output


class FrontendExtender(ABC):
    _FRONTEND_INSTANCE: object

    @staticmethod
    def set_frontend_instance(instance: object):
        FrontendExtender._FRONTEND_INSTANCE = instance

    def __setattr__(self, key, value):
        if key in self.__class__.__slots__:
            super().__setattr__(key, value)

        else:
            assert hasattr(self._FRONTEND_INSTANCE, key)

            setattr(self._FRONTEND_INSTANCE, key, value)

    def __getattr__(self, item):
        return getattr(self._FRONTEND_INSTANCE, item)


class TrainingOption(FrontendExtender, ABC):
    exit_training: bool

    __slots__ = ('keyword', 'explanation')

    @abstractmethod
    def __call__(self):
        pass


class TrainingOptions(dict):
    _INSTRUCTION_INDENTATION = output.column_percentual_indentation(percentage=0.35)

    def __init__(self, option_classes: Sequence[Type[TrainingOption]], frontend_instance: object):
        TrainingOption.exit_training = False
        TrainingOption.set_frontend_instance(instance=frontend_instance)

        super().__init__({option.keyword: option for option in map(lambda cls: cls(), option_classes)})

        self.keywords: List[str] = [option.keyword for option in self.values()] + ['']
        self.instructions: List[str] = self._compose_instruction()

    def _compose_instruction(self) -> List[str]:
        return output.align(*unzip(map(lambda option: (colored(option.keyword, 'red'), f'to {option.explanation}'), self.values())))

    def display_instructions(self, insertion_args: Tuple[Tuple[int, str, bool]] = ((-1, '', False),)):
        insertion_indices, *_ = unzip(insertion_args)

        print(f'{self._INSTRUCTION_INDENTATION}Enter:')
        for i, instruction_row in enumerate(self.instructions):
            if i in insertion_indices:
                args = insertion_args[insertion_indices.index(i)]

                print(f"\n{[self._INSTRUCTION_INDENTATION, output.centered_print_indentation(args[1])][args[2]]}{args[1]}\n")

            print(f'{self._INSTRUCTION_INDENTATION}  {instruction_row}')

        print('\n')

    @property
    def exit_training(self) -> bool:
        return TrainingOption.exit_training
