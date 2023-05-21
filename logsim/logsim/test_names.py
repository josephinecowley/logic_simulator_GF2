"""Test the names module."""
from names import Names
import pytest


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return Names()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Josephine", "Khalid", "Tom"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    return my_name


def test_query_raises_exceptions(used_names):
    """Test if query raises expected exceptiions."""
    with pytest.raises(TypeError):
        used_names.query(1)


def test_query_returns_name_ID(used_names):
    """Test if query returns correct ID"""
    assert used_names.query("Tom") == 2
    # Test None is returned for undefined name
    assert used_names.query("Patrick") is None


def test_lookup_raises_exceptions(used_names):
    """Test if lookup raises expected exceptiions."""
    with pytest.raises(TypeError):
        used_names.lookup("hello")
    with pytest.raises(TypeError):
        used_names.lookup(["hello", 2])


def test_lookup_appends_new_name(used_names):
    """Test if new name is correctly appended"""
    # New name is appended
    used_names.lookup(["Patrick"])
    assert used_names.get_name_string(3) == "Patrick"


def test_lookup_returns_correct_id_list(used_names):
    """Test if lookup returns the corresponding name ID list for the given name_string list."""
    # Correct ID list is returned
    assert used_names.lookup(["Khalid", "Josephine", "Tom"]) == [1, 0, 2]


def test_get_name_string_raises_exceptions(used_names):
    """Test if get_name_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_name_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_name_string("hello")
    with pytest.raises(ValueError):
        used_names.get_name_string(-1)


def test_get_name_string_returns_string(used_names):
    """Test get_name_string returns name string corresponding to ID"""
    assert used_names.get_name_string(2) == "Tom"
    # Name is absent
    assert used_names.get_name_string(4) is None
