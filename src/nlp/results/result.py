"""
result.py
----------------------------
Version 1.0, updated on 2024-12-17

"""

from abc import ABC, abstractmethod

from src.utils.print_utils import print_sep, print_subsep, print_wline


class Result(ABC):
    """
    Result class.

    This class defines a blueprint for results printing functionality,
    requiring concrete implementations of the 'print' and
    'restrict_print_length' methods.

    """

    def __init__(self) \
            -> None:
        """
        Constructor.

        Initializes a Result instance.

        Since this is an abstract base class, instances cannot be directly
        created. Subclasses must provide concrete implementations of the
        abstract methods.

        """

        super().__init__()

    @abstractmethod
    def print(self) \
            -> None:
        """
        Abstract method for printing results.

        Subclasses must implement this method to define how results are
        printed.

        """

    @abstractmethod
    def restrict_print_length(self) \
            -> None:
        """
        Restricts the line length of the printed result.

        Abstract method that must be implemented by the subclasses.

        """


def print_mere_results(results: Result) \
        -> None:
    """
    Prints mere results without additional context.

    This function simply invokes the `print` method on the provided `Result`
    instance. If the result is None, nothing is printed.

    Parameters
    ----------
    results : Result
        The result object to be printed.

    """

    if not results:
        # do not print anything
        print('')
        return

    results.print()


def print_results(
        results: Result,
        title: str = 'Results',
        descr: object = None
) -> None:
    """
    Prints results to console.

    - Prints a title between separating lines and a description, if provided.
    - Prints the results using the print_mere_results function.
    - Prints a separator and a blank line at the end.

    Parameters
    ----------
    results : Result
        Object containing results to be printed.

    title : str
        Optional title for the printed results.

    descr : object
        Optional description for the printed results.

    """

    print_wline()
    print_sep()
    print(title)
    print_sep()

    if descr:
        print(descr)
        print_subsep()

    if results:
        print_mere_results(results)
        print_sep()
        print_wline()
