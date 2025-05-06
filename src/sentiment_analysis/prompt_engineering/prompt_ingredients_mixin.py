"""
prompt_ingredients_mixin.py
---------------------------
Version 1.0, updated on 2025-01-03

"""

from typing import List, Tuple

from src.utils.data_utils import is_none_or_empty
from src.utils.list_utils import permute_and_join
from type_aliases import PromptIngredientsType


class PromptIngredientsMixin:
    """
    PromptIngredientsMixin class.

    This class provides and manages prompt ingredients.

    Prompt ingredients are recurring elements that will be used to constitute
    prompt parts which are defined by their position in a query string. Prompt
    ingredients can be basic or composed of other ingredients.

    See Also
    --------
    PromptGenerator
        Class that generates the bigger prompt parts and assembles them to
        build a prompt.

    """

    # region --- Properties : Ingredients collections

    @property
    def _all_ingredients(self) \
            -> PromptIngredientsType:
        """
        Retrieves all prompt ingredients.

        Returns
        -------
        PromptIngredientsType
            A dictionary where the keys represent ingredient categories, and
            the values are lists of equivalent values that are interchangeable
            within their respective categories.

        Notes
        -----
        This is a protected setter since it should only be called inside the
        mixin and the concrete prompt engineering strategies. It should not
        be called from the context of the prompt engineeriong strategy
        pattern (i.e. it should not be used to provide the PromptEngineer
        with data to return outside).

        """

        if is_none_or_empty(getattr(self, '__all_ingredients', None)):
            self._initialize_all_ingredients()

        return getattr(self, '__all_ingredients', None)

    @_all_ingredients.setter
    def _all_ingredients(self, ingredients: PromptIngredientsType) \
            -> None:
        """
        Sets _all_ingredients.

        Parameters
        ----------
        ingredients : PromptIngredientsType
            A dictionary where the keys are prompt ingredients categories
            and the values are lists of possible values the categories can
            have.

        """

        setattr(self, '__all_ingredients', ingredients)

    @property
    def _basic_ingredients(self) \
            -> PromptIngredientsType:
        """
        Gets the basic ingredients dictionary.

        The basic ingredients are used to compose bigger prompt ingredients.

        Returns
        -------
        PromptIngredientsType
            A dictionary where the keys are the types of the basic
            ingredients and the values are lists of equivalent variants of
            the given basic ingredients types.

        """

        if is_none_or_empty(getattr(self, '__basic_ingredients', {})):
            self._set_basic_ingredients()

        return getattr(self, '__basic_ingredients', {})

    @_basic_ingredients.setter
    def _basic_ingredients(self, ingredients: PromptIngredientsType) \
            -> None:
        """
        Sets the basic ingredients dictionary.

        Parameters
        ----------
        ingredients : PromptIngredientsType
            The basic ingredients dictionary.

        """

        setattr(self, '__basic_ingredients', ingredients)

    @property
    def _basic_and_composed_ingredients(self) \
            -> List[Tuple[str, str]]:
        """
        Gets the list of basic and corresponding composed ingredients types.

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
        if is_none_or_empty(
            getattr(self, '__basic_and_composed_ingredients', [])
        ):
            self._set_basic_and_composed_ingredients()

        return getattr(self, '__basic_and_composed_ingredients', [])

    @_basic_and_composed_ingredients.setter
    def _basic_and_composed_ingredients(
            self,
            basic_and_composed_ingredients: List[Tuple[str, str]]
    ) -> None:
        setattr(
            self,
            '__basic_and_composed_ingredients',
            basic_and_composed_ingredients
        )

    # endregion --- Properties : Ingredients collections

    # region --- Properties : Lists to include in _all_ingredients

    @property
    def sentiment_orders(self) \
            -> List[Tuple[str, ...]]:
        """
        Gets all permutations of sentiment orders.

        The sentiment order to use for the generation of the 'scale' parts
        of the prompts will be chosen randomly from the list of all
        permutated sentiment orders to account for the possibility that the
        the LLM's answers are influenced by the way its possible choices are
        expressed.

        It is also made a distinction between sentiments with and without
        quotation marks.

        Returns
        -------
        List[tuple[str, ...]]
            List of sentiment order permutations.

        Notes
        -----
        Produces 2 x 3! = 12 sentiment order variants.

        """

        # Without quotation marks
        sentiments_1 = ['positive', 'negative', 'neutral']

        # With quotation marks
        sentiments_2 = ['"positive"', '"negative"', '"neutral"']

        return permute_and_join(sentiments_1, sentiments_2)

    @property
    def sentiment_orders_as_strings(self) \
            -> List[str]:
        """
        Converts the sentiment orders to string format.

        Generates strings from the orders in the sentiment orders list to
        prepare them to be used as ingredients for bigger prompt ingredients.

        Returns
        -------
        List[str]
           List of sentiment orders in string format.

        Notes
        -----
        Doubles the number of sentiment order variants because variants with
        and without comma before 'or' are included => Produces 2 x 2 x 3! =
        24 string variants.

        """

        orders = []
        for order in self.sentiment_orders:
            orders.append(
                f"{order[0]}, {order[1]}, or {order[2]}, "
            )
            orders.append(
                f"{order[0]}, {order[1]} or {order[2]}, "
            )
        return orders

    @property
    def sentiment_enumerations(self) \
            -> List[str]:
        """
        Gets the list of sentiment enumerations.

        Returns
        -------
        List[str]
            List of sentiment enumerations.

        """

        sentiment_enumeration = []

        for intro in self._all_ingredients['sentiment_introductions']:
            for order in self.sentiment_orders_as_strings:
                sentiment_enumeration.append(
                    f"{intro}{order}"
                )

        return sentiment_enumeration

    # endregion --- Properties : Lists to include in _all_ingredients

    # region --- Public Methods
    def answers_before_mention(
            self,
            thoughts: List[str],
            towards: List[str],
            whats: List[str]
    ):
        """
        Generates the answer text to place before the mention of the target.

        Generates the answer introduction text to place before the mention
        of the target person based on the provided inputs.

        Parameters
        ----------
        thoughts : List[str]
            List of expressions for the thinking or evaluation process
            "undergone" by the LLM to find the appropriate answer it is asked
            for. Signs of security/insecurity, subjectivity/objectivity or
            similar attitudes about the provided answer.

        towards : List[str]
             List of "towards" synonyms.

        whats : List[str]
            List of variants to designate the sentence in which to identify
            the sentiment.

        Returns
        -------
        List[str]
            List of generated answers introduction texts to place before the
            mention of the target person.

        """

        return [
            f'\nYour answer: {thought}{what}{toward}'
            for thought in thoughts
            for what in whats
            for toward in towards
        ]

    def questions(
            self,
            towards: List[str],
            targets: List[str],
            givens: List[str]
    ):
        """
        Generates questions based on the provided inputs.

        Parameters
        ----------
        towards : List[str]
            List of "towards" synonyms.

        targets : List[str]
            List of synonyms referencing the person that is the target of
            the sentiment the LLM is required to identify.

        givens : List[str]
            List of elements that can be used at the same position as
            "(the) given", e.g. "(the) specified".

        Returns
        -------
        List[str]
            List of generated questions.

        """

        return [
            f'what is the sentiment {toward}{given}{target}? '
            for toward in towards
            for target in targets
            for given in givens
        ]

    # endregion --- Public Methods

    # region --- Protected Methods

    def _initialize_all_ingredients(self) \
            -> None:
        """
        Sets the _all_ingredients property to initial values.

        """
        # Some fields are temporarily left unfilled because they build on other
        # categories in the dictionary.
        #
        # Very basic ingredients as "the " in the 'givens' category must be
        # put at the end of the corresponding list because the decomposition
        # of ingredients into basic ingredients will recognize similar words
        # in other positions than the 'givens' positions as matches.
        #
        # Ingredients that appear in other ingredients (like 'individual'
        # does in 'target individual') must be put behind the longer
        # ingredient so that the decomposition can first find the longer
        # ingredient.

        self._all_ingredients = {
            'answer_starts':
                [
                    ' appears to be',
                    ' can be called',
                    ' can be labeled as',
                    ' can be qualified as',
                    ' can be said to be quite',
                    ' can be said to be rather',
                    ' can be said to be relatively',
                    ' is more or less',
                    ' is quite',
                    ' is rather',
                    ' is relatively',
                    ' must be called',
                    ' tends to be',
                    ' is',
                ],
            'basic_scales':
                [
                    'On a scale from negative to neutral to positive, ',
                    'On a scale from positive to neutral to negative, ',
                    'On a scale from "negative" to "neutral" to "positive", ',
                    'On a scale from "positive" to "neutral" to "negative", ',
                ],
            'givens':
                [
                    'the specified ',
                    'the mentioned ',
                    'the given ',
                    'the following ',
                    'this ',
                    'the ',
                ],
            'politenesses':
                [
                    'Please ',
                    'I would like you to ',
                    'Can you ',
                    '',
                ],
            'prepositions':
                [
                    'in '
                ],
            'scales':
                [],
            'sentence_labels':
                [
                    'Here is the ',
                    '',
                ],
            'sentiment_introductions':
                [
                    'The sentiment being either ',
                    'The sentiment being ',
                    'The possible sentiments being either ',
                    'The possible sentiments being ',
                ],
            'sentiment_orders':
                self.sentiment_orders,
            'targets':
                [
                    'target individual',
                    'target person',
                    'individual',
                    'person',
                    'target',

                ],
            'tasks':
                [
                    'apply a target-dependent sentiment analysis on ',
                    'carefully analyse ',
                    'carefully analyze ',
                    'determine ',
                    'identify ',
                    'specify ',
                    'thoroughly analyse ',
                    'thoroughly analyze ',
                    'analyse ',
                    'analyze ',
                ],
            'thoughts':
                [
                    'Analyzing this sentence, I conclude that ',
                    'As far as I\'m concerned, ',
                    'As I see it, ',
                    'As I understand it, ',
                    'Clearly, ',
                    'For me, ',
                    'From my perspective, ',
                    'Having analyzed this sentence, I believe that ',
                    'Having analyzed this sentence, I find that ',
                    'Having analyzed this sentence, I firmly believe that ',
                    'Having analyzed this sentence, I have come to the '
                    'conclusion ',
                    'Having analyzed this sentence, I tend to think that ',
                    'Having analyzed this sentence, I think that ',
                    'Having analyzed this sentence, I would think that ',
                    'I believe that ',
                    'I feel that ',
                    'I might be wrong, but ',
                    'I tend to think that ',
                    'I think ',
                    'I would think that ',
                    'If I grasp it correctly, ',
                    'If I understand it right, ',
                    'If I were to guess, ',
                    'If my understanding is correct, ',
                    'If we look at it objectively, ',
                    'If you ask me, ',
                    'In my experience, ',
                    'In my humble opinion, ',
                    'In my opinion, ',
                    'In my view, ',
                    'It is my belief that ',
                    'It is my opinion that ',
                    'It seems that ',
                    'My view is that ',
                    'Objectively speaking, ',
                    'Obviously, ',
                    'Personally, ',
                    'Speaking for myself, ',
                    'The way I see it, ',
                    'To me, ',
                    'To my knowledge, ',
                    'To my mind, ',
                    'To my way of thinking, ',
                    'that ',
                    '',
                ],
            'towards':
                [
                    'about ',
                    'concerning ',
                    'directed at ',
                    'on the subject of ',
                    'regarding ',
                    'related to ',
                    'relating to ',
                    'targeted at ',
                    'toward ',
                    'towards ',
                ],
            'whats':
                [
                    'the sentiment ',
                    'the stance ',
                    'the opinion ',
                    'the view ',
                    'the viewpoint ',
                    'the feeling ',
                ],
            'wheres':
                [
                    'assertion ',
                    'opinion ',
                    'sentence ',
                    'statement ',
                    'text ',
                    'utterance ',
                ]
        }

        # Values to fill in after self._all_ingredients has been temporarily
        # set
        _all = self._all_ingredients

        _all['scales'] = (
                _all['basic_scales'] +
                self.sentiment_enumerations
        )

    def _set_basic_ingredients(self) \
            -> None:
        self._basic_ingredients = {
            'answer_start': self._all_ingredients['answer_starts'],
            'basic_scale': self._all_ingredients['basic_scales'],
            'given': self._all_ingredients['givens'],
            'order': self.sentiment_orders_as_strings,
            'politeness': self._all_ingredients['politenesses'],
            'scale': self._all_ingredients['scales'],
            'sentence_label': self._all_ingredients['sentence_labels'],
            'sentiment_intro': self._all_ingredients[
                'sentiment_introductions'
            ],
            'target': self._all_ingredients['targets'],
            'task': self._all_ingredients['tasks'],
            'thought': self._all_ingredients['thoughts'],
            'what': self._all_ingredients['whats'],
            'where': self._all_ingredients['wheres'],
        }

    def _set_basic_and_composed_ingredients(self) \
            -> None:
        """

        Returns
        -------

        Notes
        -----
        The first element of each tuple is a basic ingredient type and
        the second a composed ingredient type the basic ingredient
        type contributes to compose. A basic ingredient type can
        be used in various composed ingredients types and a composed
        ingredient type usually is composed of multiple basic
        ingredients types

        """
        self._basic_and_composed_ingredients = [
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

    # endregion --- Protected Methods
