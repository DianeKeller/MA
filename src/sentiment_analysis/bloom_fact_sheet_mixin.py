"""
bloom_fact_sheet_mixin.py
-------------------------
Version 1.0, updated on 2024-12-24

"""

from typing import List

from constants import Language
from src.utils.print_utils import DOUBLE_LINE, SEPARATOR


class BloomFactSheetMixin:
    """
    BloomFactSheetMixin class.

    This class provides a description of the BLOOM LLM, and
    constants regarding its online resources and local storage location. They
    are used in the ServerlessBloom class.

    """

    PLATFORM = "Hugging Face"
    SOURCE = "bigscience/bloom"
    URL = "https://huggingface.co/bigscience/bloom"
    API = "https://api-inference.huggingface.co/models/bigscience/bloom"

    AUTHOR = "BigScience Workshop: T. Le Scao et al."
    TITLE = "BLOOM: A 176B-Parameter Open-Access Multilingual Language Model"
    YEAR = "Nov. 2022"
    PUBLICATION_URL = "https://arxiv.org/abs/2211.05100v4.pdf"

    DESCRIPTION = (
        f"{SEPARATOR} \n"
        f"{PLATFORM} data from {URL} \n"
        f"{DOUBLE_LINE} \n"
        f"176B-parameter open-access language model trained on a dataset "
        f"comprising hundreds of sources in 46 natural and 13 programming "
        f"languages by: \n"
        f"{AUTHOR}, '{TITLE}', {YEAR}. \n"
        f"[Online]. Available: {PUBLICATION_URL}.\n"
        f"{SEPARATOR} \n"
        f"*** Attention: The usage of BLOOM is subject to the BigScience "
        f"RAIL License v.1.0 ("
        f"https://huggingface.co/spaces/bigscience/license)"
        f"***\n"
        f"{SEPARATOR} \n")

    # Languages the LLM understands
    AVAILABLE_LANGUAGES: List[str] = [
        Language.EN,
        Language.ES,
        Language.FR,
        Language.PT,
    ]
