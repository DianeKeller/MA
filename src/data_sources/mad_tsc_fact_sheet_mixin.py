"""
mad_tsc_fact_sheet_mixin.py
---------------------------
Version 1.0, validated on 2024-09-02

"""

from src.utils.print_utils import DOUBLE_LINE, SEPARATOR


class MadTscFactSheetMixin:
    """
    MadTscFactSheetMixin class.

    This class provides a description of the MadTsc data collection, and
    constants regarding its online resources and local storage location. They
    are used in the MadTscsSuite and MadTscStrategy classes.

    """

    PLATFORM = "GitHub"
    URL = "https://github.com/EvanDufraisse/MAD_TSC"

    AUTHOR = "E. Dufraisse, A. Popescu, J. Tourille, A. Brun, and J. Deshayes"
    TITLE = ("MAD-TSC: A Multilingual Aligned News Dataset for Target-"
             "dependent Sentiment Classification")
    IN = ("Proceedings of the 61st Annual Meeting of the Association for "
          "Computational Linguistics (Volume 1: Long Papers), Toronto, Canada")
    YEAR = "2024"
    PAGES = "8286-8305"
    PUBLICATION_URL = "https://aclanthology.org/2023.acl-long.461.pdf"

    DESCRIPTION = (
        f"{SEPARATOR} \n"
        f"{PLATFORM} data from {URL} \n"
        f"{DOUBLE_LINE} \n"
        f"Multilingual aligned news dataset with 5110 samples in 8 languages "
        f"(manually translated and automatically aligned) collected from "
        f"VoxEurop (https://voxeurop.eu)\n"
        f"by: \n"
        f"{AUTHOR}, '{TITLE}', \n"
        f"in {IN}, {YEAR}, pp. {PAGES}. \n"
        f"[Online]. Available: {PUBLICATION_URL}.\n"
        f"{SEPARATOR} \n")

    ORIG_DIR = "mad_tsc"
