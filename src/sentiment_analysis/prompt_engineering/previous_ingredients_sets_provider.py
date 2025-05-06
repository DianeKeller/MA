"""
previous_ingredients_sets_provider.py
-------------------------------------
Version 1.0, updated on 2025-05-01

"""

from typing import TYPE_CHECKING

from src.sentiment_analysis.prompt_engineering import (
    prompts_and_ingredients_manager_factory as factory
)
from src.sentiment_analysis.prompt_engineering import (
    prompts_and_ingredients_provider as provider
)
from src.sentiment_analysis.prompt_engineering.prompts import Prompts
from src.utils.data_utils import is_none_or_empty

if TYPE_CHECKING:
    from src.sentiment_analysis.prompt_engineering import (
        prompts_and_ingredients_manager as manager
    )


class PreviousIngredientsSetsProvider(
    provider.PromptsAndIngredientsProvider
):
    """
    PreviousIngredientsSetsProvider class.

    This class manages and provides valid prompt ingredients sets from previous
    prototypes.

    Methods
    -------
    get_prompts(self)
            -> Prompts:
        Retrieves and returns the previous valid prompt ingredients sets.

    """

    def __init__(
            self,
            prompts_manager: "manager.PromptsAndIngredientsManager"
    ):
        """
        Constructor.

        Initializes a new PreviousIngredientsSetsProvider instance with a
        PromptsManager instance.

        Parameters
        ----------
        prompts_manager : manager.PromptsAndIngredientsManager
            The PromptsAndIngredientsManager instance that called the
            Previous    ValidPromptsProvider to delegate the retrieval of
            previous valid prompts.

        """

        super().__init__(prompts_manager)

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    def get_prompts(self, validity: str = '') \
            -> Prompts:
        """
        Retrieves previous valid ingredients sets.

        Parameters
        ----------
        validity : str
            The validity ('valid' or 'invalid') to filter by. Default is an
            empty string, which retrieves all valid previous ingredients sets.

        Returns
        -------
        Prompts:
            The previous valid ingredients sets.

        """

        match validity:
            case 'invalid':
                raise NotImplementedError
            case 'all':
                raise NotImplementedError
            case 'valid' | _:
                return self._get_previous_valid_ingredients_sets()

    # endregion --- Public Methods

    # region --- Protected Methods

    def _get_previous_valid_ingredients_sets(self) \
            -> Prompts:

        config = self.prompts_manager.config

        current_version = config.get('version')
        current_strategy = int(current_version)

        # Only set previous valid prompts and ingredients if the strategy
        # number is higher than 1
        valid_versions = range(current_strategy - 1, 1, -1)

        if not valid_versions or not self.prompts_manager.check_previous:
            self.prompts_manager.check_previous = False
            return Prompts({}, '')

        self.prompts_manager.check_previous = True
        collected = []

        for version in valid_versions:
            msg = f"Prompts provider: Using strategy nr {version}"
            self._log(msg, 'info', 'PromptsProvider using strategy nr')


            prompts_manager = (
                factory.PromptsAndIngredientsManagerFactory.create(
                    config.get("language"), version))

            if not is_none_or_empty(
                    prompts_manager.valid_ingredients_sets):
                collected.append(
                    prompts_manager.valid_ingredients_sets)

        # Reset the config setting for the version
        self.prompts_manager.config.set('version', current_version)
        print(f"Prompts provider: Strategy reset to {current_version}")

        # Combine and returnresults from all versions
        return Prompts.merge(collected)

    # endregion --- Protected Methods
