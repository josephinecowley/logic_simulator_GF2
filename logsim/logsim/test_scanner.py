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
    def _set_scanner_location(target_location):
        target_line_number, target_position = target_location
        scanner = scanner_fixture # call scanner instance

        # Reset the file pointer to the beginning of the file
        scanner.file.seek(0, 0)

        current_line_number = 1

        while not current_line_number == target_line_number: # reads file until target line reached
            scanner.current_character = scanner.file.read(1)
            #breakpoint()
            if scanner.current_character == "\n":
                current_line_number += 1

        current_position = 0

        while not current_position == target_position: # reads file until target line reached
            scanner.current_character = scanner.file.read(1)
            current_position += 1
                    
        scanner.line_number = target_line_number
        scanner.position = target_position

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
    assert scanner.current_character == " "


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

@pytest.mark.parametrize("location, expected_character, expected_line, expected_position", [
    ((1, 9), "\n", 1, 10),
    ((3, 11), "=", 3, 12),
    ((6, 5), "l", 6, 6),
])

def test_scanner_advance(scanner_fixture, set_scanner_location, location, expected_character, expected_line, expected_position):
    # advance will never get called directly when current_symbol == \n
    scanner = scanner_fixture
    set_scanner_location(location)
    scanner.advance()
    assert scanner.current_character == expected_character
    assert scanner.line_number == expected_line
    assert scanner.position == expected_position

@pytest.mark.parametrize("location, expected_character, expected_line, expected_position", [
    ((1, 0), "D", 1, 1),
    ((1, 10), "d", 2, 5),
    ((3, 11), "=", 3, 12),
    ((6, 1), "c", 6, 5),
])
def test_scanner_skip_spaces(scanner_fixture, set_scanner_location, location, expected_character, expected_line, expected_position):
    scanner = scanner_fixture
    set_scanner_location(location)
    #breakpoint()
    scanner.skip_spaces()
    print(scanner.current_character, scanner.line_number, scanner.position)
    assert scanner.current_character == expected_character
    assert scanner.line_number == expected_line
    assert scanner.position == expected_position

@pytest.mark.parametrize("location, expected_name", [
    ((1, 1), "DEVICES"),
    ((11, 19), "DATA"),
    ((5, 5), "dtype4"),
])

def test_scanner_get_name(scanner_fixture, set_scanner_location, location, expected_name):
    scanner = scanner_fixture
    set_scanner_location(location)
    name = scanner.get_name()
    assert name == expected_name


def test_scanner_get_number(scanner_fixture, set_scanner_location):
    location = (6, 17) # to '25'
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
    assert output_lines[2] == "          ^  "  

@pytest.mark.parametrize("location, expected_name, expected_type, expected_line_number, expected_start_position", [
    ((2, 1), "dtype1", 10, 2, 5),
    ((11, 2), "data", 10, 11, 5),
    ((20, 1), "MONITORS", 8, 21, 1),
])
def test_get_symbol_names(names_fixture, scanner_fixture, set_scanner_location, location, expected_name, 
                    expected_type, expected_line_number, expected_start_position):
    names = names_fixture # names class instance
    scanner = scanner_fixture 
    set_scanner_location(location)
    symbol = scanner.get_symbol()
    assert isinstance(symbol.id, int)
    assert names.get_name_string(symbol.id) == expected_name # check that symbol_id maps to expected name
    assert symbol.type == expected_type
    assert symbol.line_number == expected_line_number
    assert symbol.start_position == expected_start_position

@pytest.mark.parametrize("location, expected_type, expected_line_number, expected_start_position", [
    ((1, 8), 2, 1, 9),
    ((18, 19), 5, 18, 19),
    ((2, 11), 7, 2, 12),
])

def test_get_symbol_punctuation(scanner_fixture, set_scanner_location, location, 
                    expected_type, expected_line_number, expected_start_position):
    scanner = scanner_fixture 
    set_scanner_location(location)
    symbol = scanner.get_symbol()
    assert symbol.id == None # check that symbol_id maps to expected name
    assert symbol.type == expected_type
    assert symbol.line_number == expected_line_number
    assert symbol.start_position == expected_start_position

def test_full(scanner_fixture, set_scanner_location):
    scanner = scanner_fixture
    set_scanner_location((26,1))
    breakpoint()
