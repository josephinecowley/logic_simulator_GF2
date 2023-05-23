"""Test the names module."""
import pytest
from scanner import Scanner, Symbol
from names import Names

path = "logsim/logsim/example1_logic_description.txt"
names = Names()

@pytest.fixture
def set_scanner_location(line_number, position):
    scanner = Scanner(path, names)
    # find move the pointer to the correct line and then seek to the position
    for i, line in enumerate(scanner.file, start=1):
        if i == line_number:
            scanner.file.seek(position, 1)

    scanner.line_number = line_number
    scanner.position = position


# Test Symbol class

def test_symbol_initialization():
    symbol = Symbol()
    assert symbol.type is None
    assert symbol.id is None
    assert symbol.line_number is None
    assert symbol.end_position is None


# Test Scanner class

def test_scanner_initialisation():
    scanner = Scanner(path, names)
    assert scanner.file is not None
    assert scanner.line_number == 1
    assert scanner.position == 0
    assert scanner.names is names
    assert scanner.symbol_type_list == [scanner.BRACKET_OPEN, scanner.BRACKET_CLOSE, scanner.BRACE_OPEN, scanner.BRACE_CLOSE, scanner.COMMA, scanner.FULLSTOP, scanner.SEMICOLON, scanner.EQUALS, scanner.KEYWORD, scanner.NUMBER, scanner.NAME, scanner.EOF]
    assert scanner.keywords_list == ["DEVICES", "CONNECTIONS", "MONITORS", "END"]
    assert scanner.DEVICES_ID is not None
    assert scanner.CONNECTIONS_ID is not None
    assert scanner.MONITORS_ID is not None
    assert scanner.END_ID is not None
    assert scanner.current_character == ""


def test_scanner_open_file():
    # Test with an existing file
    scanner = Scanner(path, names)
    assert scanner.file is not None

    # Test with a non-existent file
    with pytest.raises(SystemExit):
        path = "nonexistent.txt"
        scanner = Scanner(path, names)


def test_scanner_load_scanner_data():
    scanner = Scanner(path, names)
    symbol = Symbol()
    scanner.line_number = 10
    scanner.position = 20
    scanner.load_scanner_data(symbol)
    assert symbol.line_number == 10
    assert symbol.end_position == 20

def test_scanner_advance():
    scanner = Scanner(path, names)
    position1 = scanner.position
    scanner.advance()
    assert scanner.current_character != ""
    assert scanner.position == position1 + 1


def test_scanner_skip_spaces():
    scanner = Scanner(path, names)
    set_scanner_location(1, 9) # Move scanner location to first open brace
    scanner.skip_spaces()
    assert scanner.current_character == "\n"
    set_scanner_location(2, 0) # Move scanner location to line 2 
    scanner.skip_spaces()
    assert not scanner.current_character.isspace()


def test_scanner_get_name():
    scanner = Scanner(path, names)
    set_scanner_location(1, 0)
    name = scanner.get_name()
    assert name == "DEVICES"


def test_scanner_get_number():
    scanner = Scanner(path, names)
    set_scanner_location(6, 16) # to 25
    number = scanner.get_number()
    assert number == "25"


def test_scanner_display_line_and_marker(capfd):
    scanner = Scanner(path, names)
    symbol = Symbol()
    symbol.line_number = 10
    symbol.end_position = 10
    scanner.display_line_and_marker(symbol)

    # Capture the printed output
    captured = capfd.readouterr()
    output_lines = captured.out.splitlines()

    assert output_lines[0] == "CONNECTIONS {" 
    assert output_lines[1] == "          ^  "  

