"""
prompt_engineering_strategy_4.py
--------------------------------
Version 1.0, updated on 2025-02-05

"""

from typing import List, Tuple

from pandas import DataFrame

from src.sentiment_analysis.prompt_engineering.prompt_engineering_strategy \
    import PromptEngineeringStrategy
from src.utils.data_utils import is_none_or_empty
from src.utils.dict_utils import merge_dicts, exclude_list_elements_from_dict
from type_aliases import PromptsDictType, PromptIngredientsType


class PromptEngineeringStrategy4(PromptEngineeringStrategy):
    """
    PromptEngineeringStrategy4 class.
    
    This class is a concrete implementation of the PromptEngineeringStrategy
    interface for generating a third set of prompts.

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

        Initializes the PromptEngineeringStrategy3 class passing the number
        of prompts generated in this class to the parent class.

        """

        super().__init__(self.N_PROMPTS)

        self._apply_changes()
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
        """
        Returns the prompt ingredients.

        The prompt ingredients are organized into various categories, some of
        which are used to compose other categories but are not used
        independently, such as 'basic scales', 'sentiment introductions',
        and 'sentiment orders'. These categories are not exposed explicitly.

        Returns
        -------
        PromptIngredientsType
            A dictionary where the keys are the types of the ingredients and
            the values are lists of equivalent variants of the given
            ingredients types.

        """

        _all = self._all_ingredients

        """
        Some of the categories in the _all_ingredients dictionary were used 
        to compose other categories but are not used independently:

        - basic scales
        - sentiment introductions
        - sentiment orders

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
        Returns basic ingredients and corresponding composed ingredients.

        This method retrieves a list of tuple pairs, where each tuple consists
        of a basic ingredient and its associated composed ingredient.

        Returns
        -------
        List[Tuple[str, str]]
            A list of paired tuples representing the relationship between
            basic ingredients and composed ingredients. Each tuple's first
            element denotes the basic ingredient, while the second element
            identifies the corresponding composed ingredient.

        Notes
        -----
        For the finegrained prompt optimization analysis, only the first three
        tuples in the returned list are relevant. The correlation analysis
        in the context of prompt evaluation uses the other tuples as well,
        though.

        """

        return [
            ('sentiment_intro', 'scale'),
            ('order', 'scale'),
            ('scale', 'scale'),

            ('given', 'question'),
            ('target', 'question'),
            ('what', 'question'),
            ('target', 'before_mention'),
            ('thought', 'answer_before_mention'),
            ('answer_start', 'answer_start'),
            ('given', 'before_sentence'),
            ('politeness', 'before_sentence'),
            ('target', 'before_sentence'),
            ('sentence_label', 'before_sentence'),
            ('task', 'before_sentence'),
            ('what', 'before_sentence'),
            ('where', 'before_sentence'),

        ]

    @property
    def exclude(self) \
            -> PromptIngredientsType:
        """
        Returns the prompt ingredients to exclude from all ingredients.

        Returns
        -------
        PromptIngredientsType:
            A dictionary where the keys are prompt ingredients categories
            and the values are lists of possible values the categories can
            have.

        """

        return {
            'answer_starts':
                [
                    ' is rather',
                ],
            'givens':
                [
                    'the specified ',
                ],
            'politenesses':
                [
                    'Can you '
                ],
            'prepositions':
                [],
            'basic_scales':
                [],
            'scales':
                [
                    'The possible sentiments being "negative", "neutral" or '
                    '"positive", ',
                    'The possible sentiments being "negative", "neutral", or '
                    '"positive", ',
                    'The possible sentiments being either "positive", '
                    '"negative" or "neutral", ',
                    'The possible sentiments being neutral, negative or '
                    'positive, ',
                    'The sentiment being "negative", "positive" or '
                    '"neutral", ',
                    'The sentiment being "positive", "neutral" or '
                    '"negative", ',
                    'The sentiment being either "negative", "positive", or '
                    '"neutral", ',
                    'The sentiment being either "neutral", "negative", or '
                    '"positive", ',

                    'The possible sentiments being either negative, positive, '
                    'or neutral, ',
                    'The possible sentiments being negative, positive, or '
                    'neutral, ',
                    'The possible sentiments being positive, negative or '
                    'neutral, ',
                    'The possible sentiments being positive, neutral or '
                    'negative, ',
                    'The sentiment being "neutral", "positive" or '
                    '"negative", ',
                    'The sentiment being either "positive", "negative" or '
                    '"neutral", ',
                    'The sentiment being either "positive", "negative", or '
                    '"neutral", ',
                    'The sentiment being either negative, neutral, or '
                    'positive, ',
                    'The sentiment being positive, negative, or neutral, '
                ],
            'sentence_labels':
                [],
            'sentiment_introductions':
                [],
            'sentiment_orders':
                [
                    ('negative', 'positive', 'neutral'),

                    ('"positive"', '"negative"', '"neutral"'),
                ],
            'targets':
                [],
            'tasks':
                [],
            'thoughts':
                [
                    'If I grasp it correctly, ',
                    'Analyzing this sentence, I conclude that ',
                    'For me, ',
                    'It is my belief that ',
                    '',

                    'Clearly, ',
                    'I might be wrong, but ',
                    'If I were to guess, ',
                    'To my knowledge, ',
                ],
            'towards':
                [],
            'whats':
                [],
            'wheres':
                []
        }

    @property
    def include(self):
        """
        Returns the prompt ingredients to add to all ingredients.

        Returns
        -------
        PromptIngredientsType:
            A dictionary where the keys are prompt ingredients categories
            and the values are lists of possible values the categories can
            hav.

        """

        return {
            'answer_starts':
                [],
            'givens':
                [],
            'politenesses':
                [],
            'prepositions':
                [],
            'basic_scales':
                [],
            'scales':
                [],
            'sentence_labels':
                [],
            'sentiment_introductions':
                [],
            'sentiment_orders':
                [],
            'targets':
                [],
            'tasks':
                [],
            'thoughts':
                [],
            'towards':
                [],
            'whats':
                [],
            'wheres':
                []
        }

    @property
    def scales(self) \
            -> List[str]:
        """
        Returns the list of scales used in prompt engineering, including basic
        scales and sentiment enumerations.

        This property combines the two separate lists - basic scales and
        sentiment enumerations - into a single list that represents the
        complete set of scales.

        Returns
        -------
        List[str]
            The combined list of strings representing all the scales.

        """

        return self.basic_scales + self.sentiment_enumerations

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
                lambda row: ''.join(filter(None, [
                    val.get('before_sentence'),
                    f"'{row['sentence_normalized']}'" if
                    'sentence_normalized' in row else None,
                    val.get('before_mention'),
                    row.get('mention', ''),
                    '\n',
                    val.get('scale'),
                    val.get('question'),
                    val.get('answer_before_mention'),
                    row.get('mention', ''),
                    val.get('answer_start')
                ])),
                axis=1
            )
        return samples

    # endregion --- Public Methods

    # region --- Protected Methods

    def _apply_changes(self) \
            -> None:
        """
        Adds additional prompt ingredients and removes unwished ones.

        Updates the all_ingredients dictionary by

        - removing the prompt ingredients specified in the exclude property
        - and adding the ingredients specified in the self.include property.

        """

        all_ingredients = self._all_ingredients.copy()
        excluded = self.exclude
        included = self.include

        reduced_all = exclude_list_elements_from_dict(
            all_ingredients, excluded
        )
        new_all = merge_dicts(reduced_all, included)

        self._all_ingredients = new_all

    # endregion --- Protected Methods
