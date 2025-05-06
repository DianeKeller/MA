"""
prompt_engineering_strategy_1.py
--------------------------------
Version 1.0, updated on 2025-05-01

"""

from typing import Dict, List, Tuple

from pandas import DataFrame

from src.sentiment_analysis.prompt_engineering.prompt_engineering_strategy \
    import PromptEngineeringStrategy
from type_aliases import PromptsDictType, PromptIngredientsType


class PromptEngineeringStrategy1(PromptEngineeringStrategy):
    """
    PromptEngineeringStrategy1 class.

    This class is a concrete implementation of the PromptEngineeringStrategy
    interface for generating a first set of prompts.

    Attributes
    ----------
    N_PROMPTS : int
        The number of prompts that will be generated in this class.

    """

    # Number of prompts that will be generated in this class:
    N_PROMPTS = 14

    def __init__(self):
        """
        Constructor.

        Initializes the PromptEngineeringStrategy1 class passing the number
        of prompts generated in this class to the parent class.

        """

        super().__init__(self.N_PROMPTS)

        self.prompt_generating_strategy_nr = 1

    # region --- Properties

    @property
    def prompt_generating_strategy_nr(self) \
            -> int:

        return self._prompt_generating_strategy_nr

    @prompt_generating_strategy_nr.setter
    def prompt_generating_strategy_nr(self, strategy_nr: int) \
            -> None:

        self._prompt_generating_strategy_nr = strategy_nr

    @property
    def prompt_ingredients(self) -> PromptIngredientsType:
        return {
            'before_sentence':
                [
                    'Sentence: '
                ],
            'before_mention':
                [
                    ' The sentiment expressed in this sentence towards ',
                ],
            'scales':
                [
                    ', on a scale from negative to neutral to positive, ',
                    ', on a scale from positive to neutral to negative, '
                ],
            'questions':
                [
                    'is',
                    'is definitely',
                    'most probably is',
                    'most certainly is',
                    'is rather',
                    'tends to be',
                    'is quite',
                ]
        }

    # endregion --- Properties

    # region --- Public Methods
    def add_query_cols(self, samples: DataFrame, chunk: PromptsDictType) \
            -> DataFrame:
        """
        Adds query columns to the provided samples.

        Adds query columns composed from the prompt parts in the provided
        chunk to the samples.

        Parameters
        ----------
        samples : DataFrame
            A samples DataFrame to which to add query columns.

        chunk : PromptsDictType
            Chunk of different prompts to use to create queries for each of
            the samples and add them in columns in the samples DataFrame.

        Returns
        -------
        DataFrame
            The provided samples DataFrame with the different query columns
            added.

        """

        for key, val in chunk.items():
            samples[f'query_{key}'] = samples.apply(
                lambda row: (
                    f"{val.get('before_sentence')}"
                    f"'{row['sentence_normalized']}' "
                    f"{val.get('before_mention')}"
                    f"{row['mention']}"
                    f"{val.get('scale')}"
                    f"{val.get('question')}"
                ),
                axis=1
            )
        return samples

    @property
    def basic_ingredients(self) \
            -> PromptIngredientsType:
        """
        Gets the basic ingredients dictionary.

        The basic ingredients in this strategy are the prompt_ingredients
        themselves, since they are not composed from more basic ingredients.

        Returns
        -------
        PromptIngredientsType
            A dictionary where the keys are the types of the basic
            ingredients and the values are lists of equivalent variants of
            the given basic ingredients types.

        """

        return self.prompt_ingredients

    @property
    def basic_and_composed_ingredients(self) \
            -> List[Tuple[str, str]]:
        """
        Gets the list of basic and corresponding composed ingredients types.

        In this strategy, the basic_and_composed_ingredients list is empty,
        since there are no composed ingredients.

        Returns
        -------
        List[Tuple[str, str]]
            The list of tuples of basic and composed ingredients types.
            The first element of each tuple is a basic ingredient type and
            the second a composed ingredient type the basic ingredient
            type contributes to compose. A basic ingredient type can
            be used in various composed ingredients types and a composed
            ingredient type usually is composed of multiple basic
            ingredients types.

        """

        return []

    # endregion --- Public Methods

    # region --- Protected Methods

    def _generate_prompts(self) \
            -> None:
        """
        Generates and saves prompts.

        Overrides the default '_generate_prompts' method of the parent class.

        """

        positions: Dict[int, str] = {
            1: 'before_sentence',
            2: 'before_mention',
            3: 'scale',
            4: 'question'
        }

        texts_at_position: Dict[int, str] = {
            1: 'Sentence: ',
            2: 'The sentiment expressed in this sentence towards ',
        }

        scales = [
            ', on a scale from negative to neutral to positive, ',
            ', on a scale from positive to neutral to negative, '
        ]

        questions = [
            'is',
            'is definitely',
            'is quite',
            'is rather',
            'most certainly is',
            'most probably is',
            'tends to be',
        ]

        # Dictionary where the keys are consecutive prompt numbers starting
        # from 1 and the values are dictionaries where the keys are position
        # labels and the values are the texts to insert at the indicated
        # positions.
        prompts: PromptsDictType = {}

        counter = 0

        for question in questions:
            for scale in scales:
                counter += 1

                prompts[str(counter)] = {
                    positions[1]: texts_at_position[1],
                    positions[2]: texts_at_position[2],
                    positions[3]: scale,
                    positions[4]: question
                }

        self.prompts = prompts
        self._save_prompts()

    # endregion --- Protected Methods
