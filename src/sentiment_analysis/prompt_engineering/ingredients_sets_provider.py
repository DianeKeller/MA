"""
ingredients_sets_provider.py
----------------------------
Version 1.0, updated on 2025-02-07

"""

from typing import TYPE_CHECKING, List

from src.data_structures.history import History
from src.sentiment_analysis.prompt_engineering import (
    prompts_and_ingredients_provider as provider
)
from src.sentiment_analysis.prompt_engineering.prompts import Prompts
from src.utils.data_utils import is_none_or_empty
from src.utils.dict_utils import filter_dict_by_keys
from src.utils.list_utils import to_strings
from type_aliases import PromptsDictType

if TYPE_CHECKING:
    from src.sentiment_analysis.prompt_engineering import (
        prompts_and_ingredients_manager as manager
    )


class IngredientsSetsProvider(provider.PromptsAndIngredientsProvider):
    """
    IngredientsSetsProvider class.

    This class manages and provides ingredients sets.

    Methods
    -------
    def get_prompts(validity: str = '')
            -> Prompts:
        Retrieves and returns the ingredients sets filtered by the specified
        validity.

    """

    def __init__(
            self,
            prompts_manager: "manager.PromptsAndIngredientsManager"
    ):
        """
        Constructor.

        Initializes a new ValidPromptsProvider instance with a
        PromptsManager instance.

        Parameters
        ----------
        prompts_manager : PromptsAndIngredientsManager
            The PromptsAndIngredientsManager instance that called the
            IngredientsSetsProvider to delegate the retrieval of ingredients
            sets.

        """

        super().__init__(prompts_manager)
        self._valid_ingredients_sets = None
        self._invalid_ingredients_sets = None
        self._all_ingredients_sets = None

    # region --- Properties

    @property
    def all_ingredients_sets(self) \
            -> PromptsDictType:
        """
        Returns all normalized prompt ingredients sets.

        If the property is not set yet, this method calls the
        _normalze_ingredients_sets method to retrieve the ingredients sets
        and normalize them.

        Returns
        -------
        PromptsDictType
            The normalized prompt ingredients sets.

        Notes
        -----
        The normalized ingredients sets have the same data type as the
        all_prompts collection, their keys also being aligned to the
        all_prompts collection.

        """

        if is_none_or_empty(self._all_ingredients_sets):
            self._set_all_ingredients_sets()

        return self._all_ingredients_sets

    @all_ingredients_sets.setter
    def all_ingredients_sets(
            self,
            ingredients_sets: PromptsDictType
    ) -> None:
        """
        Sets the normalized ingredients sets.

        Parameters
        ----------
        ingredients_sets : PromptsDictType
            The normalized ingredients sets to be assigned to the property.

        """

        self._all_ingredients_sets = ingredients_sets

    @property
    def valid_ingredients_sets(self) \
            -> Prompts:
        """
        Retrieves the valid prompt ingredients sets.

        If the '_valid_prompt_ingredients' are not set, the
        '_set_valid_and_invalid_ingredients_sets' method is called to
        populate both valid and invalid prompt ingredients sets.

        Returns
        -------
        Prompts
            The valid prompt ingredients sets.

        Notes
        -----
        Prompt ingredients sets are stored as Prompt data types even though
        they are no prompts.

        """

        if is_none_or_empty(self._valid_ingredients_sets):
            self._set_valid_and_invalid_ingredients_sets()

        return self._valid_ingredients_sets

    @valid_ingredients_sets.setter
    def valid_ingredients_sets(self, ingredients_sets: Prompts) \
            -> None:
        """
        Sets the valid ingredients_sets.

        Parameters
        ----------
        ingredients_sets : Prompts
            The valid ingredients sets to be assigned to the property.

        """

        self._valid_ingredients_sets = ingredients_sets

    @property
    def invalid_ingredients_sets(self) \
            -> Prompts:
        """
        Retrieves the invalid prompt ingredients sets.

        If the '_invalid_prompt_ingredients' are not set, the
        '_set_valid_and_invalid_ingredients_sets' method is called to
        populate both valid and invalid prompt ingredients sets.

        Returns
        -------
        Prompts
            The invalid prompt ingredients sets.

        Notes
        -----
        Prompt ingredients sets are stored as Prompt data types even though
        they are no prompts.

        """

        if is_none_or_empty(self._invalid_ingredients_sets):
            self._set_valid_and_invalid_ingredients_sets()

        return self._invalid_ingredients_sets

    @invalid_ingredients_sets.setter
    def invalid_ingredients_sets(self, ingredients_sets: Prompts) \
            -> None:
        """
        Sets the invalid ingredients_sets.

        Parameters
        ----------
        ingredients_sets : Prompts
            The invalid prompts to be assigned to the property.

        """

        self._invalid_ingredients_sets = ingredients_sets

    # endregion --- Properties

    # region --- Public Methods

    def get_prompts(self, validity: str = '') \
            -> Prompts:
        """
        Retrieves the ingredients sets filtered by the specified validity.

        Parameters
        ----------
        validity : str
            The validity ('valid' or 'invalid') to filter by. Default is an
            empty string, which retrieves all ingredients sets without
            filtering.

        Returns
        -------
        Prompts:
            The filtered ingredients sets.

        """

        match validity:
            case 'valid':
                return self.valid_ingredients_sets
            case 'invalid':
                return self.invalid_ingredients_sets
            case 'all' | _:
                return Prompts(
                    self.all_ingredients_sets,
                    self.prompts_manager.ALL_INGREDIENTS_SETS_NAME
                )

    # endregion --- Public Methods

    # region --- Protected Methods

    def _get_ingredients_sets_by_nrs(self, nrs: List[int], name: str) \
            -> Prompts:

        return Prompts(
            filter_dict_by_keys(
                to_strings(nrs),
                self.all_ingredients_sets
            ),
            name
        )

    def _set_all_ingredients_sets(self):
        """
        Sets the all_ingredients_sets property.

        Retrieves all prompt ingredients sets from the PromptEngineer and
        sets the all_ingredients_sets property.

        """

        engineer = self.prompt_engineer

        self.all_ingredients_sets = engineer.get_prompt_ingredients_sets()

    def _set_valid_and_invalid_ingredients_sets(self) \
            -> None:
        """
        Sets the valid and the invalid ingredients sets.

        """

        self.valid_ingredients_sets = self._get_ingredients_sets_by_nrs(
            self.valid_prompt_nrs,
            self.prompts_manager.VALID_INGREDIENTS_SETS_NAME
        )
        self.invalid_ingredients_sets = self._get_ingredients_sets_by_nrs(
            self.invalid_prompt_nrs,
            self.prompts_manager.INVALID_INGREDIENTS_SETS_NAME
        )

    def _get_original_ingredients_sets(self) \
            -> History:
        return self.prompt_engineer.get_prompt_ingredients_sets()

    # endregion --- Protected Methods
