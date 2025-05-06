"""
cross_strategy_prompt_evaluation.py
-----------------------------------
Version 1.0, updated on 2025-01-02

"""

from typing import List, Dict

from src.sentiment_analysis.evaluation.prompt_evaluation import (
    PromptEvaluation)
from src.sentiment_analysis.chunk import Chunk
from src.sentiment_analysis.chunk_loader import ChunkLoader
from src.sentiment_analysis.prompt_engineering.prompt_engineer_factory \
    import get_prompt_engineer
from src.sentiment_analysis.query import Query
from src.sentiment_analysis.retrieval.custom_exceptions import (
    CriticalException
)
from src.utils.data_utils import is_none_or_empty
from src.utils.dict_utils import (
    convert_keys_to_consecutive_str_numbers
)
from src.utils.string_utils import StringUtils
from type_aliases import PromptsDictType


class CrossStrategyPromptEvaluation(PromptEvaluation):
    """
    CrossStrategyPromptEvaluation class.

    
    """
    
    def __init__(self):
        # Initialize data structures to manage prompts and prompt
        # ingredients

        super().__init__()

        self.overall_best_prompts: PromptsDictType = {}
        self.overall_best_prompt_ingredients_sets: List[Dict[str, str]] = []

        # Chunk-specific variables
        self.overall_chunk: Chunk = Chunk()
        self.chunk_col_map: Dict[str, str] = {}

    # region --- Properties
    
    # endregion --- Properties
    
    # region --- Public Methods

    def join_best_prompts(self, versions: List[str] | None = None) \
            -> None:
        """
        Joins the best prompts from multiple prompt set versions.

        Parameters
        ----------
        versions : List[str]
            List of versions the best prompts are to be collected from.

        Notes
        -----
        - The collected best prompts are not returned from this method but
          saved so that they can be retrieved in later runs of the program.

        - The prompt engineering and optimization having been performed on
          English samples only, the language targeted in this method is also
          English.

        """

        language = 'en'

        if is_none_or_empty(versions):
            versions = ['01', '02', '03']

        for version in versions:
            self.config.update(version=version, language=language)

            processor = self.language_results_processor

            best_query_nrs = processor.get_best_query_nrs()

            self._extract_best_prompts(best_query_nrs)
            self._extract_best_prompt_ingredients_sets(best_query_nrs)
            self._extract_to_overall_chunk(best_query_nrs)

        self._align_query_nrs()
        self._save_best_prompts()

        msg = ("Best prompts have been joined and saved. You might want to "
               f"proceed with the prompt evaluation for language {language} "
               "Do not forget to set the version to {self.version}")
        self._log(msg, 'info')


    # endregion --- Public Methods
    
    # region --- Protected Methods

    def _align_query_nrs(self) \
            -> None:
        """
        Aligns query numbers across all best prompts.

        Ensures that query numbers in the 'overall_best_prompts`
        and the corresponding columns in the 'overall_chunk' are renumbered
        consecutively. The renumbering facilitates consistency and subsequent
        analysis.

        Notes
        -----
        - Updates 'chunk_col_map' to reflect the renumbered columns.

        - Renames and reorders columns in 'overall_chunk' to match the updated
          query numbers

        """

        prompts = self.overall_best_prompts

        new_prompts: PromptsDictType = {}
        query_key_map: Dict[str, str] = {}

        counter: int = 0
        for key, val in prompts.items():
            counter += 1
            query_key_map[key] = str(counter)
            new_prompts[str(counter)] = val

            current_query_nr = str(
                StringUtils.get_int_behind_last_underscore(key)
            )
            target_query_nr = str(counter)

            self._map_overall_chunk_columns(
                current_query_nr, target_query_nr
            )
        # Use completed chunk column map to rename the overall chunk columns
        chunk = self.overall_chunk

        chunk.rename_cols(self.chunk_col_map)
        chunk.reorder_cols()

    def _map_overall_chunk_columns(
            self,
            current_query_nr: str,
            target_query_nr: str
    ) -> None:
        """
        Maps the current overall_chunk column name to a new column name.

        Adds a current column name/target column name pair to the
        chunk_col_map dictionary of this class. When completed, the dictionary
        is used to replace the current column names by the target
        column names.

        Parameters
        ----------
        current_query_nr : str
            The current query identifier appended to a "query_" or "answer_"
            column in the overall_chunk.

        target_query_nr : str
            The new query identifier by which to replace the current
            identifier to build the new column name.

        """

        col_types = ['query_', 'answer_']
        for col_type in col_types:
            target_col_name = f"{col_type}{str(target_query_nr)}"

            # Find column names that match the current column type and
            # the current query number:
            col_names = self.overall_chunk.do_with_column(
                "get_col_names_by_substring",
                substring=f"{col_type}{current_query_nr}"
            )

            if is_none_or_empty(col_names):
                raise CriticalException(
                    self.logger,
                    "No column names with substring '%s' found" %
                    current_query_nr
                )

            self._add_to_chunk_col_map(col_names, target_col_name)

    def _add_to_chunk_col_map(
            self,
            col_names: List[str],
            target_col_name: str
    ) -> None:
        """
        Adds or maps column names to a new target column name.

        Handles the renaming of columns in 'overall_chunk' by adding entries to
        'chunk_col_map' or processing duplicate column names.

        Parameters
        ----------
        col_names : List[str]
            List of current column names to be mapped.

        target_col_name : str
            New column name to which the current names will be mapped.

        Raises
        ------
        NotImplementedError
            If more than two identical query column names are encountered.

        """

        if len(col_names) == 1:
            col_name = col_names[0]
            self.chunk_col_map[col_name] = target_col_name
        elif len(col_names) == 2:
            self._handle_double_col_names_in_overall_chunk(
                col_names, target_col_name
            )
        else:
            msg = ("There are more than 2 identical query names in the "
                   "chunk. This case has not been implemented yet.")
            self._log(msg, 'error')
            raise NotImplementedError(msg)

    def _handle_double_col_names_in_overall_chunk(
            self,
            col_names: List[str],
            target_col_name: str
    ) -> None:
        """
        Resolves duplicate column names in the overall chunk.

        Handles cases where the same query appears multiple times (e.g.,
        as '_x' and '_y' suffixes) and renames or maps them accordingly. If
        unexpected cases arise, applies a fallback renaming strategy.

        Parameters
        ----------
        col_names : List[str]
            List of duplicate column names.

        target_col_name : str
            Target column name to resolve the duplicates against.

        Notes
        -----
        - Renames columns in the 'overall_chunk' DataFrame to avoid conflicts.
        - Updates 'chunk_col_map' with resolved column mappings.
        - Applies a fallback strategy for unexpected cases.

        Raises
        ------
        CriticalException
            If an unresolvable case is encountered during renaming.

        """

        fallback_suffix = "_fallback"

        for col_name in col_names:
            # Find out which query column corresponds to which query
            # variant: The column that corresponds to the current
            # variant is marked with '_x':
            if col_name.endswith('_x'):
                new_col_name = col_name.replace(
                    '_x', '')
                if new_col_name not in self.chunk_col_map:
                    self.overall_chunk.df.rename(
                        columns={col_name: new_col_name},
                        inplace=True
                    )
                    self.chunk_col_map[new_col_name] = target_col_name
                else:
                    # Handle case where the new column name already exists
                    fallback_name = new_col_name + fallback_suffix
                    self.overall_chunk.df.rename(
                        columns={col_name: fallback_name},
                        inplace=True
                    )
                    self.chunk_col_map[col_name] = target_col_name

            # Process '_y' suffix columns
            elif col_name.endswith('_y'):
                new_col_name = col_name.replace('_y', '_x')
                self.overall_chunk.df.rename(
                    columns={col_name: new_col_name},
                    inplace=True
                )

            # Fallback for unexpected cases
            else:
                # Generate a unique fallback column name
                fallback_name = f"{col_name}{fallback_suffix}"
                self.overall_chunk.df.rename(
                    columns={col_name: fallback_name},
                    inplace=True
                )
                self.chunk_col_map[fallback_name] = target_col_name
                self._log(
                    f"Unexpected column name '{col_name}' encountered. "
                    f"Renamed to '{fallback_name}' using fallback strategy.",
                    level='warning'
                )

    def _extract_best_prompt_ingredients_sets(
            self,
            best_query_nrs: List[str]
    ) -> None:

        best_prompt_ingredients_sets = [
            self.prompt_ingredients_sets.data[
                StringUtils.get_int_behind_last_underscore(query_nr) - 1
                ]
            for query_nr in best_query_nrs
        ]

        if is_none_or_empty(self.overall_best_prompt_ingredients_sets):
            self.overall_best_prompt_ingredients_sets = (
                best_prompt_ingredients_sets
            )
        else:
            self.overall_best_prompt_ingredients_sets = (
                    self.overall_best_prompt_ingredients_sets +
                    best_prompt_ingredients_sets
            )

    def _extract_best_prompts(self, best_query_nrs: List[str]) \
            -> None:
        """
        Extracts the specified best queries from all queries.

        Extracts the specified best queries from all queries and assembles
        them in the overall_best_prompts dictionary of this class.

        Parameters
        ----------
        best_query_nrs : List[str]
            List of column names of the best prompts.

        Notes
        -------
        This method does not return the extracted queries. Instead,
        it stores them in the overall_best_prompts dictionary of this
        class.

        """

        prompt_engineer = get_prompt_engineer(int(self.config.get('version')))

        all_prompts: PromptsDictType = (
            prompt_engineer.get_prompts()
        )

        best_prompts = {}

        for query_nr in best_query_nrs:
            q = Query(col_name=query_nr)
            best_prompts[q.nr_with_version] = all_prompts[
                str(q.nr)
            ]

        if is_none_or_empty(self.overall_best_prompts):
            self.overall_best_prompts = best_prompts
        else:
            self.overall_best_prompts.update(best_prompts)

        print(self.overall_best_prompts)

    def _extract_to_overall_chunk(self, best_query_nrs: List[str]) \
            -> None:
        chunk_loader = ChunkLoader(
            language='en'
        )
        chunk = chunk_loader.extract_best_queries(best_query_nrs)

        if is_none_or_empty(self.overall_chunk):
            self.overall_chunk = chunk.copy()
        else:
            # Drop columns that are not query or answer columns
            chunk.do_with_column(
                'drop_columns',
                col_names=self.non_query_cols
            )
            # Add the remaining columns to the existing overall chunk
            self.overall_chunk.do_with_column('merge', other=chunk)

    def _save_best_prompts(self) \
            -> None:

        # Get new version from last version used, augmenting it by 1 and
        # prefixing it with 0
        new_version = f"0{str(int(self.config.get('version')) + 1)}"

        # Set properties needed for saving the best prompts files
        self.config.set('version', new_version)
        file_name = ("serverless_bloom_retrieval_best_validated_queries_v_"
                     f"{new_version}")
        self.prompt_engineering = PromptEngineering(file_name=file_name)

        self._save_overall_best_prompts()
        self._save_overall_best_prompt_ingredients_sets()
        self._save_overall_chunk()

    def _save_overall_best_prompts(self) \
            -> None:
        """
        Saves the overall best prompts re-indexing the dictionary.

        Notes
        -----

        "Re-indexes" the overall_best_prompts dictionary to match the
        positional index of the elements in
        overall_best_prompt_ingredients_sets.
        The keys in the overall_best_prompts dictionary correspond to
        the index numbers + 1 in the overall_best_prompt_ingredients list.

        """

        # "Re-index" the overall_best_prompts dictionary.
        self.overall_best_prompts = (
            convert_keys_to_consecutive_str_numbers(
                self.overall_best_prompts
            )
        )

        self.prompt_engineering.data = self.overall_best_prompts
        self.prompt_engineering.save()

    def _save_overall_best_prompt_ingredients_sets(self) \
            -> None:
        """
        Saves the overall best prompt ingredients sets.

        """

        history = self.prompt_engineering.prompt_sets_history

        if not is_none_or_empty(history):
            msg = ("Prompt sets history already exists! "
                   "Overall_best_prompt_ingredients_sets does not need "
                   "saving.")
            self._log(msg, 'info')
        else:
            for el in self.overall_best_prompt_ingredients_sets:
                history.add(el)
            history.save()

    def _save_overall_chunk(self) \
            -> None:
        """
        Saves the combined chunk of best queries.

        """
        chunk = self.overall_chunk

        chunk.set_directory()
        chunk.save()

    # endregion --- Protected Methods