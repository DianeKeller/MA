"""
prompt_engineering_strategy_2.py
--------------------------------
Version 1.0, updated on 2025-02-05

"""

from typing import List, Tuple

from pandas import DataFrame

from src.sentiment_analysis.prompt_engineering.prompt_engineering_strategy \
    import PromptEngineeringStrategy
from src.utils.data_utils import is_none_or_empty
from type_aliases import PromptsDictType, PromptIngredientsType


class PromptEngineeringStrategy2(PromptEngineeringStrategy):
    """
    PromptEngineeringStrategy2 class.

    This class is a concrete implementation of the PromptEngineeringStrategy
    interface for generating a second set of prompts.

    Attributes
    ----------
    N_PROMPTS : int
        The number of prompts that will be generated in this class.

    """

    # Number of prompts that will be generated in this class:
    N_PROMPTS = 150

    def __init__(self):
        """
        Constructor.

        Initializes the PromptEngineeringStrategy2 class passing the number
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
    def prompt_ingredients(self) \
            -> PromptIngredientsType:

        _all = self._all_ingredients

        """
        Some of the categories in the _all_ingredients dictionary were used 
        to compose other categories but are not used independently:
        
        - basic scales
        - sentiment introductions
        - sentiment orders
        
        This is why they are not included in the following prompt_ingredients 
        dictionary, which contains 12 categories.

        """

        ingredients = {
            'answer_start': _all['answer_starts'],
            'given': _all['givens'],
            'politeness': _all['politenesses'],
            'preposition': _all['prepositions'],
            'scale': _all['scales'],
            'sentence_label': _all['sentence_labels'],
            'target': _all['targets'],
            'task': _all['tasks'],
            'thought': _all['thoughts'],
            'toward': _all['towards'],
            'what': _all['whats'],
            'where': _all['wheres'],
        }

        return ingredients

    @property
    def basic_ingredients(self) \
            -> PromptIngredientsType:
        """
        Gets the basic ingredients dictionary.

        The basic ingredients are used to compose bigger prompt ingredients.
        They are provided by the _basic_ingredients property in the
        PromptIngredientsMixin.

        Returns
        -------
        PromptIngredientsType
            A dictionary where the keys are the types of the basic
            ingredients and the values are lists of equivalent variants of
            the given basic ingredients types.

        """

        if is_none_or_empty(self._basic_ingredients):
            # Call _set_basic_ingredients method of the PromptIngredientsMixin
            self._set_basic_ingredients()

        return self._basic_ingredients

    @property
    def basic_and_composed_ingredients(self) \
            -> List[Tuple[str, str]]:
        """
        Gets the list of basic and corresponding composed ingredients types.

        They are provided by the _basic_and_composed_ingredients property in
        the PromptIngredientsMixin.

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

        if is_none_or_empty(self._basic_and_composed_ingredients):
            # Call _set_basic_ingredients method of the PromptIngredientsMixin
            self._set_basic_and_composed_ingredients()

        return self._basic_and_composed_ingredients

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
            samples.loc[:, f'query_{key}'] = samples.apply(
                lambda row: (
                    f"{val.get('before_sentence')}"
                    f"'{row['sentence_normalized']}'"
                    f"{val.get('before_mention')}"
                    f"{row['mention']}\n"
                    f"{val.get('scale')}"
                    f"{val.get('question')}"
                    f"{val.get('answer_before_mention')}"
                    f"{row['mention']}"
                    f"{val.get('answer_start')}"
                ),
                axis=1
            )
        return samples

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
