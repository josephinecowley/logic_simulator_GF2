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
def error_names_list(name_string_list):
    """Return a list of example names with two errors"""
    my_name = Names()
    my_name.unique_error_codes(5)
    return my_name


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = Names()
    my_name.lookup(name_string_list)
    return my_name


def test_initialisation(new_names, used_names, error_names_list):
    """Test initial values for each Names instance"""
    # New names list is empty.
    assert new_names.names_list == []
    # Name_list has 3 existing names.
    assert used_names.names_list == ["Josephine", "Khalid", "Tom"]
    # New names error code = 0.
    assert new_names.error_code_count == 0
    # Error codes = 0.
    assert error_names_list.error_code_count == 5


def test_unique_error_codes_raises_exceptions(used_names):
    """Test if unique_error_codes raises the expected exceptions"""
    with pytest.raises(TypeError):
        used_names.unique_error_codes("hello")
    with pytest.raises(TypeError):
        used_names.unique_error_codes(1.3)
    with pytest.raises(ValueError):
        used_names.unique_error_codes(-1)


def test_unique_error_codes(new_names, error_names_list):
    """Test unique_error_codes returns the expected values"""
    assert new_names.unique_error_codes(0) == range(0)
    assert new_names.unique_error_codes(5) == range(5)
    assert error_names_list.unique_error_codes(3) == range(5, 8)


def test_query_raises_exceptions(used_names):
    """Test if query raises expected exceptiions."""
    with pytest.raises(TypeError):
        used_names.query(1)
    with pytest.raises(TypeError):
        used_names.query(1.55)
    with pytest.raises(TypeError):
        used_names.query(["Josephine", "Khalid"])


@pytest.mark.parametrize("name_string, expected_id", [
    ("Josephine", 0),
    ("Khalid", 1),
    ("Tom", 2),
])
def test_query_returns_name_ID(used_names, name_string, expected_id):
    """Test if query returns correct ID"""
    assert used_names.query(name_string) == expected_id
    assert isinstance(used_names.query("Josephine"), int)
    assert used_names.query("Patrick") is None


def test_lookup_raises_exceptions(used_names):
    """Test if lookup raises expected exceptiions."""
    with pytest.raises(TypeError):
        used_names.lookup("hello")
    with pytest.raises(TypeError):
        used_names.lookup(1)
    with pytest.raises(TypeError):
        used_names.lookup(1.5)
    with pytest.raises(TypeError):
        used_names.lookup(["hello", 2])


def test_lookup_appends_new_name(used_names):
    """Test if new name is correctly appended"""
    used_names.lookup(["Patrick"])
    assert used_names.get_name_string(3) == "Patrick"


def test_lookup_returns_correct_id_list(used_names):
    """Test if lookup returns the corresponding name ID list for the given name_string list."""
    assert used_names.lookup(["Khalid", "Josephine", "Tom"]) == [1, 0, 2]
    assert used_names.lookup(["Tom"]) == [2]
    assert used_names.lookup(["Josephine", "Khalid", "Tom", "Patrick"]) == [
        0, 1, 2, 3]


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
    assert used_names.get_name_string(4) is None
