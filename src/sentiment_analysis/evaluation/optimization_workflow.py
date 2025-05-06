"""
optimization_workflow.py
------------------------
Version 1.0, updated on 2025-05-01

"""

from typing import TYPE_CHECKING

from src.sentiment_analysis.evaluation.prompt_evaluation import (
    PromptEvaluation
)
from src.sentiment_analysis.prompt_engineering.prompt_optimizer_factory \
    import PromptOptimizerFactory
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)

if TYPE_CHECKING:
    pass


class OptimizationWorkflow:
    """
    OptimizationWorkflow class
    
    """

    def __init__(self, strategy_nr: int = 0):
        # Make the sentiment analysis configuration available in this class
        self.config = SentimentAnalysisConfig()

        if strategy_nr == 0:
            strategy_nr = int(self.config.get('version'))

        self.strategy_nr = strategy_nr
        self.evaluation = PromptEvaluation()

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    def find_optimization_potential_for_language(self, language: str) \
            -> None:
        """
        Finds optimization potentials for prompts for the given language.

        This method evaluates the results of the sentiment predictions
        obtained with the different prompts in terms of valid and invalid
        prompt variants and prompt ingredients in order to know which
        ingredients should be eliminated and which ones should be
        preferred for better results.

        Notes
        -----
        This method does not return anything. Instead, it prints the results
        in the console.

        """

        self.config.set('language', language)
        optimizer = PromptOptimizerFactory.create(language, self.strategy_nr)
        optimizer.correlation_analysis()
        optimizer.finegrained_analysis()
        optimizer.discarded_prompts_analysis()


    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
