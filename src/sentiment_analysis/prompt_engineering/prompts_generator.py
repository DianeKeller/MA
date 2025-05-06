"""
prompts_generator.py
--------------------
Version 1.0, updated on 2025-01-11

"""

import random
from typing import Dict

from logger import Logger
from src.sentiment_analysis.prompt_engineering.prompt_generator_factory \
    import get_prompt_generator
from src.data_structures.history import History
from src.decorators.time_decorators import duration
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.utils.dict_utils import value_is_in_dict
from type_aliases import PromptsDictType, PromptIngredientsType


class PromptsGenerator(LoggingMixin):
    """
    PromptsGenerator class

    This class orchestrates the systematic generation of prompts, ensuring

    - the desired number of prompts is generated from randomly chosen prompt
      ingredients,

    - no prompt is generated twice for the same LLM and data suite combination,

    - each prompt is guaranteed to induce the requested API to return a
      valid response.

    Attributes
    ----------
    config : SentimentAnalysisConfig
        The configuration object that holds settings for sentiment analysis.

    llm: Llm
        Llm instance.

    prompt_counter : int
        Counter for the prompts used to initialize and track the prompt
        generation.

    prompt_ingredients: PromptIngredientsType
        A dictionary where the keys are prompt ingredients categories
        and the values are lists of possible values the categories can
        have.

    prompt_ingredients_history: History
        History to keep track of all prompts ever used.

    target_n_prompts : int
        The number of prompts to generate.


    Methods
    -------
    generate_prompts() -> PromptsDictType:
        Generates the target number of prompts.

    """

    prompt_counter = 0

    def __init__(
            self,
            prompt_ingredients: PromptIngredientsType,
            prompt_generation_strategy_nr: int = 1
    ) -> None:
        """
        Constructor.

        Initializes the PromptsGenerator class with the provided
        prompt ingredients dictionary and sets the target number of
        prompts to generate.

        """

        self._previous_history: History | None = None
        self._prompt_generation_strategy_nr: int = (
            prompt_generation_strategy_nr
        )

        # Override the default logger of the 'LoggingMixin' class.
        self.logger: Logger = Logger(self.__class__.__name__).get_logger()

        self.prompt_ingredients: PromptIngredientsType = prompt_ingredients

        self.config = SentimentAnalysisConfig()

        self.version = self.config.get("version")
        target_n_prompts = self.config.get("target_n_prompts")
        self.llm = self.config.get("llm")
        self.llm_name = self.llm.name

        # Set history to keep track of all prompts ever used.
        self.prompt_ingredients_history = History(
            name=f'{self.llm_name}_'
                 f'{target_n_prompts}_prompt_ingredients_v_'
                 f'{self.version}'
        )
        self._set_previous_history()

        # Dictionary for all validated prompts
        self.validated_prompts: PromptsDictType = {}

        # Continue the prompt counter from the previous _prompt_engineering
        # runs so that the history can be continued and ensure that the same
        # prompt sets are not processed multiple times.
        self.prompt_counter_start = (len(self.prompt_ingredients_history.data)
                                     + 1)
        self.target_n_prompts = self.prompt_counter_start + target_n_prompts

        self.prompt_counter = self.prompt_counter_start

    @property
    def prompt_generation_strategy_nr(self) \
            -> int:
        return self._prompt_generation_strategy_nr

    @prompt_generation_strategy_nr.setter
    def prompt_generation_strategy_nr(self, strategy_nr: int) \
            -> None:

        self._prompt_generation_strategy_nr = strategy_nr

    # region --- Properties
    @property
    def target_n_prompts(self) \
            -> int:
        """
        Returns the target number of prompts.

        Returns the target number of prompts including all prompts already
        used. E.g., if a set of 150 prompts has already been generated in a
        previous run, the count starts with 151 and the target number for
        a new run of 150 prompts will be 300.

        """

        return self._target_n_prompts

    @target_n_prompts.setter
    def target_n_prompts(self, n_prompts: int) \
            -> None:
        """
        Sets the target number of prompts.

        """

        self._target_n_prompts = n_prompts

    @property
    def previous_history(self) \
            -> History | None:

        return self._previous_history

    @previous_history.setter
    def previous_history(self, history: History) \
            -> None:
        self._previous_history = history

    def _set_previous_history(self) \
            -> None:

        strategy_nr = int(self.version)
        if strategy_nr == 3:
            previous_version = str(strategy_nr - 1).zfill(2)
            # Do not rely on self.target_n_prompts but retrieve the original
            # value from the config
            target_n_prompts = self.config.get("target_n_prompts")
            self.previous_history = History(
                name=f'{self.llm_name}_'
                     f'{target_n_prompts}_prompt_ingredients_v_'
                     f'{previous_version}'
            )

    # endregion --- Properties

    # region --- Public Methods
    @duration
    def generate_prompts(self) \
            -> PromptsDictType:
        """
        Generates the target number of prompts.

        The target number of prompts is set in the sentiment analysis
        configuration via the _set_prompt_engineering_config method in the
        PromptEngineeringStrategy class.

        Returns
        -------
        PromptsDictType
            A dictionary with validated prompts, where the keys are the
            integer numbers of the prompts and the values are dictionaries
            containing the prompts, where the keys are the positions where
            each prompt part should go and the values are the prompt parts.

        Notes
        ------
        Any errors that occur when querying the LLM are handled by the
        query_error_handling decorator that decorates the send_query method
        in the QueryProcessor class.

        """

        while self.prompt_counter < self.target_n_prompts:

            # Get a maximum of 5 elements from a randomly chosen ingredients
            # category
            random_ingredients_list = self._get_random_ingredients_list()

            # Get one randomly chosen element from each ot the other categories
            other_random_ingredients = (
                self._get_other_random_ingredients_elements(
                    list(random_ingredients_list.keys())[0]
                )
            )

            ingredient_type = list(random_ingredients_list.keys())[0]

            # Iterate through the first ingredients list
            variants = list(random_ingredients_list.values())[0]

            for variant in variants:

                # Assemble the prompt ingredients (one of each category)
                selected_ingredients = {
                    **other_random_ingredients,
                    ingredient_type: variant
                }

                if not self._generate_validated_prompt(selected_ingredients):
                    msg = "Prompt could not be validated!"
                    self._log(msg, "info")

                    break

                print(self.prompt_counter)

                self.prompt_counter += 1

                if self.prompt_counter == self.target_n_prompts:
                    msg = "Last prompt processed!"
                    self._log(msg, "info")

                    break

                msg = "Validating next prompt..."
                self._log(msg, "info", "Validating next prompt")

        return self.validated_prompts

    # endregion --- Public Methods

    # region --- Protected Methods

    def _generate_validated_prompt(
            self,
            selected_ingredients: Dict[str, str]
    ) -> bool:
        """
        Generates and validates a prompt based on the selected ingredients,
        ensuring that there are no duplicates in the prompt history and that
        the prompt itself yields valid responses.

        This method incorporates a series of checks to verify:
        1. The selected ingredients are not already used before.
        2. The generated prompt based on the selected ingredients is valid.
        3. No duplicate prompts are introduced in the validated prompt history.

        Parameters
        ----------
        selected_ingredients : Dict[str, str]
            A dictionary of selected ingredient names mapped to their
            respective values, which are utilized to generate new prompts.

        Returns
        -------
        bool
            Returns True if the generated prompt is successfully validated and
            added to the history. Returns False otherwise.

        Raises
        ------
        CriticalException
            Raised if a duplicate prompt is found in the validated prompts,
            indicating an issue during the validation or history-check
            processes.

        """

        if self._are_not_in_history(selected_ingredients):

            prompt = self._generate_prompt(selected_ingredients)

            # Ensure that the generated prompt produces a valid response
            if self._validate_prompt(prompt):
                # If no exception was raised, all is fine and can be saved.
                # Double check for duplicates. Duplicates could only happen if
                # something in the history check or in the transformation of
                # the selected ingredients into a prompt went wrong:
                if value_is_in_dict(prompt, self.validated_prompts):
                    raise CriticalException(
                        self.logger,
                        "Duplicate prompt found"
                    )

                self.validated_prompts[str(self.prompt_counter)] = prompt

                self.prompt_ingredients_history.add(selected_ingredients)

                return True
            return False
        return False

    def _generate_prompt(self, selected_ingredients: Dict[str, str]) \
            -> Dict[str, str]:
        """
        Generates a prompt based on the given selected ingredients.

        This method creates a prompt generator instance using the provided
        ingredients dictionary and invokes its 'generate_prompt' method to
        produce a prompt.

        Parameters
        ----------
        selected_ingredients : Dict[str, str]
            A dictionary where keys are ingredient names and values are their
            selected values.

        Returns
        -------
        Dict[str, str]
            A dictionary representing the generated prompt, based on the
            selected ingredients.

        """

        prompt_generator = get_prompt_generator(
            selected_ingredients, self.prompt_generation_strategy_nr,
        )
        return prompt_generator.generate_prompt()

    def _get_random_ingredients_list(self) \
            -> PromptIngredientsType:
        """
        Returns a random list from the prompt ingredients lists.

        Randomly chooses a list from the prompt ingredients lists. If the
        chosen list has more elements than the maximum number of 5,
        the elements in the returned list are limited to the maximum number,
        picking them randomly from the chosen list. Otherwise, the entire
        list is returned.

        Returns
        -------
        PromptIngredientsType
            A dictionary with a single element where the key is the type of
            the prompt ingredients and the value is the lists of equivalent
            variants of the given prompt ingredients type.

        """

        max_elements = 5
        prompt_ingredients = self.prompt_ingredients

        ingredients_type = random.choice(list(prompt_ingredients.keys()))

        if len(prompt_ingredients[ingredients_type]) <= max_elements:
            return {ingredients_type: prompt_ingredients[ingredients_type]}

        # Limit the number of elements, select the elements randomly
        return {ingredients_type: random.sample(
            prompt_ingredients[ingredients_type], max_elements
        )}

    def _get_other_random_ingredients_elements(self, excluded_key: str) \
            -> Dict[str, str]:
        """
        Returns a randomly chosen element per prompt ingredient type.

        Except for the prompt ingredient type specified by the
        excluded_key, this method chooses one element per prompt
        ingredient type and returns the chosen elements in a dictionary
        where the keys serve to identify the respective ingredient type.

        Parameters
        ----------
        excluded_key : str
            The label of the prompt ingredients list that is not to be
            included in the output dictionary.

        Returns
        -------
        Dict[str, str]
            A dictionary where the key is the prompt ingredient type and the
            value is a randomly picked variant from the corresponding prompt
            ingredient list.

        """

        return {
            key: random.choice(lst)
            for key, lst in self.prompt_ingredients.items()
            if key != excluded_key
        }

    def _log_prompt_exists(
            self,
            selected_ingredients: Dict[str, str],
            history: History | None = None
    ) -> None:
        """
        Logs cases where a prompt was found in the history.

        Parameters
        ----------
        selected_ingredients : Dict[str, str]
            Dictionary of selected ingredients where the keys are ingredient
            categories and the values are the selected ingredient alternatives.

        history : History
            Prompt ingredients history to use for the check.
            
        Notes
        -----
        This method does not return any value. Instead, it logs a message.

        """

        if history is None:
            history = self.prompt_ingredients_history

        prompt_nr = history.get_nr(selected_ingredients)

        msg = (
            f"Prompt {self.prompt_counter} already validated: "
            f"Prompt n° {prompt_nr} in "
            f"{history.name}"
        )

        self._log(msg, 'info')

    def _validate_prompt(self, prompt: Dict[str, str]) \
            -> bool:
        """
        Validates the generated prompt.

        Calls the LLM's validate_prompt method to validate.

        Parameters
        ----------
        prompt : Dict[str, str]
            Dictionary of prompt parts to validate.

        Returns
        -------
        bool
            True if the validation was successful, otherwise False

        """

        if self.llm.validate_prompt('en', prompt):

            # if the validation fails, the validate prompt method will raise an
            # exception, otherwise the validation was successful:
            msg = "Prompt successfully validated!"
            self._log(msg, "info", "Prompt successfully validated")

            return True

        else:
            return False

    # endregion --- Protected Methods
    def _are_not_in_history(self, selected_ingredients: Dict[str, str]) \
            -> bool:
        """
        Ensures that the selected prompt ingredients set is not in the history.

        Parameters
        ----------
        selected_ingredients : Dict[str, str]
            A dictionary where the keys correspond to ingredients categories
            and the values to selected ingredients values.

        Returns
        -------
        bool
            True if the selected prompt ingredients set is not in the history,
            otherwise False.

        """

        history = self.prompt_ingredients_history
        previous_history = self.previous_history

        # Search assembled prompt ingredients in ingredients histories
        # If found, the prompt is logged and discarded

        if (
                previous_history is not None and
                selected_ingredients in previous_history.data
        ):
            self._log_prompt_exists(selected_ingredients, previous_history)
            return False

        if selected_ingredients in history.data:
            self._log_prompt_exists(selected_ingredients, history)
            return False

        return True
