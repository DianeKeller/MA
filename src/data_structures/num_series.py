"""
num_series.py
------------------
Version 1.0, updated on 2025-05-01

"""

import pandas as pd

from src.data_structures.item_series import ItemSeries
from type_aliases import StatsType


class NumSeries(ItemSeries):
    """
    NumSeries class.

    Class representing a pandas Series of numbers (Int64 or Float64). This
    class implements the ItemSeries class and inherits its attributes and
    methods.

    Attributes
    ----------
    elements : Series
        The elements of the Series.

    name : str
        The name of the Series.

    dev : float
        The standard deviation of the elements in the Series. Computed
        property without setter.

    max : int | float
        The maximum value in the Series. Computed property without setter.

    mean : float
        The mean of the elements in the Series. Computed property without
        setter.

    median : float
        The median of the elements in the Series. Computed property without
        setter.

    min : int | float
        The minimum value in the Series. Computed property without setter.

    stats : StatsType
        A dictionary representation of the NumSeries instance. Computed
        property without setter.

    sum : int | float
        Gets the sum of the elements in the Series. Computed property without
        setter.


    See Also
    --------
    ItemSeries
        Parent class of the present class.

    """

    def __init__(
            self,
            elements: pd.Series,
            name: str
    ):
        """
        Constructor.

        Initializes a new instance of the NumSeries class with a pandas Series
        of type Int64 or Float64.

        Parameters
        ----------
        elements : pd.Series
            The elements of the Series.

        name : str
            The name of the Series.

        """

        inferred_type = pd.api.types.infer_dtype(elements, skipna=True)

        # Decide the type based on inferred result
        if 'float' in inferred_type or 'decimal' in inferred_type:
            casted_elements = elements.astype('Float64')
        elif 'integer' in inferred_type:
            casted_elements = elements.astype('Int64')
        else:
            # Fall back to Float64 if there's any ambiguity or mixed types
            casted_elements = elements.astype('Float64')

        super().__init__(casted_elements, name)

    def __str__(self):
        """
        Returns a string representation of the NumSeries instance.
        """

        elements_preview = ', '.join(str(el) for el in self.elements.head(5))
        more_elements = '' if len(self.elements) <= 5 else ', ...'
        return (f"NumSeries '{self.name}': \n"
                f"{len(self.elements)} elements, "
                f"Min:\t{self.min} \n"
                f"Max:\t{self.max} \n"
                f"Mean:\t{self.mean} \n"
                f"Median:\t{self.median} \n"
                f"Dev:\t{self.dev} \n"
                f"Preview: [{elements_preview}{more_elements}]")

    # region --- Properties

    @property
    def max(self) \
            -> int | float:
        """
        Gets the maximum value in the Series.

        Returns
        -------
        int
            The maximum value in the Series.

        """

        return self.elements.max()

    @property
    def min(self) \
            -> int | float:
        """
        Gets the minimum value in the Series.

        Returns
        -------
        int | float
            The minimum value in the Series.

        """

        return self.elements.min()

    @property
    def sum(self) \
            -> int | float:
        """
        Gets the sum of the elements in the Series.

        Returns
        -------
        int | float
            The sum of the elements in the Series.

        """

        return self.elements.sum()

    @property
    def dev(self) \
            -> float:
        """
        Gets the standard deviation of the elements in the Series.

        Returns
        -------
        float
            The standard deviation of the elements in the Series.

        """

        return self.elements.std()

    @property
    def mean(self) \
            -> float:
        """
        Gets the mean of the elements in the Series.

        Returns
        -------
        float
            The mean of the elements in the Series.

        """

        return self.elements.mean()

    @property
    def median(self) \
            -> float:
        """
        Gets the median of the elements in the Series.

        Returns
        -------
        float
            The median of the elements in the Series.

        """

        return self.elements.median()

    @property
    def stats(self) \
            -> StatsType:
        """
        Returns a dictionary representation of the NumSeries instance.

        Returns a dictionary that can be used to build a DataFrame
        representation of the NumSeries instance.

        The dictionary includes
        - the name of the NumSeries instance
        - the number of elements in the Series
        - the minimum value of the Series
        - the maximum value of the Series
        - the mean of the values in the Series
        - the median of the values in the Series
        - the standard deviation of the values in the Series
        - if there are at most 3 unique values in the Series, the unique values

        Returns
        -------
        StatsType

            The dictionary representation of the NumSeries instance.


        """
        stats: StatsType = {
            "n_elements": self.n_elements,
            f"min_{self.name}": self.min,
            f"max_{self.name}": self.max,
            f"mean_{self.name}": self.mean,
            f"median_{self.name}": self.median,
            f"std_dev_{self.name}": self.dev,
        }

        return stats

    # endregion --- Properties
