"""Test the names module."""
import pytest
from scanner import Scanner, Symbol
from names import Names


@pytest.fixture
def path_fixture():
    return "example1_logic_description.txt"


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
        scanner = scanner_fixture  # call scanner instance

        # Reset the file pointer to the beginning of the file
        scanner.file.seek(0, 0)

        current_line_number = 1

        while not current_line_number == target_line_number:  # reads file until target line reached
            scanner.current_character = scanner.file.read(1)

            if scanner.current_character == "\n":
                current_line_number += 1

        current_position = 0

        while not current_position == target_position:  # reads file until target line reached
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
    assert scanner.keywords_list == [
        "DEVICES", "CONNECTIONS", "MONITORS", "END"]
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
    location = (6, 17)  # to '25'
    scanner = scanner_fixture
    set_scanner_location(location)
    number = scanner.get_number()
    assert number == "25"


@pytest.mark.parametrize("location, expected_line1, expected_line2", [
    ((2, 12), "        dtype1 = DTYPE; #comment contents 1",
     "               ^                           "),
    ((10, 1), "        CONNECTIONS {", "        ~~~~~~~~~~~  "),
    ((7, 19), "        data = SWITCH(0);", "                      ^  "),

])
def test_scanner_display_line_and_marker(scanner_fixture, set_scanner_location, capfd, location, expected_line1, expected_line2):
    scanner = scanner_fixture
    set_scanner_location(location)
    symbol = scanner.get_symbol()
    scanner.display_line_and_marker(symbol)

    # Capture the printed output
    captured = capfd.readouterr()
    output_lines = captured.out.splitlines()

    # call again to print out in case of error
    scanner.display_line_and_marker(symbol)
    assert output_lines[0] == expected_line1
    assert output_lines[1] == expected_line2


@pytest.mark.parametrize("location, expected_name, expected_type, expected_line_number, expected_start_position", [
    ((1, 1), "DEVICES", 8, 1, 1),
    ((10, 1), "CONNECTIONS", 8, 10, 1),
    ((20, 1), "MONITORS", 8, 21, 1),
    ((28, 1), "END", 8, 28, 1),
    ((6, 17), "25", 9, 6, 17),
    ((7, 19), "0", 9, 7, 19),
    ((2, 1), "dtype1", 10, 2, 5),
    ((11, 2), "data", 10, 11, 5),
    ((22, 12), "Q", 10, 22, 12),
])
def test_get_symbol_names(names_fixture, scanner_fixture, set_scanner_location, location, expected_name,
                          expected_type, expected_line_number, expected_start_position):
    names = names_fixture  # names class instance
    scanner = scanner_fixture
    set_scanner_location(location)
    symbol = scanner.get_symbol()
    assert isinstance(symbol.id, int)
    # check that symbol_id maps to expected name
    assert names.get_name_string(symbol.id) == expected_name
    assert symbol.type == expected_type
    assert symbol.line_number == expected_line_number
    assert symbol.start_position == expected_start_position


@pytest.mark.parametrize("location, expected_type, expected_line_number, expected_start_position", [
    ((6, 16), 0, 6, 16),
    ((6, 19), 1, 6, 19),
    ((10, 13), 2, 10, 13),
    ((26, 1), 3, 26, 1),
    ((18, 19), 5, 18, 19),
    ((2, 19), 6, 2, 19),
    ((2, 11), 7, 2, 12),
])
def test_get_symbol_punctuation(scanner_fixture, set_scanner_location, location,
                                expected_type, expected_line_number, expected_start_position):
    """self.BRACKET_OPEN, self.BRACKET_CLOSE, self.BRACE_OPEN, self.BRACE_CLOSE, self.COMMA, self.FULLSTOP, 
            self.SEMICOLON, self.EQUALS, self.KEYWORD, self.NUMBER, self.NAME, self.EOF"""
    scanner = scanner_fixture
    set_scanner_location(location)
    symbol = scanner.get_symbol()
    assert symbol.id == None  # check that symbol_ids are all None
    assert symbol.type == expected_type
    assert symbol.line_number == expected_line_number
    assert symbol.start_position == expected_start_position


@pytest.mark.parametrize("location, expected_character, expected_line_number, expected_position", [
    ((2, 21), "d", 3, 5),
    ((9, 1), "C", 10, 1),
])
def test_skip_comment(scanner_fixture, set_scanner_location, location, expected_character, expected_line_number, expected_position):
    scanner = scanner_fixture
    set_scanner_location(location)
    assert scanner.line_number == location[0]
    assert scanner.position == location[1]

    scanner.skip_comment()
    assert scanner.position == expected_position
    assert scanner.line_number == expected_line_number
    assert scanner.current_character == expected_character


def test_EOF(scanner_fixture, set_scanner_location):
    location = (28, 1)
    scanner = scanner_fixture
    set_scanner_location(location)
    symbol = scanner.get_symbol()  # call once to get END
    symbol = scanner.get_symbol()  # call again to get to EOF
    assert symbol.type == scanner.EOF
