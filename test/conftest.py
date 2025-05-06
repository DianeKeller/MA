"""
Fixtures for testing.

This module contains pytest fixtures that can be used by multiple test
modules within the project.

Fixtures
--------
temp_dir
    Creates a temporary directory for use in tests that requires file system
    operations. The directory is automatically removed after the test
    completes.

csv_strategy(temp_dir)
    Provides an instance of the CsvStrategy class configured with a temporary
    directory. This fixture depends on the 'temp_dir' fixture for its setup.

Notes
-----
Fixtures are automatically detected and made available for testing by pytest.
They do not need to be explicitly imported.

Examples
--------

Using 'temp_dir' in a test function:

.. code-block:: python

    def test_some_file_operation(temp_dir):
        file_path = os.path.join(temp_dir, 'testfile.txt')
        # Perform test using the temporary directory.

Using 'csv_strategy' in a test function:

.. code-block:: python

    def test_csv_strategy_save(csv_strategy):
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        csv_strategy.save(df)add
        # Verify that the CSV file was saved correctly.

"""

import os
import shutil
import tempfile
from collections import OrderedDict
from time import sleep

import pandas as pd
import psutil
import pytest
from pandas import DataFrame

from settings import get_setting, SettingCategories
from src.data_structures.my_dataframe_factory import MyDataFrameFactory
from src.logging_mixin import LoggingMixin
from src.serialization.csv_strategy import CsvStrategy
from src.serialization.file import File
from src.serialization.json_strategy import JsonStrategy
from src.serialization.pkl_strategy import PklStrategy
from src.serialization.serialization_factory import get_serializer
from src.serialization.serializer import Serializer
from src.serialization.txt_strategy import TxtStrategy

log = LoggingMixin().log

CANNOT_INSTANTIATE_ABSTRACT_CLASS = "Can't instantiate abstract class "
MISSING_IMPLEMENTATION = " without an implementation for abstract method"


def reset_mock_serializer(mock_strategy) \
        -> Serializer:
    return get_serializer(mock_strategy.FILE_TYPE,
                          mock_strategy.file.file_name)


def are_file_handles_open(path):
    pid = os.getpid()
    proc = psutil.Process(pid)
    for item in proc.open_files():
        if path in item.path:
            return True
    return False


def is_file_open(filepath):
    try:
        with open(filepath, 'a+', os.O_EXCL):
            pass
        return False
    except OSError:
        return True


def is_file_locked(filepath: str) \
        -> bool:
    """
    Checks whether a file is locked.

    Tries to rename the file. If it succeeds, the file is not locked.

    Parameters
    ----------
    filepath : str
        The path of the file to check.

    Returns
    -------
    bool
        Whether the file is locked or not.

    """
    if not os.path.exists(filepath):
        return False
    try:
        os.rename(filepath, filepath)
        return False
    except OSError:
        msg = "File %s is locked or in use" % filepath
        log(msg)
        return True


def delayed_remove_directory(directory, attempts=5, delay=1):
    """Attempt to remove the directory with retries and delays."""

    for attempt in range(attempts):
        try:
            shutil.rmtree(directory)
            print(f"Successfully removed directory {directory}")
            break
        except PermissionError as e:
            print(
                f"Attempt {attempt + 1}: "
                f"Unable to remove directory {directory} due to {e}")
            sleep(delay)
    else:
        print(
            f"Failed to remove directory {directory} "
            f"after {attempts} attempts.")


@pytest.fixture(scope="function")
def use_fixture(request):
    return request.getfixturevalue(request.param)


@pytest.fixture(scope="function")
def isolated_datasets_cache():
    """
    Creates an isolated datasets cache directory for testing.

    Use this fixture in tests where it seems that HuggingFace caching
    of datasets affects the test results.

    """

    original_cache_dir = os.environ.get('HF_DATASETS_CACHE')
    with tempfile.TemporaryDirectory() as tmp_cache_dir:
        os.environ['HF_DATASETS_CACHE'] = tmp_cache_dir
        yield
    if original_cache_dir is not None:
        os.environ['HF_DATASETS_CACHE'] = original_cache_dir
    else:
        del os.environ['HF_DATASETS_CACHE']


@pytest.fixture(scope="function")
def temp_dir():
    """
    Provides a temporary directory for file-based tests.

    """

    directory = tempfile.mkdtemp()
    yield directory
    try:
        shutil.rmtree(directory)
    except PermissionError as err:
        if is_file_locked(directory):
            print("Problem found: locked?")
        if are_file_handles_open(directory):
            print("Problem found: open file_handles?")
        if is_file_open(directory):
            print("Problem found: open?")

        if os.path.exists(directory):
            delayed_remove_directory(directory)

        if os.path.exists(directory):
            # Known problem when the data was saved to disk.
            # The teardown will fail, even if a delay strategy is used.
            # The test must be exited and the directory must be torn down
            # afterward. Since the problem is known and caught by wrapping
            # the test in another test function, here a warning is sufficient.
            msg = "Unable to remove directory %s due to %s" % (directory, err)
            log(msg, 'warning')

    except OSError as err:
        msg = "Unable to remove directory %s due to %s" % (directory, err)
        log(msg)
        raise OSError(msg) from err
    except Exception as err:
        msg = "Unable to remove directory %s due to %s" % (directory, err)
        log(msg)
        raise Exception(msg) from err


