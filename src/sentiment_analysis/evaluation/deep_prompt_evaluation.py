"""
deep_prompt_evaluation.py
-------------------------
Version 1.0, updated on 2025-01-10

"""

from chunk import Chunk
from typing import List, Tuple, Dict, Any

import numpy as np
import pandas as pd
from pandas import Series, DataFrame

from logger import Logger
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException)
from src.data_structures.my_data_frame import MyDataFrame
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.decorators.data_check_decorators import requires_property
from src.logging_mixin import LoggingMixin
from src.sentiment_analysis.evaluation.metrics_visualization_mixin import (
    MetricsVisualizationMixin
)
from src.sentiment_analysis.evaluation.single_prompt_evaluation import (
    SinglePromptEvaluation
)
from src.sentiment_analysis.prompt_engineering.prompt_engineer_factory \
    import get_prompt_engineer
from src.sentiment_analysis.sentiment_analysis_config import (
    SentimentAnalysisConfig
)
from src.sentiment_analysis.sentiment_stats import normalize_polarities
from src.stats.labels import Labels
from src.utils.data_comparison_utils import are_equal
from src.utils.data_utils import is_none_or_empty
from src.utils.list_utils import (
    get_second_elements_from_list_of_tuples,
    get_first_elements_from_tuple_list_by_second_element
)
from src.utils.print_utils import print_in_box
from src.utils.string_utils import StringUtils
from type_aliases import PromptsDictType

# Set Pandas display options
pd.set_option('display.max_rows', None)  # Show all rows
pd.set_option('display.max_columns', None)  # Show all columns
pd.set_option('display.width', 1000)  # Set display width
pd.set_option('display.max_colwidth', None)  # Set max column width

pd.set_option('display.float_format', '{:,.5f}'.format)
pd.options.display.float_format = '{:.4f}'.format


