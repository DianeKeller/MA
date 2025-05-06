def are_equal(data: T, other: T) \
        -> bool:
    """
    Generic function to check if two objects are equal.

    This singledispatch mechanism provides custom comparison functionality
    for data types that do not allow for a simple equality check with the
    '==' operator.

    Parameters
    ----------
    data : T
        The data to compare to other data

    other : T
        Other data to compare with the data

    Returns
    -------
    bool
        'True' if the data and the other data are equal. 'False' otherwise.

    Raises
    ------
    NotImplementedError
        If the data type of the provided parameters is not covered by one of
        the registered functions of this singledispatch mechanism.

    Notes
    -----
    This function defines the singledispatch mechanism that delegates the
    equality checks to the registered specialized function that covers the
    the respective type of the input values. If there is no special function
    for the data type of the input values, this function serves as a
    "catch-all" function, returning a NotImplementedError.

    """
