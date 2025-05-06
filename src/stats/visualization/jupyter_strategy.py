"""
jupyter_strategy.py
"""

from src.stats.visualization.plotting_strategy import PlottingStrategy


class JupyterStrategy(PlottingStrategy):
    def plot(self):
        # In Jupyter, plots are automatically shown, so we don't need to
        # call plt.show()
        pass
