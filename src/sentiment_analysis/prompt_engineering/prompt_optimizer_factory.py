"""
prompt_optimizer_factory.py
---------------------------
Version 1.0, updated on 2025-02-03

"""

from typing import TYPE_CHECKING

from src.sentiment_analysis.sentiment_analysis_config import \
    SentimentAnalysisConfig
from src.sentiment_analysis.chunk_loader import ChunkLoader

if TYPE_CHECKING:
    from src.sentiment_analysis.prompt_engineering.prompt_optimizer import (
        PromptOptimizer
    )


class PromptOptimizerFactory:
    """
    PromptOptimizerFactory class.

    This class provides factory methods to create PromptOptimizer instances.
    
    """

    @staticmethod
    def create(
            language: str,
            strategy_nr: int = 0
    ) -> "PromptOptimizer":
        """
        Factory method to create a PromptOptimizer instance.

        Parameters
        ----------
        language : str
            The language code for the prompts.

        strategy_nr : int
            The strategy version number to use.

        Returns
        -------
        PromptOptimizer
            A new instance of PromptOptimizer.

        """

        config = SentimentAnalysisConfig()
        if int(config.get('version')) != strategy_nr and strategy_nr != 0:
            config.update(version=str(strategy_nr).zfill(2))

        # Import lazily to avoid circular imports
        from src.sentiment_analysis.prompt_engineering.prompt_optimizer \
            import PromptOptimizer

        chunk_loader = ChunkLoader(
            language=language
        )

        return PromptOptimizer(
            language,
            chunk_loader.chunks
        )

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
