"""
test_string_utils.py
"""
import pytest

from src.utils.string_utils import StringUtils


def test_convert_class_name_into_module_name():
    class_name = "TxtStrategy"
    expected_module_name = "txt_strategy"

    module_name = StringUtils.convert_class_name_into_module_name(class_name)
    assert module_name == expected_module_name


def test_convert_class_name_into_module_name_basic():
    assert (StringUtils.convert_class_name_into_module_name('TxtStrategy') ==
            'txt_strategy')
    assert (StringUtils.convert_class_name_into_module_name('MyClass') ==
            'my_class')
    assert StringUtils.convert_class_name_into_module_name(
        'TestClassName') == 'test_class_name'


def test_convert_class_name_with_numbers():
    assert (StringUtils.convert_class_name_into_module_name('MyClass1') ==
            'my_class_1')
    assert (StringUtils.convert_class_name_into_module_name('MyClassV20') ==
            'my_class_v_20')
    assert (StringUtils.convert_class_name_into_module_name(
        'Class2023Update') == 'class_2023_update')


def test_convert_class_name_with_multiple_uppercase():
    assert (StringUtils.convert_class_name_into_module_name('HTTPRequest') ==
            'http_request')
    assert (StringUtils.convert_class_name_into_module_name('JSONParser') ==
            'json_parser')
    assert (StringUtils.convert_class_name_into_module_name('IDNumber') ==
            'id_number')


def test_remove_extension_single_dot():
    assert (StringUtils.remove_extension_from_file_name("example.txt") ==
            "example")
    assert (StringUtils.remove_extension_from_file_name("document.pdf") ==
            "document")
    assert StringUtils.remove_extension_from_file_name("image.jpeg") == "image"


def test_remove_extension_multiple_dots():
    assert (StringUtils.remove_extension_from_file_name("archive.tar.gz") ==
            "archive.tar")
    assert StringUtils.remove_extension_from_file_name(
        "backup_2023.07.30.zip") == "backup_2023.07.30"
    assert StringUtils.remove_extension_from_file_name(
        "my.file.name.with.many.dots.txt") == "my.file.name.with.many.dots"


def test_remove_extension_no_dot():
    assert (StringUtils.remove_extension_from_file_name("filename") ==
            "filename")
    assert (StringUtils.remove_extension_from_file_name("document") ==
            "document")
    assert (StringUtils.remove_extension_from_file_name("examplefile") ==
            "examplefile")


def test_remove_extension_hidden_file():
    assert (StringUtils.remove_extension_from_file_name(".hiddenfile") ==
            ".hiddenfile")
    assert (StringUtils.remove_extension_from_file_name(".hiddenfile.txt") ==
            ".hiddenfile")
    assert (StringUtils.remove_extension_from_file_name(".hidden.file.txt") ==
            ".hidden.file")


def test_remove_extension_dot_at_end():
    assert (StringUtils.remove_extension_from_file_name("filename.") ==
            "filename")
    assert (StringUtils.remove_extension_from_file_name("document.") ==
            "document")


def test_remove_extension_empty_string():
    with pytest.raises(ValueError, match="File name not found or empty!"):
        StringUtils.remove_extension_from_file_name("")


def test_remove_extension_dot_only():
    with pytest.raises(
            ValueError, match="The file name cannot consist only of dots."
    ):
        StringUtils.remove_extension_from_file_name(".")
    with pytest.raises(
            ValueError, match="The file name cannot consist only of dots."
    ):
        StringUtils.remove_extension_from_file_name("..")