class DeepPromptEvaluation(MetricsVisualizationMixin, LoggingMixin):
    """
    DeepPromptEvaluation class.

    This class evaluates prompts by analyzing their components and computing
    metrics.

    """

    def __init__(
            self,
            data: MyDataFrame = None,
            language: str = "en"
    ):
        """
        Constructor.

        Initializes the DeepPromptEvaluation class with the given parameters.

        Parameters
        ----------
        data : MyDataFrame
            MyDataFrame instance containing a DataFrame with different
            query columns and the corresponding answers retrieved from the
            LLM's API. These data are needed to evaluate the quality of the
            different prompts.

        language : str
            Language code indicating the language of the sentences for which
            the queries were formulated. Defaults to English ('en').

        """

        super().__init__()

        self._encoded_prompt_ingredients = None
        self._decomposed_prompts = None
        self._n_prompts: int = 150
        self._best = None
        self._worst = None
        self._metrics: MyDataFrame | None = None
        self._all_freqs = None
        self._data = None

        # Override the default logger of the 'LoggingMixin' class.
        self.logger = Logger(self.__class__.__name__).get_logger()

        self.data = data
        self.language = language

        # Variable for the current prompt name
        self.prompt_name = ''

        self.config = SentimentAnalysisConfig()
        self.n_prompts = self.config.get('n_best_prompts')

        self.describe_data()
        self.describe_answer_data()

        self.correct_labels = Labels(self.data.df['polarity'], "correct")

        self.compute_all_prompt_metrics()
        self.add_ranks()

        # Use PromptEngineer instance to get access to the basic_ingredients
        # and the basic_and_composed_ingredients.

        ranking = self.ranking.sort_values(ascending=True)
        print(ranking)

        prompt_engineer = get_prompt_engineer(int(self.config.get("version")))

        self.prompts: PromptsDictType = (
            prompt_engineer.get_prompts()
        )

        self.basic_ingredients = prompt_engineer.get_basic_ingredients()
        self.basic_and_composed_ingredients = (
            prompt_engineer.get_basic_and_composed_ingredients()
        )

        self.composed_ingredients = (
            None
            if is_none_or_empty(self.basic_and_composed_ingredients)
            else get_second_elements_from_list_of_tuples(
                self.basic_and_composed_ingredients
            )
        )

    # region --- Properties
    @property
    def metrics(self) \
            -> MyDataFrame | None:
        """
        Returns the metrics MyDataFrame.

        Returns
        -------
        MyDataFrame
            A MyDataFrame containing a DataFrame with the metrics where the
            metrics names are column names and the query variants rows with
            metrics values.

        """

        return self._metrics

    @metrics.setter
    def metrics(self, metrics: MyDataFrame) \
            -> None:
        """
        Sets the metrics MyDataFrame.

        Parameters
        ----------
        metrics : MyDataFrame
            A MyDataFrame containing a DataFrame with the metrics where the
            metrics names are column names and the query variants rows with
            metrics values.

        """

        self._metrics = metrics

    @property
    def ranking(self) \
            -> Series:

        return self.get_ranking()

    @property
    def data(self) \
            -> Chunk:
        """
        Returns the data chunk.

        Returns
        -------
        Chunk
            The data chunk Chunk with samples, query and answer columns.

        """

        return self._data

    @data.setter
    def data(self, data: Chunk) \
            -> None:
        """
        Sets the data chunk ensuring the polarities are normalized.

        Parameters
        ----------
        data : Chunk
            Chunk with samples, query and answer columns.

        """

        data.df = normalize_polarities(data.df)
        self._data = data

    @property
    def best(self) \
            -> MyDataFrame:
        if is_none_or_empty(self._best):
            self._set_best()
        return self._best

    @best.setter
    def best(self, best: MyDataFrame) \
            -> None:

        self._best = best

    @property
    def worst(self) \
            -> MyDataFrame:
        if is_none_or_empty(self._worst):
            self._set_worst()
        return self._worst

    @worst.setter
    def worst(self, worst: MyDataFrame) \
            -> None:

        self._worst = worst

    @property
    def n_prompts(self) \
            -> int:
        """
        Returns the number of best (and worst) prompts to show.

        Returns
        ----------
        int
            The the number of best (and worst) prompts to show.

        """

        return self._n_prompts

    @n_prompts.setter
    def n_prompts(self, n_prompts: int) \
            -> None:
        """
        Sets the number of best (and worst) prompts to show.

        Parameters
        ----------
        n_prompts : int
            The the number of best (and worst) prompts to show.

        Notes
        -----
        The number of best (and worst) prompts to show normally is defined
        in the SentimentAnalysisConfig settings and used in this class to
        set the n_prompts property.

        """

        self._n_prompts = n_prompts

    @property
    def cols_to_analyze(self) \
            -> List[str]:
        """
        Retrieves all names of 'answer' columns from the data chunk.

        Returns
        -------
        List[str]
            A list of names of columns in the data chunk that constitute
            'answer' columns.

        Notes
        -----
        The name of an 'answer' column starts with "answer_" followed by a
        prompt number that corresponds to one of the numbers used to
        identify the query columns in the chunk.

        """

        return [col_name for col_name in self.data.col_names if
                col_name.startswith('answer')]

    @property
    def correct_labels(self) \
            -> Labels:
        """
        Gets the correct labels.
        """

        return self._correct_labels

    @correct_labels.setter
    def correct_labels(self, labels: Labels) \
            -> None:
        """
        Sets the correct labels.
        """

        self._correct_labels = labels

    @property
    def all_freqs(self) \
            -> Dict[str, List[Tuple[str, int]]]:
        """
        Returns the dictionary of sentiment frequencies for all prompts.

        Returns
        -------
        Dict[str, List[Tuple[str, int]]]
            A dictionary where the keys are the names of the prompts and the
            values are lists of three tuples for the three sentiment
            classes where the first element constitutes the sentiment label
            and the second element is the frequency value.

        """

        if not self._all_freqs:
            self._initialize_all_freqs()

        return self._all_freqs

    @all_freqs.setter
    def all_freqs(self, freqs: Dict[str, List[Tuple[str, int]]]):
        """
        Sets the dictionary of sentiment frequencies for all prompts.

        Parameters
        ----------
        freqs : Dict[str, List[Tuple[str, int]]]
            A dictionary where the keys are the names of the prompts and the
            values are lists of three tuples for the three sentiment
            classes where the first element constitutes the sentiment label
            and the second element is the frequ

        """

        self._all_freqs = freqs

    @property
    def all_freqs_df(self) \
            -> DataFrame:
        """
        Returns a DataFrame with the content of the all_freqs dictionary.

        Returns the DataFrame from the all_freqs_my_df MyDataFrame object
        created from the all_freqs dictionary..

        """

        return self.all_freqs_my_df.df

    @property
    def all_freqs_my_df(self) \
            -> MyDataFrame:
        """
        Creates and returns a MyDataFrame from the all_freqs dictionary.

        Returns
        -------
        MyDataFrame
            The created MyDataFrame with the content of the all_freqs
            dictionary.

        """

        return MyDataFrameFactory.create(self.all_freqs)

    @property
    def all_freqs_my_df_with_totals(self) \
            -> MyDataFrame:
        """
        Returns the all_freqs_my_df MyDataFrame with a column for the totals.

        Returns
        -------
        MyDataFrame
            The all_freqs_my_df MyDataFrame with a column for the totals added.

        """

        with_totals = self.all_freqs_my_df
        with_totals.do_with_column(
            'add_sums', col_name='total', sort=True
        )

        return with_totals

    @property
    def decomposed_prompts(self) \
            -> DataFrame:
        """
        Returns the decomposed prompts.

        Returns
        -------
        DataFrame
            The DataFrame with the decomposed prompts and their ranks.

        """

        if is_none_or_empty(self._decomposed_prompts):
            self._decompose_prompts()

        return self._decomposed_prompts

    @decomposed_prompts.setter
    def decomposed_prompts(self, decomposed_prompts: DataFrame) \
            -> None:
        """
        Sets the decomposed_prompts property.

        Parameters
        ----------
        decomposed_prompts : DataFrame
            A DataFrame with decomposed prompts.

        """

        self._decomposed_prompts = decomposed_prompts

    @property
    def encoded_prompt_ingredients(self) \
            -> DataFrame:
        """
        Returns the one-hot-encoded prompt ingredients.

        Returns
        -------
        DataFrame
            The one-hot-encoded prompt ingredients.

        """

        if is_none_or_empty(self._encoded_prompt_ingredients):
            self._encode_prompt_ingredients()

        return self._encoded_prompt_ingredients

    @encoded_prompt_ingredients.setter
    def encoded_prompt_ingredients(self, encoded_ingredients: DataFrame) \
            -> None:
        """
        Sets the one-hot-encoded prompt ingredients.

        Parameters
        ----------
        encoded_ingredients: DataFrame
            A DataFrame with one-hot-encoded prompt ingredients.

        """

        self._encoded_prompt_ingredients = encoded_ingredients

    # endregion --- Properties

    # region --- Public Methods

    def describe_answer_data(self) \
            -> None:
        """
        Describes the answer data columns with the pandas describe() function.

        Filters the DataFrame wrapped in the data MyDataFrame object for
        answer columns to the console and prints the filtered DataFrame to the
        console.

        """

        df = self.data.do_with_column(
            'extract_columns_by_name_substring',
            substring="answer_"
        )

        df_T = df.describe().T
        answer_counts = df_T[['count']]

        print(answer_counts)

    def describe_data(self) \
            -> None:
        """
        Describes the data with the pandas describe() function.

        Prints the DataFrame wrapped in the data MyDataFrame object to the
        console.

        """

        # Display DataFrame programmatically
        df = self.data.df.describe().T
        print(df)

    def compute_all_prompt_metrics(self) \
            -> None:
        """
        Computes the metrics for all columns to analyze
        Instantiates a SinglePromptEvaluation instance for each column that
        is to be analyzed and adds prompt metrics and frequencies to
        collections of metrics and frequencies for all prompts.

        Shows the overall frequencies after having added the sentiment
        frequencies for all prompts.

        """

        for col_name in self.cols_to_analyze:
            evaluation = SinglePromptEvaluation(
                self.correct_labels,
                self.data.df[col_name],
                self.language,
                col_name,
            )

            self.add_prompt_metrics(evaluation)
            self.add_prompt_freqs(evaluation)

        title = "Frequencies"
        body = self.all_freqs_my_df_with_totals

        print_in_box(title, body)

    def add_prompt_freqs(self, evaluation: SinglePromptEvaluation) \
            -> None:
        """
        Adds sentiment frequencies for a prompt to the all_freqs dictionary.

        Adds the sentiment frequencies for a prompt to the overall dictionary
        of sentiment frequencies of all prompts.

        Retrieves the frequencies for a single prompt from the
        SinglePromptEvaluation instance created for the prompt's evaluation.

        Parameters
        ----------
        evaluation : SinglePromptEvaluation
            The SinglePromptEvaluation instance created for the prompt's
            evaluation.

        """

        # Uncomment to output the comparison of frequencies of the correct
        # labels and the predicted labels in the console.

        # evaluation.compare_freqs()

        predicted_freqs = evaluation.predicted_freqs
        self.all_freqs[predicted_freqs[0]] = predicted_freqs[1]

    def add_prompt_metrics(self, evaluation: SinglePromptEvaluation) \
            -> None:
        """
        Adds computed metrics for a prompt to the overall metrics MyDataFrame.

        The overall metrics MyDataFrame collects the metrics for all prompts.

        Parameters
        ----------
        evaluation : SinglePromptEvaluation
            A SinglePromptEvaluation instance for the currently analyzed
            prompt that computes the prompt's metrics.

        """

        metrics = evaluation.compute_metrics()

        if not self._metrics:
            self.metrics = MyDataFrameFactory.create(
                metrics.values,
                name=f"{self.language}_prompt_metrics",
                index_column='info'
            )
        else:
            tmp_metrics = MyDataFrameFactory.create(
                metrics.values,
                name=f"{self.language}_prompt_metrics",
                index_column='info'
            )
            self.metrics.do_with_row(
                "add_rows",
                data=tmp_metrics,
                ignore_index=False
            )

    def metrics_are_equal(self, metric_1: str, metric_2: str) \
            -> bool:
        return are_equal(self.metrics.df[metric_1], self.metrics.df[metric_2])

    def get_partial_metrics(self, col_substring: str) \
            -> MyDataFrame:
        """
        Extracts partial metrics based on the given column name substring.

        Extracts columns from the metrics DataFrame whose column names
        contain the given substring.

        Parameters
        ----------
        col_substring : str
            The substring to match column names with.

        Returns
        -------
        MyDataFrame
            A MyDataFrame object containing the extracted columns.

        Notes
        -----
        If the columns to extract are macro metrics, the accuracy ('acc')
        column is also added to the returned MyDataFrame as it is also an
        overall metric.

        """

        my_df = MyDataFrameFactory.create(
            self.metrics.do_with_column(
                "extract_columns_by_name_substring",
                substring=col_substring
            )
        )

        # Add the accuracy to the macro metrics
        if col_substring == 'macro':
            my_df.df.insert(0, 'acc', self.metrics.df['acc'])

        # Sort by rank
        # Temporarily add the rank column and sort by it
        if 'rank' in self.metrics.col_names:
            my_df.df.insert(0, 'rank', self.metrics.df['rank'])
            my_df = my_df.sorted('rank', asc=True)

            # Remove the rank column
            my_df.df.pop('rank')

        else:
            my_df.sorted(asc=False)

        return my_df

    def add_ranks(self) \
            -> None:
        """
        Adds ranks to the metrics based on the macro metrics.

        Notes
        -----
        The metrics DataFrame is changed in place. The resulting DataFrame
        can be retrieved using the metrics getter of this class.

        """

        self.add_macro_ranks()

    def add_macro_ranks(self) \
            -> None:
        """
        Adds ranks to the metrics based on the macro metrics.

        Notes
        -----
        The metrics DataFrame is changed in place. The resulting DataFrame
        can be retrieved using the metrics getter of this class.

        """

        df = self.get_partial_metrics('macro').df
        ranks = df.rank(ascending=False)
        df['rank'] = ranks.mean(axis=1)
        df_sorted_rounded = df.sort_values(by='rank').round(5)
        print(df_sorted_rounded)
        print(df.describe().round(5))
        self.metrics.df['rank'] = ranks.mean(axis=1)

    @requires_property("metrics")
    def get_ranking(self, replace_language_prefix: bool = False) \
            -> Series:
        """
        Returns the ranking replacing the language prefix in the row index.

        Replaces the language prefix in the row names by a prefix that just
        identifies the respective prompt.

        Parameters
        ----------
        replace_language_prefix : bool
            If set to True, the prefix replacement method is called.
            Otherwise, the row names of the ranking Series remain unchanged.
            Defaults to False.

        Returns
        -------
        Series
            The ranking Series with the new index (if this is replaced) or
            the old index (if the replace_language_prefix was not set to True.

        """

        ranking = self.metrics.df['rank']

        if replace_language_prefix:
            ranking = self._replace_language_specific_index(self.ranking)

        return ranking

    def get_metrics_for_aggregation(self) \
            -> DataFrame:
        return self._replace_language_specific_index(self.metrics.df)

    def analyze_correlation(self) \
            -> None:
        """
        Analyzes the correlations between all prompt parts.

        """

        complete_matrix = self._analyze_complete_correlation()

        high_corr_matrix = self._analyze_high_correlations(
            complete_matrix, 0.7
        )

        very_high_corr_matrix = self._analyze_high_correlations(
            complete_matrix, 0.8
        )

        self._analyze_rank_correlations(complete_matrix)

    # endregion --- Public Methods

    # region --- Protected Methods
    def _analyze_complete_correlation(self) \
            -> DataFrame:
        # The correlation_matrix contains the correlations between all the
        # prompt ingredients

        # Remove trailing whitespaces from column names to avoid issues in the
        # correlation matrix
        encoded = self.encoded_prompt_ingredients.copy()
        encoded.columns = encoded.columns.str.strip()

        correlation_matrix = encoded.corr()

        tmp_corr_matrix = correlation_matrix.__deepcopy__()

        sorted_indices = tmp_corr_matrix['rank'].sort_values(
            ascending=True).index
        sorted_corr_matrix = tmp_corr_matrix.loc[
            sorted_indices, sorted_indices]

        if (sorted_corr_matrix.index.tolist() !=
                sorted_corr_matrix.columns.tolist()):
            raise CriticalException(
                self.logger,
                "The correlation matrix is not symmetric."
            )

        # The following call results in a modified correlation matrix!
        self.show_correlation_heatmap(sorted_corr_matrix)

        if (sorted_corr_matrix.index.tolist() !=
                sorted_corr_matrix.columns.tolist()):
            raise CriticalException(
                self.logger,
                "The correlation matrix is not symmetric."
            )

        return sorted_corr_matrix

    def _analyze_high_correlations(
            self,
            corr_matrix: DataFrame,
            threshold: float = 0.7
    ) -> DataFrame:
        """
        Keeps only ingredients with high absolute correlation values.

        Keeps only ingredients with absolutecorrelation values above the given
        threshold.

        Parameters
        ----------
        corr_matrix : DataFrame
            A Pandas DataFrame representing the correlation matrix.

        threshold : float
            The threshold for keeping ingredients with high correlation values.
            Defaults to 0.7.

        Returns
        -------
        DataFrame
            The reduced correlation matrix.

        """

        cols_to_keep = self._find_high_corr_rows(corr_matrix, threshold)

        if 'rank' not in cols_to_keep:
            cols_to_keep.append('rank')

        # Reduce the correlation matrix to the columns and rows with high
        # correlation values
        high_corr_matrix = corr_matrix.loc[
            cols_to_keep,
            cols_to_keep
        ]

        tmp_high_corr_matrix = high_corr_matrix.__deepcopy__()

        sorted_indices = tmp_high_corr_matrix['rank'].sort_values(
            ascending=True).index
        sorted_high_corr_matrix = tmp_high_corr_matrix.loc[
            sorted_indices, sorted_indices]

        self.show_correlation_heatmap(sorted_high_corr_matrix)
        return sorted_high_corr_matrix

    def _find_high_corr_rows(
            self,
            corr_matrix: DataFrame,
            threshold: float = 0.7
    ) -> List[str]:
        """
        Identifies rows with high correlation values (positive or negative)
        in the given correlation matrix based on the specified threshold.
        The function excludes self-correlations by masking diagonal elements
        with NaN and then checks if any value in a row exceeds the threshold
        in magnitude.

        Parameters
        ----------
        corr_matrix : DataFrame
            The correlation matrix containing pairwise correlation values. It
            is assumed to have the same index and column labels.

        threshold : float
            The threshold used to detect high correlations. Rows with any
            value above this threshold or below -threshold (ignoring
            self-correlations) will be identified. Default is 0.7.

        Returns
        -------
        List[str]
            A list of index labels corresponding to the rows in the
            correlation matrix that have at least one correlation value
            exceeding the specified threshold in magnitude.

        """

        # Exclude self-correlations setting them to NaN
        masked_matrix = corr_matrix.copy()
        np.fill_diagonal(masked_matrix.values, np.nan)

        # Identify rows where the absolute value of any correlation exceeds
        # the threshold
        high_corr_rows = masked_matrix.index[
            (masked_matrix.abs() > threshold).any(axis=1)
        ]

        return list(high_corr_rows)

    def _analyze_rank_correlations(self, corr_matrix: DataFrame) \
            -> None:
        """
        Analyzes the rank correlations for specific prefixes in the matrix.

        The method processes the input correlation matrix to extract
        correlations of all parts of the prompt with the rank, excluding
        self-correlation of the "rank" itself. It then utilizes unique
        prefixes from the correlation indices to identify structured groups
        of correlations. Finally, it sorts and visualizes the partial
        correlations for each prefix using a heatmap.

        Parameters
        ----------
        corr_matrix : DataFrame
            A Pandas DataFrame representing the correlation matrix. It must
            contain a column named 'rank', which includes the correlations
            of various prompt elements with the rank.

        Notes
        -----
        This method does not return a value; instead, it visualizes a
        heatmap for specific partial rank correlations.

        """

        # Extract only the correlation of all prompt parts with the  rank,
        # excluding the self-correlation of "rank"
        rank_correlation = corr_matrix['rank'].drop('rank')

        prefixes = StringUtils.get_unique_prefixes(Series(
            rank_correlation.index.values
        ))

        for prefix in prefixes:
            partial_rank_correlation = (
                rank_correlation[
                    rank_correlation.index.str.startswith(f"{prefix}_")
                ]
            )
            self.show_correlation_heatmap(
                partial_rank_correlation.sort_values(ascending=False)
            )

    def _set_best(self) \
            -> None:
        best = MyDataFrameFactory.create(
            self.metrics.sorted('rank').df[:self.n_prompts]
        )
        self.best = self._add_query_col(best)

    def _set_worst(self) \
            -> None:
        worst = MyDataFrameFactory.create(
            self.metrics.sorted('rank').df[-self.n_prompts:]
        )
        self.worst = self._add_query_col(worst)

    def _decompose_prompts(self) \
            -> None:
        """
        Decomposes prompts into basic ingredients.

        Sets the decomposed_prompts property.

        Notes
        -----
        This implementation supposes there is only one basic ingredient per
        prompt part.

        """

        # Extract rank column as a DataFrame from the metrics
        # MyDataFrame
        df = self.metrics.do_with_column(
            'extract_columns', col_names=['rank']
        )
        df = df.copy()

        # Iterate through the ranks
        for index, _ in df.iterrows():
            # Get the query number from the index field of the rank
            query_nr = str(StringUtils.get_int_behind_last_underscore(index))

            # Get the prompt's parts dictionary from the prompts dictionary
            prompt_parts = self.prompts[query_nr]

            # Decompose composed ingredients:

            # With each part
            for key, val in prompt_parts.items():
                # Check whether the part is in the composed_ingredients list
                if not is_none_or_empty(self.composed_ingredients) and \
                        key in self.composed_ingredients:
                    # if yes, find and add basic ingredient to the DataFrame
                    df = self._add_basic_ingredient(df, index, key, val)
                else:
                    # if no, add the part to the DataFrame
                    df.loc[index, key] = val

        # Set the decomposed_prompts property to the DataFrame with the
        # metrics and ingredients.
        self.decomposed_prompts = df

    def _add_basic_ingredient(
            self,
            df: DataFrame,
            prompt_name: str,
            prompt_part_category: str,
            prompt_part_value: str
    ) -> DataFrame:
        """
        Adds basic ingredients to the provided DataFrame.

        For the given prompt part category, adds basic ingredients variantsto
        the provided DataFrame.

        Parameters
        ----------
        df : DataFrame
            A DataFrame whose rows represent the prompts, with a rank
            column containing the rank the prompt has received, and columns
            representing basic ingredients like "before_sentence",
            "before_mention".

        prompt_name : str
            The prompt name (e.g. "en_1") indicating the row in which to add
            the ingredients derived from the prompt_part_value parameter.

        prompt_part_category : str
            Prompt part category like "before_sentence" or "question" for
            which to retrieve basic ingredients categories like
            "sentence_label", "politeness", "toward" etc.

        prompt_part_value : str
            Concrete prompt part in which to identify basic ingredients to
            insert into the DataFrame, e.g. "Can you specifiy the opinion in
            the statement targeted at the individual. \nHere is the
            statement: ".

        Returns
        -------
        DataFrame
            The DataFrame with the found basic ingredients added.

        """

        df = df.copy()

        # Get the basic ingredients categories for the given prompt part
        # category.
        basic_ingredients_categories = (
            self._get_basic_ingredients_categories_for_prompt_part_category(
                prompt_part_category
            )
        )

        # print(f"\nPrompt part category: {prompt_part_category}")
        # print (
        #   f"Basic ingredients categories: {basic_ingredients_categories}"
        # )

        # For each basic ingredients category
        for category in basic_ingredients_categories:
            found = False
            basic_category_ingredients = self.basic_ingredients[category]

            # print(f"Basic category: {category}")
            # print(f"Basic ingredients: {basic_category_ingredients}")

            for ingredient in basic_category_ingredients:
                # print (
                #   f"Ingredient: {ingredient} - in prompt part value:
                #   {ingredient in prompt_part_value}"
                # )

                if ingredient in prompt_part_value:
                    df.loc[prompt_name, category] = ingredient
                    found = True
                    # Do not look for more ingredients from the same category
                    break
                # Ensure that capitalization is not a problem
                if ingredient.lower() in prompt_part_value.lower():
                    df.loc[prompt_name, category] = ingredient.lower()
                    found = True
                    # Do not look for more ingredients from the same category
                    break

        # Return the modified DataFrame
        return df


    def _encode_prompt_ingredients(self) \
            -> None:
        """
        Applies one-hot encoding in preparation of the correlation analysis.

        The resulting encoded prompt ingredients DataFrame is stored in the
        corresponding property.

        """

        encoded = pd.get_dummies(
            self.decomposed_prompts.drop(
                'rank',
                axis=1
            )
        )

        encoded['rank'] = self.decomposed_prompts['rank']
        self.encoded_prompt_ingredients = encoded

    def _add_query_col(self, metrics: MyDataFrame) \
            -> MyDataFrame:

        for index in metrics.data.index:
            for col_name in self.data.col_names:
                if col_name == (
                        f"query_"
                        f"{StringUtils.get_int_behind_last_underscore(index)}"
                ):
                    value = self.data.do_with_field(
                        "get_field_value",
                        row_identifier=0,
                        col_identifier=col_name
                    )

                    sentence = self.data.do_with_field(
                        "get_field_value",
                        row_identifier=0,
                        col_identifier='sentence_normalized'
                    )

                    mention = self.data.do_with_field(
                        "get_field_value",
                        row_identifier=0,
                        col_identifier='mention'
                    )

                    value = value.replace(
                        sentence, "[SENTENCE]"
                    ).replace(
                        mention, "[MENTION]"
                    )

                    metrics.do_with_field(
                        "set_field_value",
                        row_identifier=index,
                        col_identifier='query',
                        value=value
                    )
        return metrics

    def _initialize_all_freqs(self) \
            -> None:
        self.all_freqs = {'correct': self.correct_labels.freqs}

    def _replace_language_specific_index(self, data: DataFrame | Series) \
            -> DataFrame | Series:
        """
        Replaces the original language-specific index in a DataFrame or Series.

        Replaces the language prefix with the overall prefix 'prompt'

        """

        prefix = 'prompt'

        if len(data.index[0]) == 4:
            data.index = [
                prefix + idx[2:] for idx in data.index
            ]

        return data

    def _verify_row_and_column_names(self, sorted_corr_matrix):
        matrix = sorted_corr_matrix

        identical = 0

        for col_name in matrix.columns:
            col_nr = matrix.columns.get_loc(col_name)
            row_name = matrix.index[col_nr]
            if row_name != col_name:
                print(f"row: _{row_name}_ vs. col: _{col_name}_")
            else:
                print(f"row = col: _{row_name}_")
                identical += 1

        print(f"Identical: {identical}")

    # endregion --- Protected Methods
    def _get_basic_ingredients_categories_for_prompt_part_category(
            self,
            prompt_part_category: str
    ) -> List[Any]:
        """
        Retrieves the basic ingredients categories for a prompt part category.

        Retrieves the basic ingredients categories from which a prompt part
        category is composed. Searches the prompt part category in the
        basic_and_composed_ingredients property and returns the
        corresponding list of basic ingredients categories.

        Parameters
        ----------
        prompt_part_category : str
            Prompt part category like "before_sentence" or "question" for
            which to retrieve basic ingredients categories like
            "sentence_label", "politeness", "toward" etc.

        Returns
        -------
        List[Any]
            The list of basic ingredients categories found for the prompt
            part category.

        """

        basic_ingredients_categories = (
            get_first_elements_from_tuple_list_by_second_element(
                self.basic_and_composed_ingredients, prompt_part_category
            )
        )

        return basic_ingredients_categories
