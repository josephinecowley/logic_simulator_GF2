"""Test the mynames module."""
import pytest

from mynames import MyNames


@pytest.fixture
def new_names():
    """Return a new names instance."""
    return MyNames()


@pytest.fixture
def name_string_list():
    """Return a list of example names."""
    return ["Alice", "Bob", "Eve"]


@pytest.fixture
def used_names(name_string_list):
    """Return a names instance, after three names have been added."""
    my_name = MyNames()
    for name in name_string_list:
        my_name.lookup(name)
    return my_name


def test_get_string_raises_exceptions(used_names):
    """Test if get_string raises expected exceptions."""
    with pytest.raises(TypeError):
        used_names.get_string(1.4)
    with pytest.raises(TypeError):
        used_names.get_string("hello")
    with pytest.raises(ValueError):
        used_names.get_string(-1)


def test_lookup_raises_exceptions(used_names):
    """Test if lookup raises expected exceptiions."""
    with pytest.raises(TypeError):
        used_names.lookup(1)


def test_lookup_appends_new_name(used_names):
    """Test if new name is correctly appended"""
    # New name is appended
    used_names.lookup("Patrick")
    assert used_names.get_string(3) == "Patrick"


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve"),
    (3, None)
])
def test_get_string(used_names, new_names, name_id, expected_string):
    """Test if get_string returns the expected string."""
    # Name is present
    assert used_names.get_string(name_id) == expected_string
    # Name is absent
    assert new_names.get_string(name_id) is None


@pytest.mark.parametrize("name_id, expected_string", [
    (0, "Alice"),
    (1, "Bob"),
    (2, "Eve")
])
def test_lookup_returns_correct_id(used_names, name_id, expected_string):
    """Test if lookup returns the corresponding name ID for the given name_string."""
    # Correct ID is returned
    assert used_names.lookup(expected_string) == name_id
