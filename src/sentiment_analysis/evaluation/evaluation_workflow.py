"""
evaluation_workflow.py
----------------------
Version 1.0, updated on 2025-01-02

"""
from typing import List

from src.sentiment_analysis.evaluation.prompt_evaluation import (
    PromptEvaluation)
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)


class EvaluationWorkflow:
    """
    EvaluationWorkflow class
    
    """

    def __init__(self, strategy_nr: int = 1):
        # Make the sentiment analysis configuration available in this class
        self.config = SentimentAnalysisConfig()
        self.evaluation = PromptEvaluation()

    def evaluate_cross_lingual_performance(self) \
            -> None:
        self.evaluation.evaluate_prompts()

    def evaluate_language(self, language: str = 'en') \
            -> None:
        """
        Evaluates the prompts of the specified language.

        Parameters
        ----------
        language : str
            The language of the prompts to evaluate.

        Notes
        -----
        Ensure you have moved the generated chunks files in the csv data
        folder to a subfolder named "chunks_v_" + the two-digit number of
        the prompt engineering strategy it was created by (e.g. "chunks_v_01")

        """
        self.evaluation.evaluate_prompts_for_language(
            language,
            partial_metrics=['macro']
        )

    def evaluate_prompt_group(
            self,
            prompt_group: List[int],
            language: str = 'en'
    ) -> None:
        """
        Evaluates the given group of prompts in the specified language context.

        Configures the evaluation environment by setting the specified
        language and performs an evaluation on the provided group of prompts.

        Parameters
        ----------
        prompt_group : List[int]
            A list of integers representing the group of prompts to be
            evaluated.

        language : str
            The language setting for the evaluation, given as a string.
            Default is 'en'.

        Returns
        -------
        None
            This method does not return any value but outputs results to the
            console.

        """

        self.config.set('language', language)

        self.evaluation.evaluate_prompt_group(
            prompt_group
        )

    # region --- Properties

    # endregion --- Properties

    # region --- Public Methods

    # endregion --- Public Methods

    # region --- Protected Methods

    # endregion --- Protected Methods
