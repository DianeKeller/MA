"""
word_tokenization_regex.py
--------------------------
Version 1.0, validated on 2024-09-18

This module provides regular expressions that can be used for different
word tokenization strategies.

Functions
---------
regex_penn_treebank_wo_punctuation -> Pattern[str]
    Regex for Penn Treebank identification of words without punctuation
    marks.

"""

import re
from re import Pattern


def regex_penn_treebank_wo_punctuation():
    """
    Regex for Penn Treebank word tokenization but without including
    punctuation and similar characters.

    The Penn Treebank word tokenization rules were established by:
    Mitchell P. Marcus, Beatrice Santorini, and Mary Ann Marcinkiewicz,
    "Building a Large Annotated Corpus of English: The Penn Treebank,"
    International Conference on Computational Logic, 1993. [Online]. Available:
    <https://www.semanticscholar.org/paper/Building-a-Large-Annotated-Corpus
    -of-English%3A-The-Marcus-Santorini
    /0b44fcbeea9415d400c5f5789d6b892b6f98daff>

    Aiming at the tagging of the parts of speech in the Penn Treebank
    corpus, the authors treat punctuation, brackets, quotation marks, currency
    symbols etc., and compounds like "won't" or "children's".

    This regular expression is originally based on the Penn Treebank
    tokenization principles and taken from page 19 of:
    D. Jurafsky and J. H. Martin, Speech and Language Processing: An
    Introduction to Natural Language Processing, Computational Linguistics,
    and Speech Recognition, 2023. Accessed: Nov. 17 2023. [Online]. Available:
    https://web.stanford.edu/~jurafsky/slp3/

    It has been slightly modified for the current needs, especially by
    removing the line including punctuation, brackets and similar characters.

    Returns
    -------
    regex : Pattern[str]
        Compiled regex pattern for Penn Treebank tokenization without
        punctuation marks.

    Notes
    -----
    Explanation of the regex per line:

    [1] Set x flag to allow comments at the end of the lines.
    [2] Abbreviations, e.g. "U.S.A.".
    [3] Words with optional internal hyphens, e.g. "or-so".
    [4] Currency and percentages, e.g. "$12.40", "82%", "82 %".
    [5] Ellipsis ("...").

    """

    pattern = r'''(?x)                          # [1]
           ([A-Za-z]\.)+                        # [2]
           | \w+(-\w+)*                         # [3]
           | [€\$]?\d+(\.\d+)?\s?[%€]?          # [4]
           | \.\.\.                             # [5]
       '''

    return re.compile(pattern)
