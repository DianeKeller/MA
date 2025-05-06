"""
diagram.py
---------------------
Version 1.0, updated on 2024-12-28

"""
import textwrap
from typing import Callable, List, Dict

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from pandas import DataFrame, Series

from src.sentiment_analysis.sentiment_analysis_config import \
    SentimentAnalysisConfig
from src.stats.visualization.command_line_strategy import CommandLineStrategy
from src.stats.visualization.plotter import Plotter
from src.utils.time_utils import beep


class Diagram:
    """
    This class provides diagram drawing methods for the visualization of
    statistics.

    Notes
    -----
    This class uses a DO_BEEP constant which is set at the beginning of
    the class. It is used to decide whether to play a sound or not when the
    drawing of a diagram is finished. As the statistical analysis and the
    drawing of diagrams is time-consuming, the user may wish to be
    acoustically alerted when the analysis is done. Most probably, you may
    want to set DO_BEEP to
    - False when running the programm via Jupyter Notebook
    - True when using a Python IDE or a command line.

    """

    DO_BEEP = True
    COLOR_1 = 'blue'
    COLOR_2 = 'orange'

    def __init__(self, plotter: Plotter = Plotter(CommandLineStrategy())):
        self.plotter = plotter
        self.config = SentimentAnalysisConfig()

    def diagram_beep(self) \
            -> None:
        """
        Decide whether to play a sound and act accordingly.

        Play a sound depending on the DO_BEEP setting at the beginning of the
        file.

        """

        if self.DO_BEEP:
            beep()

    def bar_plot(
            self,
            array,
            y_label: str,
            legend: str
    ) -> None:
        """
        Visualizes the array content in a bar plot.

        Parameters
        ----------
        array
            The array to be visualized.

        y_label : str
            The label for the y-axis.

        legend : str
            The label for the legend.

        """

        self.diagram_beep()

        plt.figure(figsize=(8, 6))
        plt.bar(range(array.size), array, alpha=0.5, align='center',
                label=legend)
        plt.legend()
        plt.ylabel(y_label)
        plt.xlabel('Words')
        plt.xticks(rotation=45, size=20, horizontalalignment='right')

        self.plotter.plot()

    def line_plot(
            self,
            df: DataFrame,
            title: str = '',
            y_label: str = '',
            x_label: str = '',
            thresholds: Dict[str, float] | None = None,
            invert_y_axis: bool = False
    ) -> None:
        """
        Plots a line diagram for the given DataFrame.

        If thresholds are provided, threshold lines are added with labels on
        the secondary y-axis qualifying the range of values above the threshold
        up to the next threshold.

        Parameters
        ----------
        df : DataFrame
            A DataFrame containing the data to plot.

        title : str
            Title of the diagram.

        y_label : str
            Label for the y-axis.

        x_label : str
            Label for the x-axis.

        thresholds : Dict[str, float]
            Dictionary where the keys are the labels for the area above the
            given threshold, and the values are the threshold values.

        invert_y_axis : bool
            Whether the y-axis is to be inverted. Defaults to False.

        """

        fig, ax = plt.subplots(figsize=(12, 6))

        for column in df.columns:
            ax.plot(df.index, df[column], marker='o', label=column)

        ax.set_title(title)
        ax.set_xlabel(x_label)
        ax.set_ylabel(y_label)
        ax.grid(True)

        if thresholds:
            self.add_thresholds(ax, thresholds)

        if invert_y_axis:
            ax.invert_yaxis()

        # Rotate x labels if there are too many labels
        if len(df.index) > 50:
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(), rotation=90,
                               horizontalalignment='right')
        elif len(df.index) > 15:
            ax.set_xticks(ax.get_xticks())
            ax.set_xticklabels(ax.get_xticklabels(), rotation=45,
                               horizontalalignment='right')

        if len(df.columns) > 10:
            fig.legend(
                loc='outside right upper',
                bbox_to_anchor=(1, 1),
                ncols=2
            )
        else:
            fig.legend(
                loc='outside right upper',
                bbox_to_anchor=(0.98, 0.87)
            )

        # Adjust layout
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])
        fig.subplots_adjust(bottom=0.2, top=0.85, right=0.75)

        # Show the plot
        plt.show()

        print()

    def add_thresholds(self, ax1, thresholds: Dict[str, float]) \
            -> None:

        ax2 = ax1.twinx()

        # Ensure the secondary y-axis ticks and labels are set correctly
        threshold_values = list(thresholds.values())
        threshold_keys = list(thresholds.keys())

        # Plot threshold lines on the primary axis and create corresponding
        # labels on the secondary axis
        for label, value in thresholds.items():
            ax1.axhline(y=value, color='r', linestyle='--', linewidth=0.7)

        # Set the tick positions and labels for the secondary y-axis
        ax2.set_yticks(threshold_values)
        ax2.set_yticklabels(
            [label for label in threshold_keys]
        )
        ax2.set_ylim(ax1.get_ylim())
        ax2.tick_params(axis='y', which='both', length=0)  # Hide tick marks

    def box_plot(
            self,
            df: DataFrame,
            title: str = '',
            y_label: str = '',
            x_label: str = '',
            invert_y_axis: bool = False
    ) -> None:
        _, (ax) = plt.subplots(1, 1, figsize=(12, 6))

        df.boxplot(ax=ax)

        # Setting the title and labels
        ax.set_title(title)
        ax.set_ylabel(y_label)
        ax.set_xlabel(x_label)

        # Rotating the x-axis labels
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45,
                           horizontalalignment='right')

        if invert_y_axis:
            ax.invert_yaxis()

        # Displaying the plot
        plt.tight_layout()
        self.plotter.plot()


    def heatmap_from_df(self, correlation_data: DataFrame):
        lines = len(correlation_data)
        cols = len(correlation_data.columns)

        height = lines / 1.3 if lines >= 12 else 6
        width = cols / 1.3 if cols >= 12 else 6

        plt.figure(figsize=(width, height))

        # With vmin and vmax, ensure that the range of the color scale
        # reflects the range of possible values, not the range of actual
        # values.
        # sns.heatmap(correlation_data.to_frame(), annot=True,
        #            cmap='coolwarm', vmin=-1, vmax=1)
        correlation_data.index = [textwrap.fill(label, 30) for label in
                                  correlation_data.index]

        sns.heatmap(correlation_data, annot=True,
                    cmap='coolwarm', vmin=-1, vmax=1, fmt=".2f")

        plt.yticks(rotation=0, fontsize=10)  # Make y-tick labels horizontal
        plt.xticks(fontsize=12)

        version = self.config.get('version')
        plt.title('Correlation of Prompt Parts with Rank - v%s' % version)

        # Displaying the plot
        plt.tight_layout()
        self.plotter.plot()

    def heatmap(self, correlation_data: Series):

        lines = len(correlation_data)
        height = lines / 1.3 if lines >= 12 else 6

        plt.figure(figsize=(12, height))

        # With vmin and vmax, ensure that the range of the color scale
        # reflects the range of possible values, not the range of actual
        # values.
        # sns.heatmap(correlation_data.to_frame(), annot=True,
        #            cmap='coolwarm', vmin=-1, vmax=1)
        correlation_data.index = [textwrap.fill(label, 30) for label in
                                  correlation_data.index]

        sns.heatmap(correlation_data.to_frame(), annot=True,
                    cmap='coolwarm', vmin=-1, vmax=1, fmt=".2f")

        plt.yticks(rotation=0, fontsize=10)  # Make y-tick labels horizontal
        plt.xticks(fontsize=12)

        version = self.config.get('version')
        plt.title('Correlation of Prompt Parts with Rank - v%s' % version)

        # Displaying the plot
        plt.tight_layout()
        self.plotter.plot()

    @staticmethod
    def calculate_zipf_values(df: DataFrame) \
            -> DataFrame:
        """
        Calculate target values according to Zipf's law.

        This function calculates target values according to Zipf's law. It
        takes a DataFrame as input, calculates the Zipf values based on the
        frequencies in the DataFrame, and returns a new DataFrame containing
        the calculated Zipf values.

        Parameters
        ----------
        df : DataFrame
            The DataFrame containing the frequencies.

        Returns
        -------
        zipf_values_df : DataFrame
            The DataFrame containing the target values.

        Notes
        -----
        According to Zipf's law, the frequency with wich a word is used is
        inversely proportional to its rank. The most frequent word therefore
        has a frequency of x/1, the second most frequent word a frequency of
        x/2, the third most frequent word a frequency of x/3 and so on.

        """

        zipf_values = []
        i = 1
        for value in df.values:
            zipf_values.append(int(value) / i)
            i += 1
        zipf_values_df = pd.DataFrame(zipf_values, columns=['Zipf'])

        return zipf_values_df

    def prepare_frequency_dataframe(
            self,
            df: DataFrame,
            col_name: str | None
    ) -> DataFrame:

        # If the DataFrame has only one row and the counted elements are
        # given in the columns, transpose the DataFrame and rename the
        # single column using the provided column name.
        if df.shape[0] == 1 and df.shape[1] > 1:
            df = df.T
            df.columns = [col_name]
            return df

        return df

    def zipf_frequency_diagram(
            self,
            df: DataFrame,
            col_name: str,
            n_rows: int,
            items_type,
            title: str
    ) -> None:
        """
        Generates a zipf frequency diagram.

        This function generates a zipf frequency diagram based on the given
        DataFrame and parameters. It selects the specified number of rows from
        the given column in the DataFrame, plots a bar graph, calculates Zipf
        values, plots the Zipf values on the same graph, and adds labels and
        title to the graph. Finally, it prints the graph and applies tight
        layout to the plot.

        Parameters
        ----------
        df : DataFrame
            The DataFrame containing the data.

        col_name : str
            The name of the column in the DataFrame containing the frequencies
            for the frequency diagram.

        n_rows : int
            The number of rows to select from the specified column.

        items_type : str
            The type of items in the column.

        title : str
            The title of the frequency diagram.

        """

        df = self.prepare_frequency_dataframe(df, col_name)

        df = df[col_name][:n_rows]
        ax = df.plot.bar()

        zipf_values = self.calculate_zipf_values(df)
        zipf_values.plot(ax=ax)

        plt.xticks(
            rotation=45,
            horizontalalignment='right',
            fontweight='light',
            fontsize='medium',
        )
        plt.title(title)
        plt.ylabel('Frequency')
        plt.xlabel(items_type)
        plt.legend()

        print(ax)
        plt.tight_layout()

        self.plotter.plot()

    def all_multiple_frequencies_by_prompt_diagrams(
            self,
            freqs_by_prompt: List[DataFrame],
            title: str = ''
    ) -> None:
        """
        Combines all multiple frequencies by prompt diagrams.

        Parameters
        ----------
        freqs_by_prompt: List[DataFrame]
            The list of frequency DataFrames to include as subplots.

        title : str
            The title of the entire diagram.

        """

        n_subplots = len(freqs_by_prompt)
        n_diagram_cols = 4

        # Ceiling division to get the number of rows
        n_diagram_rows = -(-n_subplots // n_diagram_cols)

        fig, axes = plt.subplots(
            n_diagram_rows,
            n_diagram_cols,
            figsize=(20, 5 * n_diagram_rows)
        )
        axes = axes.flatten()

        for i, df in enumerate(freqs_by_prompt):
            self.multiple_frequencies_by_prompt_subplot(
                df,
                axes[i],
                f"Prompt {str(i + 1)}"
            )

        # Remove any unused axes
        for i in range(n_subplots, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(title, fontsize=16)

        # Adjusting the layout to make room for the suptitle
        # using rect=[...]:
        plt.tight_layout(rect=(0, 0, 1, 0.96))
        plt.show()

    def multiple_frequencies_by_prompt_subplot(
            self,
            df: DataFrame,
            ax: plt.Axes,
            title: str = '',
    ):
        # Plot the DataFrame
        df.T.plot(kind='bar', ax=ax)

        # Customize the plot
        ax.set_title(title)
        ax.set_xlabel('Categories')
        ax.set_ylabel('Frequency')
        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(
            df.columns,
            rotation=0,
            horizontalalignment='center'
        )
        ax.legend(title='Language')

    def multiple_frequencies_by_prompt_diagram(self, df: DataFrame):
        # Plot the DataFrame
        df.T.plot(kind='bar', figsize=(10, 6))

        # Customize the plot
        plt.title('Frequency Comparison')
        plt.xlabel('Categories')
        plt.ylabel('Frequency')
        plt.xticks(rotation=0, horizontalalignment='center')
        plt.legend(title='Language')
        plt.tight_layout()

        # Show the plot
        plt.show()

    def simple_frequency_diagram(
            self,
            df: DataFrame,
            col_name: str,
            n_rows: int,
            title: str
    ) -> None:
        """
        Generate a frequency diagram for a specified column in a DataFrame.

        Parameters
        ----------
        df : DataFrame
            The DataFrame containing the data.

        col_name : str
            The column in the DataFrame containing the frequencies for the
            frequency diagram.

        n_rows : int
            The number of rows to select from the specified column.

        title : str
            The title of the frequency diagram.

        """

        df = self.prepare_frequency_dataframe(df, col_name)

        df = df[col_name][:n_rows]
        ax = df.plot.bar()

        plt.xticks(
            rotation=45,
            horizontalalignment='right',
            fontweight='light',
            fontsize='medium'
        )
        plt.title(title)
        plt.ylabel('Frequency')
        plt.xlabel('')
        plt.legend()

        # Adding frequency values over the bars
        for p in ax.patches:
            ax.annotate(
                str(int(p.get_height())),
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                xytext=(0, 10),
                textcoords='offset points'
            )

        # Adjust the y-axis to add some padding
        y_max = df.max() * 1.1
        ax.set_ylim(0, y_max)

        plt.tight_layout()
        self.plotter.plot()

    def all_pairwise_frequency_comparison_diagrams(
            self,
            df: DataFrame,
            true_col: str,
            n_rows: int,
            title: str
    ) -> None:
        """
        Combines all pairwise frequency comparison diagrams.

        Parameters
        ----------
        df
        true_col
        n_rows
        title

        Returns
        -------

        """

        # In the provided original DataFrame, the predicted columns are rows
        predicted_cols = df.index[1:]
        n_subplots = len(predicted_cols)

        n_diagram_cols = 4
        n_diagram_rows = round(n_subplots // n_diagram_cols)

        fig, axes = plt.subplots(
            n_subplots,
            n_diagram_cols,
            figsize=(20, 20 * n_diagram_rows)
        )
        axes = axes.flatten()

        for i, col in enumerate(predicted_cols):
            self.pairwise_frequency_comparison_subplot(
                df,
                true_col,
                col,
                n_rows,
                col,
                axes[i]
            )

        # Remove any unused axes
        for i in range(n_subplots, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(title, fontsize=16)

        # Adjusting the layout to make room for the suptitle
        # using rect=[...]:
        plt.tight_layout(rect=(0, 0, 1, 0.96))
        plt.show()

    def pairwise_frequency_comparison_subplot(
            self,
            df: DataFrame,
            true_col: str,
            predicted_col: str,
            n_rows: int,
            title: str,
            ax: plt.Axes
    ) -> None:
        """
        Generate a frequency comparison subplot for true and predicted values.

        Parameters
        ----------
        df : DataFrame
            The DataFrame containing the data.

        true_col : str
            The column in the DataFrame containing the true frequencies.

        predicted_col : str
            The column in the DataFrame containing the predicted frequencies.

        n_rows : int
            The number of rows to select from the specified columns.

        title : str
            The title of the frequency comparison subplot.

        ax : plt.Axes
            The axes on which to plot the subplot.

        """

        df_true = df.T[true_col][:n_rows]
        df_predicted = df.T[predicted_col][:n_rows]

        ax = df_true.plot.bar(color=self.COLOR_1, position=0, width=0.4,
                              align='center', label='True', ax=ax)
        df_predicted.plot.bar(color=self.COLOR_2, position=1, width=0.4,
                              align='center', label='Predicted', ax=ax)

        ax.set_xticks(range(len(df.columns)))
        ax.set_xticklabels(df.columns, rotation=0, ha='right')
        ax.set_title(title)
        ax.set_ylabel('Frequency')
        ax.set_xlabel('')
        ax.legend()

        self._add_values_to_bars(ax, ax.patches[:n_rows], self.COLOR_1)
        self._add_values_to_bars(ax, ax.patches[n_rows:], self.COLOR_2)

        # Adjust the y-axis to add some padding
        y_max = max(df_true.max(), df_predicted.max()) * 1.1
        ax.set_ylim(0, y_max)

    def _add_values_to_bars(self, ax, data_row, color):
        # Adding frequency values over the bars for true values
        for p in data_row:
            ax.annotate(
                str(int(p.get_height())),
                (p.get_x() + p.get_width() / 2., p.get_height()),
                ha='center', va='center',
                xytext=(0, 10),
                textcoords='offset points',
                color=color
            )

    def pairwise_frequency_comparison_diagram(
            self,
            df: DataFrame,
            true_col: str,
            predicted_col: str,
            n_rows: int,
            title: str
    ) -> None:
        """
        Generate a frequency comparison diagram for true and predicted values.

        Parameters
        ----------
        df : DataFrame
            The DataFrame containing the data.

        true_col : str
            The column in the DataFrame containing the true frequencies.

        predicted_col : str
            The column in the DataFrame containing the predicted frequencies.

        n_rows : int
            The number of rows to select from the specified columns.

        title : str
            The title of the frequency comparison diagram.

        """

        df_true = df.T[true_col][:n_rows]
        df_predicted = df.T[predicted_col][:n_rows]

        ax = df_true.plot.bar(color=self.COLOR_1, position=0, width=0.4,
                              align='center', label='True')
        df_predicted.plot.bar(color=self.COLOR_2, position=1, width=0.4,
                              align='center', label='Predicted', ax=ax)

        plt.xticks(
            rotation=45,
            horizontalalignment='right',
            fontweight='light',
            fontsize='medium'
        )
        plt.title(title)
        plt.ylabel('Frequency')
        plt.xlabel('')
        plt.legend()

        self._add_values_to_bars(ax, ax.patches[:n_rows], self.COLOR_1)
        self._add_values_to_bars(ax, ax.patches[n_rows:], self.COLOR_2)

        # Adjust the y-axis to add some padding
        y_max = max(df_true.max(), df_predicted.max()) * 1.1
        ax.set_ylim(0, y_max)

        plt.tight_layout()
        self.plotter.plot()

    def plot_side_by_side(
            self,
            plot1: Callable[[plt.Axes], None],
            plot2: Callable[[plt.Axes], None],
            title1: str,
            title2: str,
            attr='Comparison'
    ) -> None:
        """
        Plots two diagrams side-by-side.

        Parameters
        ----------
        plot1
            A function that takes a matplotlib axis and plots the
            first diagram.

        plot2
            A function that takes a matplotlib axis and plots the
            second diagram.

        title1 : str
            Title for the first diagram.

        title2 : str
            Title for the second diagram.

        attr : str
            Attribute for comparison, used as a subtitle. Default is
            'Comparison'.

        """
        fig, (_, _) = plt.subplots(1, 2, figsize=(10, 6))
        fig.suptitle(attr, fontsize=14)
        fig.subplots_adjust(top=0.85, wspace=0.3)

        # First diagram:
        ax1 = fig.add_subplot(1, 2, 1)
        ax1.set_title(title1)
        ax1.set_xlabel(attr)

        plot1(ax1)

        plt.tight_layout(rect=(0, 0, 0.8, 0.8))

        # Second diagram:
        ax2 = fig.add_subplot(1, 2, 2)
        ax2.set_title(title2)
        ax2.set_xlabel(attr)

        plot2(ax2)

        plt.tight_layout(rect=(0, 0, 0.8, 0.8))

        self.plotter.plot()
