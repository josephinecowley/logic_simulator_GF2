"""Test the parser class"""

from names import Names
from scanner import Scanner, Symbol
from parse import Parser
import pytest


@pytest.fixture
def path_fixture():
    return "example1_logic_description.txt"


@pytest.fixture
def names_fixture():
    names = Names()
    return names


@pytest.fixture
def scanner_fixture(path_fixture, names_fixture):
    scanner = Scanner(path_fixture, names_fixture)
    return scanner


@pytest.fixture
def parser_fixture(names_fixture, scanner_fixture):
    """Return a new parser instance"""
    return Parser(names_fixture, scanner_fixture)


def test_parser_initialisation(parser_fixture, names_fixture, scanner_fixture):
    parser = parser_fixture
    assert parser.names is names_fixture
    assert parser.scanner is scanner_fixture
    assert parser.error_count == 0

    # KO! Need to add check for list of syntax error once JC has changed it to a dictionary


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
            if scanner.current_character == "\n":
                current_line_number += 1

        current_position = 0

        while not current_position == target_position: # reads file until target line reached
            scanner.current_character = scanner.file.read(1)
            current_position += 1
                    
        scanner.line_number = target_line_number
        scanner.position = target_position

    return _set_scanner_location


@pytest.fixture
def symbol_fixture(scanner_fixture, set_scanner_location):
    scanner = scanner_fixture
    set_scanner_location((2, 5))
    symbol = scanner.get_symbol()

    return symbol


'''@pytest.mark.parametrize("symbol, error_type, proceed, stopping_symbol_types", [
    ("=", 4, True, [2, 3, 6, 8]),
])
def test_parser_display_error(parser_fixture, symbol, error_type, proceed, stopping_symbol_types):
    parser = parser_fixture

    with pytest.raises(TypeError):
        parser.display_error(symbol, "non-integer error_type")
    with  pytest.raises(ValueError):
        parser.display_error(symbol, 22)
    with  pytest.raises(ValueError):
        parser.display_error(symbol, 100)
    with  pytest.raises(ValueError):
        parser.display_error(symbol, -1)
    with  pytest.raises(TypeError):
        parser.display_error(symbol, error_type)'''

@pytest.fixture
def correct_error_arguments(symbol_fixture):
    symbol = symbol_fixture
    return symbol, 4, True, [2, 3, 6, 8]

def test_parser_display_error_instance_handling(parser_fixture, correct_error_arguments):
    parser = parser_fixture
    symbol, error_type, proceed, stopping_symbol_types = correct_error_arguments

    with pytest.raises(TypeError):
        parser.display_error(symbol, "non-integer error_type") # Expected error_type to be an integer type argument
    with pytest.raises(ValueError):
        parser.display_error(symbol, 22) # Expected an error code within range of error types
    with pytest.raises(ValueError):
        parser.display_error(symbol, 100) # Expected an error code within range of error types
    with pytest.raises(ValueError):
        parser.display_error(symbol, -1) # Cannot have a negative error code
    with pytest.raises(TypeError):
        parser.display_error("not an instance of Symbol class", error_type) # Expected an instance of the Symbol class
    with pytest.raises(TypeError):
        parser.display_error(symbol, error_type, proceed, "not a list") # Expected stopping symbol to be an integer type argument
    with pytest.raises(ValueError):
        parser.display_error(symbol, error_type, proceed, list(range(12))) # Expected stopping symbol to be within range of given symbols
    with pytest.raises(ValueError):
        parser.display_error(symbol, error_type, proceed, list(range(32))) # Expected stopping symbol to be within range of given symbols
    with pytest.raises(ValueError):
        parser.display_error(symbol, error_type, proceed, list(range(0))) # Expected stopping symbol to be within range of given symbols
    with pytest.raises(ValueError):
        parser.display_error(symbol, error_type, proceed, list(range(-8))) # Expected stopping symbol to be within range of given symbols


def test_parser_display_error_error_count_increment(parser_fixture, correct_error_arguments):
    parser = parser_fixture
    parser.display_error(*correct_error_arguments)

    assert parser.error_count == 1

@pytest.mark.parametrize(", error_type, proceed, stopping_symbol_types", [
    ("=", 4, True, [2, 3, 6, 8]),
])
def test_parser_display_error_show_error_messages(parser_fixture, correct_error_arguments, capfd):
    parser = parser_fixture
    symbol, error_type, proceed, stopping_symbol_types = correct_error_arguments



    captured = capfd.outererr()


'''@pytest.mark.parametrize("error_type, expected_error_message", [
    (4, "Syntax Error: Expected the keyword DEVICES"),
])
def test_parser_display_error_type_of_error(parser_fixture, correct_error_arguments):
    parser = parser_fixture
    symbol, error_type, proceed, stopping_symbol_types = correct_error_arguments
    assert parser.display_error(symbol, error_type, proceed, stopping_symbol_types) == "Line 2: Syntax Error: Expected a '{' sign"'''


def test_parser_display_error_valid_error_code(parser_fixture, correct_error_arguments):
    parser = parser_fixture
    symbol, error_type, proceed, stopping_symbol_types = correct_error_arguments
    invalid_error_type = max(parser.syntax_errors) + 1

    with pytest.raises(ValueError):
        parser.display_error(symbol, invalid_error_type, proceed, stopping_symbol_types)


def test_error_recovery_instance_handling(parser_fixture, correct_error_arguments):
    parser = parser_fixture
    symbol, error_type, proceed, stopping_symbol_types = correct_error_arguments

    with pytest.raises(TypeError):
        parser.error_recovery("not an integer") # Expected error_type to be an integer type argument
    with pytest.raises(ValueError):
        parser.error_recovery(len(parser.syntax_errors)) # Expected an error code within range of error types
    with pytest.raises(ValueError):
        parser.error_recovery(len(parser.syntax_errors) + 10) # Expected an error code within range of error types
    with pytest.raises(ValueError):
        parser.error_recovery(-4) # Cannot have a negative error code
    with pytest.raises(TypeError):
        parser.error_recovery(error_type, "not a boolean") # Expected bool type argument for proceed
    with pytest.raises(TypeError):
        parser.error_recovery(error_type, proceed, "not a list") # Expected stopping symbol to be an integer type argument
    with pytest.raises(ValueError):
        parser.error_recovery(error_type, proceed, list(range(12))) # Expected stopping symbol to be within range of given symbols
    with pytest.raises(ValueError):
        parser.error_recovery(error_type, proceed, list(range(32))) # Expected stopping symbol to be within range of given symbols
    with pytest.raises(ValueError):
        parser.error_recovery(error_type, proceed, list(range(0))) # Expected stopping symbol to be within range of given symbols
    with pytest.raises(ValueError):
        parser.error_recovery(error_type, proceed, list(range(-8))) # Expected stopping symbol to be within range of given symbols


def test_error_recovery_check_built_in_error_handling(parser_fixture, correct_error_arguments, capfd):
    parser = parser_fixture
    symbol, error_type, proceed, stopping_symbol_types = correct_error_arguments

    proceed = True
    assert parser.error_recovery(error_type, proceed, stopping_symbol_types) is None # KO! May need to check this again once parse.py is complete