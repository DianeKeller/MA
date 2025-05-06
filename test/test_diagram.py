"""
test_diagram.py
"""

import numpy as np
import pandas as pd
import pytest

from src.stats.visualization.diagram import Diagram


def test_calculate_zipf_values():
    df = pd.DataFrame({'Frequency': [100, 50, 33]})
    expected = pd.DataFrame({'Zipf': [100, 25, 11]}, dtype=float)
    result = Diagram.calculate_zipf_values(df)
    pd.testing.assert_frame_equal(result, expected)


def test_bar_plot(mocker):
    # Mock beep so that the sound is not played
    mocker.patch('src.stats.visualization.diagram.beep')

    df = pd.DataFrame({'Frequency': [100, 50, 33]})
    diagram = Diagram()
    diagram.bar_plot(df['Frequency'], 'Frequency', 'Test Legend')


def test_bar_plot_2(mocker):
    # Mock beep so that the sound is not played
    mocker.patch('src.stats.visualization.diagram.beep')

    plt_mock = mocker.patch('src.stats.visualization.diagram.plt')
    diagram = Diagram()
    array = np.array(
        [100, 50, 33])  # Using a NumPy array directly for simplicity

    diagram.bar_plot(array, 'Frequency', 'Test Legend')

    # Directly check if plt.bar was called
    assert plt_mock.bar.called, "plt.bar was not called as expected"


@pytest.mark.parametrize("method, expected_calls", [
    ("bar_plot", ['figure', 'bar', 'legend', 'ylabel', 'xlabel', 'xticks']),
    (
            "zipf_frequency_diagram",
            [
                'xticks', 'title', 'ylabel', 'xlabel',
                'legend', 'tight_layout'
            ]
    ),
    (
            "frequency_diagram",
            [
                'xticks', 'title', 'ylabel', 'xlabel', 'legend',
                'tight_layout'
            ]
    ),
])
def test_plot_methods(mocker, method, expected_calls):
    plt_mock = mocker.patch('src.stats.visualization.diagram.plt')
    # Mock beep so that the sound is not played
    mocker.patch('src.stats.visualization.diagram.beep')

    diagram = Diagram()
    df = pd.DataFrame({'Frequency': [100, 50, 33], 'Zipf': [100, 25, 11]})

    if method == "bar_plot":
        diagram.bar_plot(
            df['Frequency'], 'Frequency', 'Test Legend'
        )

    elif method == "zipf_frequency_diagram":
        diagram.zipf_frequency_diagram(
            df, 'Frequency', 3, 'Words',
            'Test Title'
        )

    elif method == "frequency_diagram":
        diagram.simple_frequency_diagram(
            df, 'Frequency', 3, 'Test Title'
        )

    # Check if the expected pyplot functions were called
    for expected_call in expected_calls:
        assert getattr(plt_mock, expected_call).called


def test_plot_side_by_side(mocker):
    plot1 = mocker.Mock()
    plot2 = mocker.Mock()
    diagram = Diagram()
    diagram.plot_side_by_side(plot1, plot2, "Title 1", "Title 2")

    plot1.assert_called_once()
    plot2.assert_called_once()
