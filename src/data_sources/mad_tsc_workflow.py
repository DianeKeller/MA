"""
mad_tsc_workflow.py
-----------------------
Version 1.0, updated on 2025-05-01

"""

from __future__ import annotations

from typing import no_type_check, TYPE_CHECKING, List

from src.data_sources.data_source_workflow import DataSourceWorkflow
from src.data_sources.mad_tsc_strategy import MadTscStrategy
from src.data_sources.mad_tsc_suite import MadTscSuite
from src.data_sources.mentions import Mentions
from src.data_structures.str_series import StrSeries
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty
from src.utils.string_utils import StringUtils

if TYPE_CHECKING:
    from src.data_structures.my_data_frame import MyDataFrame


class MadTscWorkflow(DataSourceWorkflow):
    """
    MadTscWorkflow class.

    This class implements the DataSourceWorkflow base class. It provides easy
    access to the functionalities of the MadTscSuite and the classes
    associated with the MAD-TSC data source, facilitating the loading,
    analysis and comparison of its subsets.

    It's main functionality is the "execute" method.

    Attributes
    ----------
    POLARITY_COL_NAME : str
        Name of the column containing polarity data.

    MENTION_COL_NAME : str
        Name of the column containing mention data.

    N_SENTENCES_COL_NAME : str
        Name of the column containing the number of sentences.

    TEXT_COL_NAME : str
        Name of the column containing the normalized sentence text.

    chosen_subset : MadTscStrategy
       The currently selected subset strategy.

    mentions : Mentions
        The "mentions" column of the chosen subset, wrapped in a Mentions
        object. Computed property without setter.

    mentions_and_polarities : MyDataFrame
        The combined dataframe of mentions and polarities.

    mentions_comparison : MyDataFrame
        The comparison of mentions across the subsets. (read-only)

    n_sentences_comparison : MyDataFrame
        The comparison of the number of sentences across the subsets.

    stats : MyDataFrame
        The statistics of the MAD-TSC suite. (read-only)

    Methods
    -------
    analyze_content() -> None:
        Analyzes the MAD-TSC subsets.

    combine_subsets() -> MadTscStrategy:
        Combines all subsets in one single subset.

    combined_feature(feature: str) -> MadTscStrategy:
        Returns the specified feature extracted from the combined subsets.

    combined_split_feature(split: str, feature: str) -> MadTscStrategy:
        Returns the specified feature extracted from the combined split
        subsets.

    compute_statistics() -> None:
        Computes the complete MAD-TSC statistics.

    compare_n_sentences() -> None:
        Compares the number of sentences across the subsets and prints
        whether they are identical or differ.

    compare_mentions_freq_diagrams(languages: List[str]) -> None:
        Prints mention frequency diagrams for the specified languages.

    compare_mentions() -> None:
        Compares the mentions across the subsets and prints whether they
        are identical or differ.

    compare_polarities() -> None:
        Compares the polarities across the subsets and prints whether they
        are identical or differ.

    choose_subset(language: str = 'en') -> None:
        Sets the chosen_subset property to the specified language subset.

    execute() -> None:
        Defines and runs the operations the MAD-TSC workflow needs to execute.

    mentions_freq_diagram(min_freq: int = 2, max_n: int = 30) -> None:
        Displays a frequency diagram of the mentions based on the specified
        parameters.

    """

    POLARITY_COL_NAME: str = "polarity"
    MENTION_COL_NAME: str = "mention"
    N_SENTENCES_COL_NAME: str = "n_sentences"
    TEXT_COL_NAME: str = "sentence_normalized"

    def __init__(self) \
            -> None:
        """
        Initializes a new instance of the MadTscWorkflow class.

        """

        super().__init__(MadTscSuite())

        self._chosen_subset = MadTscStrategy()
        self._mentions_and_polarities = None
        self._n_sentences_comparison: MyDataFrame | None = None
        self._mentions_comparison: MyDataFrame | None = None

    # region --- Properties

    @property
    def chosen_subset(self) \
            -> MadTscStrategy:
        """
        Gets the currently selected subset strategy.

        If currently there is no subset strategy selected, the choose_subset
        method is called letting it set a default subset.

        """

        if is_none_or_empty(self._chosen_subset):
            msg = "Currently, no subset is chosen. Choosing default subset..."
            self._log(msg, 'info')
            self.choose_subset()
            msg = "Default subset chosen: %s" % self._chosen_subset.name
            self._log(msg, 'info')

        return self._chosen_subset

    @chosen_subset.setter
    def chosen_subset(self, value: MadTscStrategy) \
            -> None:
        """
        Sets the currently selected subset strategy.

        """

        self._chosen_subset = value

    @property
    def stats(self) \
            -> MyDataFrame:
        """
        Gets the suite's statistics.

        """

        return self.suite.stats

    @property
    def mentions(self) \
            -> Mentions:
        """
        Gets the entire "mentions" column of the chosen subset.

        Gets the entire "mentions" column of the currently chosen
        subset and returns it as a Mentions object.

        """

        subset = self.chosen_subset
        mentions = StrSeries(
            subset.get_col(self.MENTION_COL_NAME),
            f"Mentions in Subset '"
            f"{StringUtils.first_char_to_upper(self.chosen_subset.name)}'"
        )
        return Mentions(mentions)

    @property
    def mentions_comparison(self) \
            -> MyDataFrame:
        """
        Gets a MyDataFrame showing the differences between mentions.

        Gets a MyDataFrame showing the differences between mentions across
        subsets.

        If the comparison has not been previously computed, it is calculated
        by comparing the mention columns across the subsets.

        Returns
        -------
        MyDataFrame
           A dataframe showing the comparison of mentions across subsets.

        """

        if is_none_or_empty(self._mentions_comparison):
            self._mentions_comparison = self.suite.show_compare_cols(
                self.MENTION_COL_NAME
            )
        return self._mentions_comparison

    @property
    def mentions_and_polarities(self) \
            -> MyDataFrame:
        """
        Gets the mentions and polarities MyDataFrame.
        """

        if is_none_or_empty(self._mentions_and_polarities):
            raise CriticalException(
                self.logger,
                "The mentions and polarities first need to be extracted. "
                "Run the 'extract_mentions_and_polarities' method before "
                "re-trying this operation."
            )

        return self._mentions_and_polarities

    @mentions_and_polarities.setter
    def mentions_and_polarities(self, value: MyDataFrame) \
            -> None:
        """
        Sets the mentions and polarities MyDataFrame.

        Parameters
        ----------
        value : MyDataFrame
            The mentions and polarities MyDataFrame.

        """

        self._mentions_and_polarities = value

    @property
    def n_sentences_comparison(self) \
            -> MyDataFrame:
        """
        Returns the comparison of the number of sentences across the subsets.

        """

        if is_none_or_empty(self._n_sentences_comparison):
            self._n_sentences_comparison = self.suite.show_compare_cols(
                self.N_SENTENCES_COL_NAME, self.TEXT_COL_NAME
            )
        return self._n_sentences_comparison

    # endregion --- Properties

    # region --- Methods

    def combine_subsets(self) \
            -> MadTscStrategy:
        """
        Combines all subsets in one single subset.

        Returns
        -------
        MadTscStrategy
            An instance of MadTscStrategy.

        """

        return self.suite.combine_subsets()

    def combined_feature(self, feature: str) \
            -> MadTscStrategy:
        """
        Returns extracted feature columns from combined subsets.

        Extracts the specified feature from the combined subsets and returns
        the corresponding subset strategy.

        Parameters
        ----------
        feature : str
            The feature to be extracted.

        Returns
        -------
        MadTscStrategy
            An instance of MadTscStrategy.

        """

        # Set the column names for the columns that are to be extracted
        col_names = [
            f'{feature}_{lang}' for lang in self.suite.languages
        ]

        # Extract the columns
        extracted = self.suite.combined_subsets.extract_columns(
            f'_{feature}',
            col_names
        )

        # In the extracted data, rename the columns
        extracted.my_df.df.columns = self.suite.languages

        return extracted

    def combined_split_feature(self, split: str, feature: str) \
            -> MadTscStrategy:
        """
        Returns extracted feature columns from combined split subsets.
        
        Extracts the specified feature from the combined split subsets and
        returns the corresponding subset strategy.

        Parameters
        ----------
        split : str
            The split identifier for the subsets.
        
        feature : str
            The feature to be extracted.

        Returns
        -------
        MadTscStrategy
            An instance of MadTscStrategy with the extracted feature.
        
        """

        # Set the column names for the columns that are to be extracted
        col_names = [
            f'{feature}_{lang}' for lang in self.suite.languages
        ]

        # Extract the columns
        combined_split_subsets = (
            self.suite.combined_subsets.filter_by_split(split)
        )
        extracted = combined_split_subsets.extract_columns(
            f'_{feature}',
            col_names
        )

        # In the extracted data, rename the columns
        extracted.my_df.df.columns = self.suite.languages

        return extracted

    @no_type_check
    def compute_statistics(self) \
            -> None:
        """
        Computes the complete MAD-TSC statistics.

        """

        self.suite.compute_all_stats()

    def compare_n_sentences(self) \
            -> None:
        """
        Compares the number of sentences across the subsets.

        Compares the numbers of sentences across the subsets and simply
        prints whether the columns are identical or differ.

        Notes
        -----
        The numbers of sentences are expected to differ across languages
        for various reasons:

        - Translation from one language to another does not respect sentence
          boundaries as, in different languages, there might be different
          conventions as to what sentence length is acceptable for a reader
          and what information can conveniently be joined in one sentence
          and what has better be packed in a new sentence. So, one sentence
          in one language can correspond, e.g., to half a sentence in
          another language or even to several sentences in yet another
          language.

        - Punctuation marks used in abbreviations, dates, etc. may cause
          the tokenizer to incorrectly set the sentence boundaries in one
          language, whilst correctly identifying them in another
          language.

        See Also
        --------
        n_sentences_comparison : MyDataFrame
            A MyDataFrame object providing insights into how samples
            presenting different numbers of sentences across languages look
            like.

        """

        self.suite.compare_cols(self.N_SENTENCES_COL_NAME)

    def compare_mentions(self) \
            -> None:
        """
        Compares the mentions across the subsets.

        Compares the mentions across the subsets and prints whether
        the columns are identical or differ.

        Notes
        -----
        For the MAD-TSC suite, the mention columns are expected to differ
        across the subsets, due to the different character sets the
        different languages use. The same person's name may be written
        differently in different languages.

        See Also
        --------
        mentions_comparison : MyDataFrame
            A MyDataFrame object providing insights into the differences
            between mentions in the different languages.

        """

        self.suite.compare_cols(self.MENTION_COL_NAME)

    def compare_polarities(self) \
            -> None:
        """
        Compares the polarities across the subsets.

        Compares the polarities across the subsets and prints whether the
        columns are identical or differ.

        Notes
        -----
        For the MAD-TSC suite, the polority columns should be the same
        across all subsets.

        """

        self.suite.compare_cols(self.POLARITY_COL_NAME)

    def choose_subset(self, language: str = 'en') \
            -> None:
        """
        Sets the chosen_subset property.

        Selects the subset with the specified language and sets the
        "chosen_subset" property accordingly.

        Parameters
        ----------
        language : str
            The language of the subset. Defaults to 'en'.

        Notes
        -----
        The selected subset is not returned but used to set the
        chosen_subset property of this class.

        """

        self.chosen_subset = self.suite.choose_subset(language)

    def mentions_freq_diagram(self, min_freq: int = 2, max_n: int = 30) \
            -> None:
        """
        Displays a frequency diagram of the mentions.

        Parameters
        ----------
        min_freq : int
            The minimum frequency to display. Default is 2.

        max_n : int
            The maximum number of mentions to display. Default is 30.

        """

        self.mentions.frequency_diagram(
            min_freq=min_freq,
            max_n=max_n
        )

    def compare_mentions_freq_diagrams(self, languages: List[str]) \
            -> None:
        """
        Prints mention frequency diagrams for the specified languages.

        Parameters
        ----------
        languages : List [str]
            List of language codes for the languages to include in the
            comparison.

        """

        for language in languages:
            self.choose_subset(language)
            self.mentions_freq_diagram()

    def execute(self) \
            -> None:
        """
        Defines and runs the operations the MAD-TSC workflow needs to execute.

        """

        self.load_subsets()
        print(self.suite.to_string())

    def analyze_content(self) \
            -> None:
        """
        Analyzes the MAD-TSC subsets.

        """

        self.load_subsets()
        self.compare_polarities()
        # self.compare_mentions()

        languages = [
            "en",
            "es",
            "fr",
            "pt"
        ]
        self.compare_mentions_freq_diagrams(languages)

        self.compare_n_sentences()
        print(self.n_sentences_comparison)
        self.get_statistics()
        self.suite.get_sentiment_distributions(batch_size=100)

    # endregion --- Methods


if __name__ == '__main__':
    """
    Loads the MAD-TSC datasets.
    
    Usage
    -----
    From a command line in the SentimenAnalysis directory:
    
    >>> python -m src.data_sources.mad_tsc_workflow
    
    """

    wf = MadTscWorkflow()
    wf.execute()
