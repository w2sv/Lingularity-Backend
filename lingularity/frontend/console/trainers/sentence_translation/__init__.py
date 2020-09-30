import time
from typing import Optional, Tuple
from itertools import groupby
import os
import cursor

from lingularity.backend.trainers.sentence_translation import SentenceTranslationTrainerBackend as Backend
from lingularity.backend.trainers.vocable_trainer import VocableEntry
from lingularity.backend.database import MongoDBClient
from lingularity.frontend.console.trainers.base import TrainerConsoleFrontend, TrainingOptionCollection
from lingularity.frontend.console.trainers.sentence_translation.options import *
from lingularity.frontend.console.utils.output import (clear_screen, erase_lines, centered_print,
                                                       get_max_line_length_based_indentation,
                                                       DEFAULT_VERTICAL_VIEW_OFFSET)
from lingularity.frontend.console.utils.input_resolution import (resolve_input, recurse_on_unresolvable_input,
                                                                 indissolubility_output)


class SentenceTranslationTrainerConsoleFrontend(TrainerConsoleFrontend):
    _TRAINING_LOOP_INDENTATION = ' ' * 16

    def __init__(self, mongodb_client: MongoDBClient):
        super().__init__(Backend, mongodb_client)

        # select tts language variety if applicable
        if all([self._backend.tts.available, self._backend.tts.language_varieties, not self._backend.tts.language_variety_identifier_set]):
            selected_variety = self._select_language_variety()
            self._backend.tts.change_language_variety(selected_variety)

        # tts
        self._tts_enabled = self._backend.tts.query_enablement()
        self._playback_speed = self._backend.tts.query_playback_speed()
        self._audio_file_path: Optional[str] = None

        self._training_loop_suspended = False

    def _select_language(self, mongodb_client: Optional[MongoDBClient] = None) -> Tuple[str, bool]:
        """
            Returns:
                non-english language: str
                train_english: bool """

        clear_screen()
        eligible_languages = Backend.get_eligible_languages()

        centered_print(f'{DEFAULT_VERTICAL_VIEW_OFFSET}Eligible languages:\n'.upper())
        starting_letter_grouped_languages = [', '.join(list(v)) for _, v in groupby(eligible_languages, lambda x: x[0])]
        indentation = get_max_line_length_based_indentation(starting_letter_grouped_languages)

        for language_group in starting_letter_grouped_languages:
            print(indentation, language_group)

        selection, train_english = resolve_input(input(f'{self.SELECTION_QUERY_OUTPUT_OFFSET}Select language: '), eligible_languages), False
        if selection is None:
            return recurse_on_unresolvable_input(self._select_language, n_deletion_lines=-1)

        elif selection == 'English':
            eligible_languages.remove('English')
            reference_language_validity = False

            while not reference_language_validity:
                reference_language = resolve_input(input('Enter desired reference language: \n\n'), eligible_languages)
                if reference_language is None:
                    print("Couldn't resolve input")
                    time.sleep(1)
                else:
                    selection = reference_language
                    train_english, reference_language_validity = [True]*2
        return selection, train_english

    def _get_training_options(self) -> TrainingOptionCollection:
        SentenceTranslationOption.set_frontend_instance(self)

        option_classes = [AddVocabulary, AlterLatestVocableEntry, Exit]

        if self._backend.tts.available:
            option_classes += [EnableTTS, DisableTTS, ChangePlaybackSpeed]

        if self._backend.tts.language_varieties_available:
            option_classes.append(ChangeTTSLanguageVariety)

        return TrainingOptionCollection(option_classes)

    # -----------------
    # Driver
    # -----------------
    def run(self):
        self._backend.training_mode = self._select_mode()
        self._backend.set_item_iterator()
        cursor.hide()

        self._display_instructions()
        self._run_training()

        self._backend.enter_session_statistics_into_database(self._n_trained_items)
        self._plot_training_history()

    # -----------------
    # Pre training
    # -----------------
    def _select_mode(self) -> str:
        explanations = (
            'show me sentences containing rather infrequently used vocabulary',
            'show me sentences comprising exclusively commonly used vocabulary',
            'just hit me with dem sentences')

        clear_screen()
        centered_print(f'{DEFAULT_VERTICAL_VIEW_OFFSET}TRAINING MODES\n')

        indentation = get_max_line_length_based_indentation(explanations)
        for i, training_mode in enumerate(Backend.TrainingMode):
            print(f'{indentation}{training_mode.value.title()}:')
            print(f'{indentation}\t{explanations[i]}\n')

        if (mode_selection := resolve_input(input(f'{self.SELECTION_QUERY_OUTPUT_OFFSET}Enter desired mode: '), Backend.TrainingMode.values())) is None:
            return recurse_on_unresolvable_input(self._select_mode, n_deletion_lines=-1)

        print('\n', end='')
        return mode_selection

    def _display_instructions(self):
        clear_screen()
        centered_print(f"{DEFAULT_VERTICAL_VIEW_OFFSET * 2}Document comprises {self._backend.n_training_items:,d} sentences.\n\n")

        indentation = get_max_line_length_based_indentation(self._training_options.instructions)
        for i, line in enumerate(self._training_options.instructions):
            print(indentation, line)

            if i == 2:
                centered_print('Text-to-Speech Options\n')

        # print let's go translation
        print('\n' * 2, end='')
        self._output_lets_go()

    # -----------------
    # Training
    # -----------------
    @property
    def _tts_available_and_enabled(self) -> bool:
        return self._backend.tts.available and self._tts_enabled

    def _remove_audio_file(self):
        os.remove(self._audio_file_path)
        self._audio_file_path = None

    def _pending_output(self):
        print(f"{self._TRAINING_LOOP_INDENTATION}pending... ")

    def _run_training(self):
        translation: Optional[str] = None

        while True:
            if not self._training_loop_suspended:
                # get sentence pair
                if (sentence_pair := self._backend.get_training_item()) is None:
                    print('\nSentence data file depleted')
                    return

                # try to convert forenames, output reference language sentence
                reference_sentence, translation = self._backend.forename_converter(sentence_pair)
                self._buffer_print(f'{self._TRAINING_LOOP_INDENTATION}{reference_sentence}')
                self._pending_output()

            # get tts audio file if available
            if self._tts_available_and_enabled and self._audio_file_path is None:
                self._audio_file_path = self._backend.tts.download_audio(text=translation)

            self._training_loop_suspended = False

            # get response, execute selected option if applicable
            if (response := resolve_input(input('$'), options=self._training_options.keywords + [''])) is not None:
                if len(response):
                    self._training_options[response].execute()
                    if type(self._training_options[response]) is Exit:
                        return

            else:
                indissolubility_output("Couldn't resolve input", sleep_duration=0.8, n_deletion_lines=2)
                self._training_loop_suspended = True

            if not self._training_loop_suspended:
                # erase pending... + entered option identifier
                erase_lines(2)

                # output translation
                self._buffer_print(f'{self._TRAINING_LOOP_INDENTATION}{translation}')
                self._buffer_print(f'{self._TRAINING_LOOP_INDENTATION}_______________')

                # play tts file if available, otherwise suspend program
                # for some time to incentivise gleaning over translation
                if self._tts_available_and_enabled:
                    self._backend.tts.play_audio_file(self._audio_file_path, self._playback_speed, suspend_program_for_duration=True)
                    self._remove_audio_file()
                else:
                    time.sleep(len(translation) * 0.05)

                self._n_trained_items += 1

                if self._n_trained_items >= 5:
                    self._buffer_print.partially_redo_buffer_content(n_deletion_lines=3)