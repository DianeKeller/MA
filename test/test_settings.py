"""
test_settings.py
"""

import os

import pytest

from settings import get_setting, SettingCategories, DATA_ROOT, \
    get_settings_category_from_string
from src.serialization.file_extension import FileExtension


def test_csv_path():
    csv_path = get_setting(SettingCategories.CSV, 'PATH')
    assert csv_path == os.path.join(DATA_ROOT, 'csv')


def test_pkl_extension():
    pkl_extension = get_setting(SettingCategories.PKL, 'EXTENSION')
    assert isinstance(pkl_extension, FileExtension)
    assert pkl_extension.value == '.pkl'


@pytest.mark.parametrize("category", ['BAT', None])
def test_string_instead_of_category(category):
    with pytest.raises(KeyError) as err:
        get_setting(category, 'EXTENSION')
    assert str(err.value) == (
        f"'There is no category {category} in the settings.'"
    )


def test_category_does_not_exist():
    with pytest.raises(AttributeError) as err:
        get_setting(SettingCategories.BAT, 'EXTENSION')
    assert str(err.value) == (
        "type object 'SettingCategories' has no attribute 'BAT'"
    )


def test_setting_does_not_exist():
    with pytest.raises(KeyError) as err:
        get_setting(SettingCategories.JSON, 'SEPARATOR')
    assert str(err.value.args[0]) == (
        "There is no setting SEPARATOR in the setting category JSON."
    )


def test_no_setting_specified():
    with pytest.raises(TypeError) as err:
        get_setting(SettingCategories.JSON)
    assert str(err.value) == (
        "get_setting() missing 1 required positional argument: 'setting_name'"
    )


def test_no_category_specified():
    with pytest.raises(TypeError) as err:
        get_setting('SEPARATOR')
    assert str(err.value) == (
        "get_setting() missing 1 required positional argument: 'setting_name'"
    )


@pytest.mark.parametrize("category_name, expected", [
    ('csv', SettingCategories.CSV),
    ('txt', SettingCategories.TXT),
    ('log', SettingCategories.LOG),
    ('Num', SettingCategories.NUM),
    ('PKL', SettingCategories.PKL),
    ('jSon', SettingCategories.JSON),
])
def test_get_settings_category_from_string(category_name, expected):
    assert get_settings_category_from_string(category_name) == expected
