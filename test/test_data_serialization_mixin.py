"""
test_data_serialization_mixin
"""

from src.data_sources.mad_tsc_workflow import MadTscWorkflow
from src.data_structures.my_data_frame import MyDataFrame
from src.utils.data_utils import is_none_or_empty


def test_mad_tsc_load():
    wf = MadTscWorkflow()
    wf.load_subsets()
    suite = wf.suite
    subset_names = suite.subset_names
    assert len(subset_names) == 8
    suite.load_subset(suite.subset_names[3])
    strategy = suite.use_subset(suite.subset_names[3])
    assert strategy.file_name == 'mad_tsc_fr'
    assert strategy.name == 'mad_tsc_fr'
    assert strategy.data is not None
    assert not is_none_or_empty(strategy.data)
    assert isinstance(strategy.data, MyDataFrame)

    assert strategy.n_cols == 10
    assert strategy.n_rows == 5110
