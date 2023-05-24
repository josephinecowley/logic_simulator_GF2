"""Test the names module."""
import pytest
from scanner import Scanner, Symbol
from names import Names

@pytest.fixture
def path_fixture():
    return "logsim/logsim/example1_logic_description.txt"

@pytest.fixture
def names_fixture():
    names = Names()
    return names

@pytest.fixture
def scanner_fixture(path_fixture, names_fixture):
    return Scanner(path_fixture, names_fixture)


@pytest.fixture
def set_scanner_location(scanner_fixture):
    def _set_scanner_location(location):
        line_number, position = location
        scanner = scanner_fixture
        # Move the pointer to the correct line and then seek to the position
        for i, line in enumerate(scanner.file, start=1):
            if i == line_number:
                scanner.file.seek(position, 1)

        scanner.line_number = line_number
        scanner.position = position
        scanner.current_character = scanner.file.read(1)

    return _set_scanner_location


# Test Symbol class

def test_symbol_initialization():
    symbol = Symbol()
    assert symbol.type is None
    assert symbol.id is None
    assert symbol.line_number is None
    assert symbol.start_position is None


# Test Scanner class

def test_scanner_initialisation(scanner_fixture, names_fixture):
    scanner = scanner_fixture
    assert scanner.file is not None
    assert scanner.line_number == 1
    assert scanner.position == 0
    assert scanner.names is names_fixture
    assert scanner.symbol_type_list == range(0, 12)
    assert scanner.keywords_list == ["DEVICES", "CONNECTIONS", "MONITORS", "END"]
    assert scanner.DEVICES_ID is not None
    assert scanner.CONNECTIONS_ID is not None
    assert scanner.MONITORS_ID is not None
    assert scanner.END_ID is not None
    assert scanner.current_character == ""


def test_scanner_open_file(scanner_fixture, names_fixture):
    # Test with an existing file
    scanner = scanner_fixture
    assert scanner.file is not None

    # Test with a non-existent file
    with pytest.raises(ValueError):
        path = "nonexistent.txt"
        scanner = Scanner(path, names_fixture)


def test_scanner_load_scanner_data(scanner_fixture):
    scanner = scanner_fixture
    symbol = Symbol()
    scanner.line_number = 10
    scanner.position = 20
    scanner.load_scanner_data(symbol)
    assert symbol.line_number == 10
    assert symbol.start_position == 20

def test_scanner_advance(scanner_fixture):
    scanner = scanner_fixture
    position1 = scanner.position
    scanner.advance()
    assert scanner.current_character != ""
    assert scanner.position == position1 + 1

@pytest.mark.parametrize("location, expected_character", [
    ((1, 9), "\n"),
    ((2, 0), "d"),
])
def test_scanner_skip_spaces(scanner_fixture, set_scanner_location, location, expected_character):
    scanner = scanner_fixture
    set_scanner_location(location)
    scanner.skip_spaces()
    assert scanner.current_character == expected_character


def test_scanner_get_name(scanner_fixture, set_scanner_location):
    location = (1,0)
    scanner = scanner_fixture
    set_scanner_location(location)
    name = scanner.get_name()
    assert name == "DEVICES"


def test_scanner_get_number(scanner_fixture, set_scanner_location):
    location = (6, 16) # to '25'
    scanner = scanner_fixture
    set_scanner_location(location) 
    number = scanner.get_number()
    assert number == "25"


def test_scanner_display_line_and_marker(scanner_fixture, capfd):
    scanner = scanner_fixture
    symbol = Symbol()
    symbol.line_number = 10
    symbol.start_position = 10
    scanner.display_line_and_marker(symbol)

    # Capture the printed output
    captured = capfd.readouterr()
    output_lines = captured.out.splitlines()

    assert output_lines[0] == "CONNECTIONS {" 
    assert output_lines[1] == "          ^  "  


"""Still need to write lots of tests for get_symbol """