@pytest.fixture(scope="function")
def mock_csv_file(temp_dir):
    """
    Provides a mock File object configured to use the temporary directory.

    Parameters
    ----------
    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    File
        A mock File object configured for the temporary directory.

    """

    extension = get_setting(SettingCategories.CSV, 'EXTENSION')
    file = File(file_name="test", extension=extension)
    file.path = temp_dir
    return file


@pytest.fixture(scope="function")
def mock_json_file(temp_dir):
    """
    Provides a mock File object configured to use the temporary directory.

    Parameters
    ----------
    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    File
        A mock File object configured for the temporary directory.

    """

    extension = get_setting(SettingCategories.JSON, 'EXTENSION')
    file = File(file_name="test", extension=extension)
    file.path = temp_dir
    return file


@pytest.fixture(scope="function")
def mock_pkl_file(temp_dir):
    """
    Provides a mock File object configured to use the temporary directory.

    Parameters
    ----------
    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    File
        A mock File object configured for the temporary directory.

    """

    extension = get_setting(SettingCategories.PKL, 'EXTENSION')
    file = File(file_name="test", extension=extension)
    file.path = temp_dir
    return file


@pytest.fixture(scope="function")
def mock_txt_file(temp_dir):
    """
    Provides a mock File object configured to use the temporary directory.

    Parameters
    ----------
    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    File
        A mock File object configured for the temporary directory.

    """

    extension = get_setting(SettingCategories.TXT, 'EXTENSION')
    file = File(file_name="test", extension=extension)
    file.path = temp_dir
    return file


@pytest.fixture(scope="function")
def mock_csv_strategy(mock_csv_file, temp_dir):
    """
    Provides a CsvStrategy instance targeting a temporary directory and file.

    Parameters
    ----------
    mock_csv_file : File
        A mock File object provided by the 'mock_csv_file' fixture.

    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    CsvStrategy
        An instance of CsvStrategy configured to use the mock File object.
    """
    strategy = CsvStrategy(file=mock_csv_file)
    # when initiating CsvStrategy the file path gets set to the production
    # path, so we need to re-change this here
    strategy.file.path = temp_dir
    return strategy


@pytest.fixture(scope="function")
def mock_pkl_strategy(mock_pkl_file, temp_dir):
    """
    Provides a PklStrategy instance targeting a temporary directory and file.

    Parameters
    ----------
    mock_pkl_file : File
        A mock File object provided by the 'mock_pkl_file' fixture.

    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    PklStrategy
        An instance of PklStrategy configured to use the mock File object.
    """
    strategy = PklStrategy(file=mock_pkl_file)
    # when initiating CsvStrategy the file path gets set to the production
    # path, so we need to re-change this here
    strategy.file.path = temp_dir
    return strategy


@pytest.fixture(scope="function")
def mock_txt_strategy(mock_txt_file, temp_dir):
    """
    Provides a TxtStrategy instance targeting a temporary directory and file.

    Parameters
    ----------
    mock_txt_file : File
        A mock File object provided by the 'mock_txt_file' fixture.

    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    TxtStrategy
        An instance of TxtStrategy configured to use the mock File object.
    """
    strategy = TxtStrategy(file=mock_txt_file)
    # when initiating CsvStrategy the file path gets set to the production
    # path, so we need to re-change this here
    strategy.file.path = temp_dir
    return strategy


@pytest.fixture(scope="function")
def mock_json_strategy(mock_json_file, temp_dir):
    """
    Provides a JsonStrategy instance targeting a temporary directory and file.

    Parameters
    ----------
    mock_json_file : File
        A mock File object provided by the 'mock_json_file' fixture.

    temp_dir : object
        The temporary directory to use for the file.

    Returns
    -------
    JsonStrategy
        An instance of JsonStrategy configured to use the mock File object.
    """
    strategy = JsonStrategy(file=mock_json_file)
    # when initiating CsvStrategy the file path gets set to the production
    # path, so we need to re-change this here
    strategy.file.path = temp_dir
    return strategy


@pytest.fixture(scope="function")
def my_df():
    data = {'name': ['nnn', 'lll', 'kkk'], 'url': ['nnn_url', 'lll_url',
                                                   'kkk_url']}
    mydf = MyDataFrameFactory.create(
        data)  # Assuming YourClassName is the class
    return mydf


@pytest.fixture(scope="function")
def a_num_dict():
    return {'a': 1, 'b': 2.5, 'c': 3, 'd': 4.5, 'e': 5.0, 'f': 5.5, 'g': 5.7
            }


@pytest.fixture(scope="function")
def a_dict():
    return {
        'b': "1bcd",
        'f': "3fgh",
        'e': "11def",
        'a': "2abc",
        'c': "11def",
        'd': "11def",
    }


