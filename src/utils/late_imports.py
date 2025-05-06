"""
late_imports.py
----------------------------
Version 1.0, validated on 2024-09-10

"""


class LateImports:
    """
    LateImports class.

    This class provides static methods for late imports of custom classes
    into other modules to help avoid circular imports.

    Methods
    -------
    get_my_dataframe_class() -> type
        Late import of the MyDataFrame class.

    get_my_dataframe_factory_class() -> type
        Late import of the MyDataFrameFactory class.

    def get_item_list_factory_class() -> type
        Late import of the ItemListFactory class.

    Examples
    --------

    .. code-block:: python

        # Create a MyDataFrame instance
        >>> from src.data_structures.my_dataframe_factory import \
        ... MyDataFrameFactory
        >>> from src.utils.late_imports import LateImports
        >>> from typing import cast

        # Check data type using a LateImports method.
        >>> my_df = MyDataFrameFactory.create()
        >>> if isinstance(my_df, LateImports.get_my_dataframe_class())
        >>>     do_something()

        # Execute a method that needs an input parameter of a specific late
        # import type: Cast the input parameter to the late imported type.
        >>> my_data_frame_cls = LateImports.get_my_dataframe_class()
        >>> do_something_with(cast(my_data_frame_cls, my_df).df)

    """

    @staticmethod
    def get_my_dataframe_class() \
            -> type:
        """
        Late import of the MyDataFrame class to avoid circular imports.

        Returns
        -------
        type
            The MyDataFrame class.

        """

        # pylint: disable=import-outside-toplevel
        from src.data_structures.my_data_frame import MyDataFrame
        return MyDataFrame

    @staticmethod
    def get_my_dataframe_factory_class() \
            -> type:
        """
        Late import of the MyDataFrameFactory class to avoid circular imports.

        Returns
        -------
        type
            The MyDataFrameFactory class.

        Examples
        --------

        .. code-block:: python

            # Create a MyDataFrame instance using the late imported factory:
            >>> from src.utils.late_imports import LateImports

            >>> my_dataframe_factory_cls = (
            ...     LateImports.get_my_dataframe_factory_class()
            ... )

            >>> my_df = my_dataframe_factory_cls().create(data)

        """

        # pylint: disable=import-outside-toplevel
        from src.data_structures.my_dataframe_factory import (
            MyDataFrameFactory)
        return MyDataFrameFactory

    @staticmethod
    def get_item_list_factory_class() \
            -> type:
        """
        Late import of the ItemListFactory class to avoid circular imports.

        Returns
        -------
        type
            The ItemListFactory class.

        Examples
        --------

        .. code-block:: python

            # Create an ItemList using the late imported factory:
            >>> from src.utils.late_imports import LateImports

            >>> item_list_factory_cls = LateImports.get_item_list_factory_class()
            >>> item_list = item_list_factory_cls().create(items)

        """

        # pylint: disable=import-outside-toplevel
        from src.data_structures.item_collection_factories import (
            ItemListFactory)
        return ItemListFactory
