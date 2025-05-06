"""
prompts_provider.py
-------------------
Version 1.0, updated on 2025-02-07

"""

from typing import TYPE_CHECKING, List

from src.sentiment_analysis.prompt_engineering.prompts import Prompts
from src.sentiment_analysis.prompt_engineering import (
    prompts_and_ingredients_provider as provider
)
from src.utils.dict_utils import filter_dict_by_keys
from src.utils.list_utils import to_strings
from src.utils.data_utils import is_none_or_empty

from type_aliases import PromptsDictType

if TYPE_CHECKING:
    from src.sentiment_analysis.prompt_engineering import (
        prompts_and_ingredients_manager as manager
    )


class PromptsProvider(provider.PromptsAndIngredientsProvider):
    """
    PromptsProvider class.

    This class manages and provides prompts from the collection of
    prompts provided in the PromptsAndIngredientsManager class.

    Methods
    -------
    def get_prompts(validity: str = '')
            -> Prompts:
        Retrieves and returns the prompts filtered by the specified validity.

    """

    def __init__(
            self,
            prompts_manager: "manager.PromptsAndIngredientsManager"
    ):
        """
        Constructor.

        Initializes a new PromptsProvider instance with a
        PromptsManager instance.

        Parameters
        ----------
        prompts_manager : manager.PromptsAndIngredientsManager
            The PromptsAndIngredientsManager instance that called the
            PromptsProvider to delegate the retrieval of invalid
            prompts.

        """

        super().__init__(prompts_manager)
        self._discarded_prompts = None
        self._invalid_prompts = None
        self._valid_prompts = None
        self._all_prompts = None

    # region --- Properties
    @property
    def all_prompts(self) \
            -> PromptsDictType:
        """
        Retrieves all prompts from the prompt engineer.

        Returns
        -------
        PromptsDictType
            A dictionary with the prompts, where the keys are
            consecutive prompt numbers starting from 1 and the values are
            dictionaries where the keys are position labels and the values
            are the texts to insert at the indicated positions.

        """

        if is_none_or_empty(self._all_prompts):
            self._set_all_prompts()

        return self._all_prompts

    @all_prompts.setter
    def all_prompts(self, prompts: PromptsDictType) \
            -> None:
        """
        Sets the all prompts property.

        Parameters
        ----------
        prompts : PromptsDictType
            The all prompts to be assigned to the property.

        """

        self._all_prompts = prompts

    @property
    def valid_prompts(self) \
            -> Prompts:
        """
        Retrieves the valid prompts.

        If the '_valid_prompts' are not set, the
        '_set_valid_and_invalid_prompts' method is called to populate both
        valid and invalid prompts.

        Returns
        -------
        Prompts
            The valid prompts.

        Notes
        -----
        A prompt is a set of prompt parts.

        """

        if is_none_or_empty(self._valid_prompts):
            self._set_valid_and_invalid_prompts()

        return self._valid_prompts

    @valid_prompts.setter
    def valid_prompts(self, prompts: Prompts) \
            -> None:
        """
        Sets the valid prompts.

        Parameters
        ----------
        prompts : Prompts
            The valid prompts to be assigned to the property.

        """

        self._valid_prompts = prompts

    @property
    def invalid_prompts(self) \
            -> Prompts:
        """
        Retrieves the invalid prompts.

        If the '_invalid_prompts' are not set, the
        '_set_valid_and_invalid_prompts' method is called to populate both
        valid and invalid prompts.

        Returns
        -------
        Prompts
            The invalid prompts.

        Notes
        -----
        A prompt is a set of prompt parts.

        """

        if is_none_or_empty(self._invalid_prompts):
            self._set_valid_and_invalid_prompts()

        return self._invalid_prompts

    @invalid_prompts.setter
    def invalid_prompts(self, prompts: Prompts) \
            -> None:
        """
        Sets the invalid prompts.

        Parameters
        ----------
        prompts : Prompts
            The invalid prompts to be assigned to the property.

        """

        self._invalid_prompts = prompts

    @property
    def discarded_prompts(self) \
            -> Prompts:
        """
        Retrieves the discarded prompts.

        Returns
        -------
        Prompts
            The discarded prompts.

        """

        if is_none_or_empty(self._discarded_prompts):
            self._set_discarded_prompts()

        return self._discarded_prompts

    @discarded_prompts.setter
    def discarded_prompts(self, prompts: Prompts) \
            -> None:
        """
        Sets the discarded prompts.

        Parameters
        ----------
        prompts : Prompts
            The discarded prompts to be assigned to the property.

        """

        self._discarded_prompts = prompts

    # endregion --- Properties

    # region --- Public Methods

    def get_prompts(self, validity: str = '') \
            -> Prompts:
        """
        Retrieves the prompts filtered by the specified validity.

        Parameters
        ----------
        validity : str
            The validity ('valid' or 'invalid') to filter by. Default is an
            empty string, which retrieves all prompts without filtering.

        Returns
        -------
        Prompts:
            The filtered prompts.

        """

        match validity:
            case 'valid':
                return self.valid_prompts
            case 'invalid':
                return self.invalid_prompts
            case 'discarded':
                return self.discarded_prompts
            case 'all' | _:
                return Prompts(
                    self.all_prompts,
                    self.prompts_manager.ALL_PROMPTS_NAME
                )

    # endregion --- Public Methods

    # region --- Protected Methods

    def _get_prompts_by_nrs(self, nrs: List[int], name: str) \
            -> Prompts:

        return Prompts(
            filter_dict_by_keys(to_strings(nrs), self.all_prompts),
            name
        )

    def _set_all_prompts(self) \
            -> None:
        """
        Sets the all prompts property.

        """

        self.all_prompts = self.prompt_engineer.get_prompts()

    def _set_discarded_prompts(self) \
            -> None:
        """
        Sets the discarded prompts.

        """

        self.discarded_prompts = Prompts(
            self.prompt_engineer.get_discarded_prompts(),
            'discarded'
        )

    def _set_valid_and_invalid_prompts(self) \
            -> None:
        """
        Sets the valid and the invalid prompts.

        """

        self.valid_prompts = self._get_prompts_by_nrs(
            self.valid_prompt_nrs, self.prompts_manager.VALID_PROMPTS_NAME
        )
        self.invalid_prompts = self._get_prompts_by_nrs(
            self.invalid_prompt_nrs, self.prompts_manager.INVALID_PROMPTS_NAME
        )

    # endregion --- Protected Methods