@pytest.fixture(scope="function")
def an_empty_dict():
    return {}


@pytest.fixture(scope="function")
def an_ordered_dict():
    return OrderedDict({
        'b': "1bcd",
        'f': "3fgh",
        'e': "11def",
        'a': "2abc",
        'c': "11def",
        'd': "11def",
    })


@pytest.fixture(scope="function")
def an_ordered_dict_with_multiple_columns():
    return OrderedDict([('A', [1, 2, 3]), ('B', [4, 5, 6]), ('C', [7, 8, 9])])


@pytest.fixture(scope="function")
def an_empty_ordered_dict():
    return OrderedDict({
    })


@pytest.fixture(scope="function")
def an_empty_dataframe():
    return DataFrame({})


@pytest.fixture(scope="function")
def a_dataframe(a_dict):
    return DataFrame([a_dict])


@pytest.fixture(scope="function")
def a_statistics_dataframe():
    data1 = {
        'olympia_1_en': [0, 2, 1.008523, 1.0, [0, 1, 2], 137, 134, 81],
        'olympia_1_pt': [0, 2, 0.860274, 1.0, [0, 1, 2], 111, 162, 92]
    }
    index1 = ['min_polarity', 'max_polarity', 'mean_polarity',
              'median_polarity',
              'unique_polarity', 'n_positive', 'n_negative', 'n_neutral']
    return pd.DataFrame(data1, index=index1)


@pytest.fixture(scope="function")
def another_statistics_dataframe():
    data2 = {
        'olympia_2_en': [0, 2, 1.168794, 2.0, [0, 1, 2, None], 371, 252, 82,
                         102]
    }
    index2 = ['min_polarity', 'max_polarity', 'mean_polarity',
              'median_polarity',
              'unique_polarity', 'n_positive', 'n_negative', 'n_neutral',
              'n_none']
    return pd.DataFrame(data2, index=index2)


@pytest.fixture(scope="function")
def an_empty_mydataframe():
    return MyDataFrameFactory.create()


@pytest.fixture(scope="function")
def a_mydataframe_with_empty_data(an_empty_dict):
    return MyDataFrameFactory.create(an_empty_dict)


@pytest.fixture(scope="function")
def a_mydataframe(a_dataframe):
    return MyDataFrameFactory.create(a_dataframe)


@pytest.fixture(scope="function")
def a_simple_text():
    return ("This is a - very short but nice - little text.  "
            "It contains but 2 sentences.")


@pytest.fixture(scope="function")
def another_simple_text():
    return ("This is my little text. "
            "It contains three little sentence examples. "
            "They are pretty stupid, but still useful.")


@pytest.fixture(scope="function")
def a_text_collection_df():
    return MyDataFrameFactory.create(
        {"text": [
            "This is a test. This too.",
            "Another test.",
            "Yet: another test.",
            "Yes! ",
            "No, never",
            "Yesterday, today, tomorrow... Always ...",
            "url: www.example.com"
        ]},
        name="Test Data"
    )


@pytest.fixture(scope="function")
def a_text_collection_with_two_columns_df():
    dic = {
        "category": ["news", "not-news"],
        "text": ["This is news.", "This is not."]
    }
    return MyDataFrameFactory.create(dic, name="Test Data")


@pytest.fixture(scope="function")
def sample_text():
    return """
    This is a Sample_Text with various words of all sorts, including upper and 
    lower case characters, hyphens, numbers like 123, and underscores like 
    word_word. 
    It also contains non-word characters like different sorts of whitespace, 
    such as tabs\t, newlines\n, and multiple spaces.
    """


@pytest.fixture(scope="function")
def complex_text():
    return """
    This is a Sample_Text with various words of all sorts, including upper and 
    lower case characters, hyphens, numbers like 123, and underscores like 
    word_word. 
    It also contains non-word characters like different sorts of whitespace, 
    such as tabs\t, newlines\n, and multiple spaces.
    Además, contiene palabras en español con acentos y otros caracteres 
    especiales como: áéíóúüñ¡¿
    Il contient également des mots en français avec des accents et d'autres 
    caractères spéciaux tels que: àâçéèêëîïôœùûüÿ
    汉字/漢字 (Chinese characters) and 片假名 (Katakana) are also included in 
    this text.
    Und deutsche Äußerungen dürfen auch nicht fehlen!
    """


@pytest.fixture()
def some_sentences():
    return [
        "most likely to be __________.\nThe sentiment expressed in this "
        "sentence towards Silvio Berlusconi, on a scale",
        "'neutral'.The sentiment expressed towards the",
        "negative. The sentiment towards the word 'Socialist' is neutral, "
        "and the sentiment towards the word",
        "most likely to be…\n\nA:\n\nThe sentiment expressed in this "
        "sentence towards José Manuel Barroso, on",
        "positive, while the sentiment towards Stefanos Marguaritis is "
        "neutral",
        "negative (-3). In fact, the sentence is a direct attack on Guy "
        "Abeille, and the"

    ]
