"""Test the parser class"""
import pytest
import os

from names import Names
from devices import Devices, Device
from network import Network
from monitors import Monitors
from scanner import Scanner, Symbol
from parse import Parser


@pytest.fixture
def path_fixture():
    """Return logic description file 1 fixture"""
    return "example1_logic_description.txt"


@pytest.fixture
def names_fixture():
    """Return names instance fixture"""
    return Names()


@pytest.fixture
def devices_fixture(names_fixture):
    """Return devices instance fixture"""
    return Devices(names_fixture)


@pytest.fixture
def network_fixture(names_fixture, devices_fixture):
    """Return networks instance fixture"""
    return Network(names_fixture, devices_fixture)


@pytest.fixture
def monitors_fixture(names_fixture, devices_fixture, network_fixture):
    """Return monitors instance fixture"""
    return Monitors(names_fixture, devices_fixture, network_fixture)


@pytest.fixture
def create_testing_file_to_scan(names_fixture):
    """This is an in-house helper function not strictly related to testing parse.py"""
    def _create_testing_file(testing_example, scan_through_all=False):
        with open("testing_file.txt", "w") as file:
            # by structure, this will always create testing_file.txt within this directory
            file_path = file.name
            file.write(testing_example)

        scanner = Scanner(file_path, names_fixture)

        if scan_through_all:
            while scanner.current_character != "":
                scanner.get_symbol()

        return scanner
    return _create_testing_file


def test_create_testing_file_to_scan(create_testing_file_to_scan):
    """This is an in-house helper function not strictly related to testing parse.py"""
    scanner = create_testing_file_to_scan(
        """
    DEVICES {
        dtype1 = DTYPE;
        dtype2 = DTYPE;
        dtype3 = DTYPE;
        dtype4 = DTYPE;
        clock = CLK(25);
        data = SWITCH(0);
    }
    """, scan_through_all=True)

    assert scanner.names.names_list == ['DEVICES', 'CONNECTIONS', 'MONITORS', 'END', 'dtype1', 'DTYPE', 'dtype2',
                                        'dtype3', 'dtype4', 'clock', 'CLK', '25', 'data', 'SWITCH', '0']


@pytest.fixture
def scanner_fixture(create_testing_file_to_scan):
    def _scanner_fixture(scan_through_all=True):
        scanner = create_testing_file_to_scan(
            """
        DEVICES {
            dtype1 = DTYPE;
            dtype2 = DTYPE;
            dtype3 = DTYPE;
            dtype4 = DTYPE;
            clock = CLK(25);
            data = SWITCH(0);
        }

        CONNECTIONS {
            dtype1.DATA = data;
            dtype1.SET = set;
            dtype1.CLEAR = set;
            dtype1.CLK = clock;

            dtype2.DATA = dtype1.Q;
            dtype2.SET = set;
            dtype2.CLEAR = set;
            dtype2.CLK = clock;

            dtype3.DATA = dtype2.Q;
            dtype3.SET = set;
            dtype3.CLEAR = set;
            dtype3.CLK = clock;

            dtype4.DATA = dtype3.Q;
            dtype4.SET = set;
            dtype4.CLEAR = set;
            dtype4.CLK = clock;
        }

        MONITORS {
            dtype1.Q;
            dtype2.Q;
            dtype3.Q;
            dtype4.Q;
        }

        END
        """, scan_through_all)
        return scanner
    return _scanner_fixture


@pytest.fixture
def parser_fixture(names_fixture, devices_fixture, network_fixture, monitors_fixture):
    """Return a new parser instance"""
    def _parser_fixture(scanner):
        return Parser(names_fixture, devices_fixture, network_fixture, monitors_fixture, scanner)
    return _parser_fixture


def test_parser_fixture(parser_fixture, create_testing_file_to_scan):
    """Test the parser fixture"""
    scanner = create_testing_file_to_scan(
        """
        DEVICES {
        dtype1 = DTYPE;
        dtype2 = DTYPE;
        dtype3 = DTYPE;
        dtype4 = DTYPE;
        clock = CLK(25);
        data = SWITCH(0);
    }
    """, scan_through_all=True)

    parser = parser_fixture(scanner)

    assert isinstance(parser, Parser)

    assert parser.names.names_list == \
        ['AND', 'OR', 'NAND', 'NOR', 'XOR', 'CLOCK', 'SWITCH', 'DTYPE', 'CLK', 'SET', 'CLEAR', 'DATA', 'Q', 'QBAR',
            'DEVICES', 'CONNECTIONS', 'MONITORS', 'END', 'dtype1', 'dtype2', 'dtype3', 'dtype4', 'clock', '25', 'data', '0']


# DEPRECATED
# @pytest.fixture
# def old_parser_fixture(names_fixture, old_scanner_fixture):
#     """Return a new parser instance
#     DEPRECATED"""
#     return Parser(names_fixture, old_scanner_fixture)


@pytest.fixture
def set_scanner_location(scanner_fixture):
    """Returns _set_scanner_location function to target location within parameters"""
    def _set_scanner_location(target_location):
        target_line_number, target_position = target_location
        scanner = scanner_fixture()  # call scanner instance

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

# # DEPRECATED


@pytest.fixture
def symbol_fixture(scanner_fixture, set_scanner_location):
    """Returns a symbol instance at a particular place"""
    scanner = scanner_fixture()
    set_scanner_location((2, 5))
    symbol = scanner.get_symbol()

    return symbol


# # # DEPRECATED


@pytest.fixture
def correct_error_arguments(symbol_fixture):
    """Return the correct error arguments"""
    symbol = symbol_fixture
    return symbol, 4, True, True, [2, 3, 6, 8]


def test_parser_initialisation(scanner_fixture, parser_fixture):
    """Test the parser initialisation and exception handling"""
    scanner = scanner_fixture()
    parser = parser_fixture(scanner)

    assert isinstance(parser.names, Names)
    assert isinstance(parser.devices, Devices)
    assert isinstance(parser.network, Network)
    assert isinstance(parser.monitors, Monitors)
    assert isinstance(parser.scanner, Scanner)

    assert parser.error_count == 0
    # Check unique error coes are appended onto existing syntax_errors of which there are 15 from devices, network and monitors initialisation
    assert parser.syntax_errors == range(15, 39)


def test_parser_display_error_instance_handling(scanner_fixture, parser_fixture):
    """Test the parser exception handling"""
    scanner = scanner_fixture(scan_through_all=False)
    parser = parser_fixture(scanner)
    symbol = parser.scanner.get_symbol()
    error_type = parser.syntax_errors[0]
    proceed = True

    with pytest.raises(TypeError):
        # Expected error_type to be an integer type argument
        parser.display_error(symbol, "non-integer error_type")
    with pytest.raises(ValueError):
        # Cannot have a negative error code
        parser.display_error(symbol, -1)
    with pytest.raises(TypeError):
        # Expected an instance of the Symbol class
        parser.display_error("not an instance of Symbol class", error_type)
    with pytest.raises(TypeError):
        # Expected stopping symbol to be an integer type argument
        parser.display_error(symbol, error_type,
                             stopping_symbol_types="not a list")
    with pytest.raises(ValueError):
        # Expected stopping symbol to be within range of given symbols
        parser.display_error(symbol, error_type,
                             stopping_symbol_types=list(range(max(parser.syntax_errors) + 16)))
    with pytest.raises(ValueError):
        # Expected stopping symbol to be within range of given symbols
        parser.display_error(symbol, error_type, proceed,
                             stopping_symbol_types=list(range(0)))
    with pytest.raises(ValueError):
        # Expected stopping symbol to be within range of given symbols
        parser.display_error(symbol, error_type, proceed,
                             stopping_symbol_types=list(range(-8)))
    with pytest.raises(TypeError):
        # Expected bool type argument for proceed
        parser.display_error(symbol, error_type, proceed="not a bool")
    with pytest.raises(TypeError):
        # Expected bool type argument for proceed
        parser.display_error(symbol, error_type, syntax_error="not a bool")


def test_parser_display_error_see_error_count_increment_by_one(scanner_fixture, parser_fixture):
    """Test display_error functionality"""
    scanner = scanner_fixture()
    parser = parser_fixture(scanner)
    symbol = parser.scanner.get_symbol()
    error_type = parser.syntax_errors[0]

    parser.display_error(symbol, error_type)

    assert parser.error_count == 1


@pytest.mark.parametrize("error_type, expected_message", [
    ("parser.NO_DEVICES_KEYWORD", "  Line 2: Syntax Error: Expected the keyword DEVICES"),
    ("parser.NO_CONNECTIONS_KEYWORD",
     "  Line 2: Syntax Error: Expected the keyword CONNECTIONS"),
    ("parser.NO_MONITORS_KEYWORD",
     "  Line 2: Syntax Error: Expected the keyword MONITORS"),
    ("parser.NO_END_KEYWORD",
     "  Line 2: Syntax Error: Expected the keyword END straight after monitors list"),
    ("parser.NO_BRACE_OPEN", "  Line 2: Syntax Error: Expected a '{' symbol"),
    ("parser.NO_BRACE_CLOSE", "  Line 2: Syntax Error: Expected a '}' symbol"),
    ("parser.INVALID_NAME", "  Line 2: Syntax Error: Invalid user name entered"),
    ("parser.NO_EQUALS", "  Line 2: Syntax Error: Expected an '=' symbol"),
    ("parser.INVALID_COMPONENT",
     "  Line 2: Syntax Error: Invalid component name entered"),
    ("parser.NO_BRACKET_OPEN",
     "  Line 2: Syntax Error: Expected a '(' for an input"),
    ("parser.NO_BRACKET_CLOSE", "  Line 2: Syntax Error: Expected a ')' for an input"),
    ("parser.NO_NUMBER", "  Line 2: Syntax Error: Expected a positive integer"),
    ("parser.INPUT_OUT_OF_RANGE",
     "  Line 2: Semantic Error: Input number of gates is out of range. Must be an integer between 1 and 16"),
    ("parser.CLK_OUT_OF_RANGE",
     "  Line 2: Semantic Error: Input clock half period is out of range. Must be a positive integer"),
    ("parser.SWITCH_OUT_OF_RANGE",
     "  Line 2: Semantic Error: Input switch number is out of range. Must be either 1 or 0"),
    ("parser.UNDEFINED_NAME", "  Line 2: Syntax Error: Undefined device name given"),
    ("parser.NO_FULLSTOP", "  Line 2: Syntax Error: Expected a full stop"),
    ("parser.NO_SEMICOLON", "  Line 2: Syntax Error: Expected a semicolon"),
    ("parser.NO_Q_OR_QBAR",
     "  Line 2: Syntax Error: Expected a Q or QBAR after the full stop"),
    ("parser.NO_INPUT_SUFFIX", "  Line 2: Syntax Error: Expected a valid input suffix"),
    ("parser.SYMBOL_AFTER_END",
     "  Line 2: Syntax Error: There should not be any text after the keyword END"),
    ("parser.EMPTY_FILE", "  Line 2: Syntax Error: Cannot parse an empty file"),
    ("parser.TERMINATE", "  Line 2: Syntax Error: Could not find parsing point to restart, program terminated early"),
    ("parser.devices.NO_QUALIFIER",
     "  Line 2: Semantic Error: Expected a device property for initialisation"),
    ("parser.devices.QUALIFIER_PRESENT",
     "  Line 2: Semantic Error: Expected no device property for this device"),
    ("parser.devices.DEVICE_PRESENT",
     "  Line 2: Semantic Error: Device already exists in the device list"),
    ("parser.devices.BAD_DEVICE", "  Line 2: Semantic Error: Invalid type of device"),
    ("parser.network.INPUT_TO_INPUT",
     "  Line 2: Semantic Error: Cannot connect an input port to another input port"),
    ("parser.network.OUTPUT_TO_OUTPUT",
     "  Line 2: Semantic Error: Cannot connect an output port to another output port"),
    ("parser.network.INPUT_CONNECTED",
     "  Line 2: Semantic Error: Cannot connect input port as it is already connected"),
    ("parser.network.PORT_ABSENT",
     "  Line 2: Semantic Error: Cannot make connection as specified port does not exist"),
    ("parser.network.DEVICE_ABSENT",
     "  Line 2: Semantic Error: Cannot make connection as device is undefined in DEVICE list"),
    ("parser.FLOATING_INPUT",
     "  Line 2: Semantic Error: Cannot make network as not all inputs are connected to an output"),
    ("parser.monitors.MONITOR_PRESENT",
     "  Line 2: Semantic Error: Cannot assign more than one monitor to a single device output port")


])
def test_parser_display_error_show_appropriate_error_message(scanner_fixture, parser_fixture, capfd, error_type, expected_message):
    """Test display_error returns the correct error strings"""
    scanner = scanner_fixture(False)
    parser = parser_fixture(scanner)
    symbol = parser.scanner.get_symbol()
    error_type = eval(error_type)

    parser.display_error(symbol, error_type)

    captured = capfd.readouterr()
    output_lines = captured.out.splitlines()

    assert output_lines[1] == expected_message


def test_parser_display_error_valid_error_code(scanner_fixture, parser_fixture, correct_error_arguments):
    """Test display_error returns ValueError for out of range error_code"""
    scanner = scanner_fixture()
    parser = parser_fixture(scanner)
    symbol, error_type, syntax_error, proceed, stopping_symbol_types = correct_error_arguments
    invalid_error_type = max(parser.syntax_errors) + 16

    with pytest.raises(ValueError):
        parser.display_error(symbol, invalid_error_type,
                             syntax_error, proceed, stopping_symbol_types)


def test_parser_display_error_symbol_is_EOF(parser_fixture, create_testing_file_to_scan):
    """Test display_error when symbol is EOF"""
    scanner = create_testing_file_to_scan(
        """
    """, scan_through_all=True)
    parser = parser_fixture(scanner)
    error_type = parser.syntax_errors[0]

    symbol = parser.scanner.get_symbol()
    symbol.type = parser.scanner.EOF

    assert parser.display_error(symbol, error_type) is None


def test_error_recovery_instance_handling(scanner_fixture, parser_fixture, correct_error_arguments):
    """Test exception handling in error_recovery function"""
    scanner = scanner_fixture()
    parser = parser_fixture(scanner)
    symbol = parser.scanner.get_symbol()
    error_type = parser.syntax_errors[0]

    with pytest.raises(TypeError):
        # Expected error_type to be an integer type argument
        parser.error_recovery("not an integer")
    with pytest.raises(ValueError):
        # Expected an error code within range of error types
        parser.error_recovery(max(parser.syntax_errors) + 16)
    with pytest.raises(ValueError):
        # Cannot have a negative error code
        parser.error_recovery(-4)
    with pytest.raises(TypeError):
        # Expected bool type argument for syntax_error
        parser.error_recovery(error_type, syntax_error="not a boolean")
    with pytest.raises(TypeError):
        # Expected bool type argument for proceed
        parser.error_recovery(error_type, proceed="not a boolean")
    with pytest.raises(TypeError):
        # Expected stopping symbol to be an integer type argument
        parser.error_recovery(error_type, stopping_symbol_types="not a list")
    with pytest.raises(ValueError):
        # Expected stopping symbol to be within range of given symbols
        parser.error_recovery(
            error_type, stopping_symbol_types=list(range(12)))
    with pytest.raises(ValueError):
        # Expected stopping symbol to be within range of given symbols
        parser.error_recovery(
            error_type, stopping_symbol_types=list(range(32)))
    with pytest.raises(ValueError):
        # Expected stopping symbol to be within range of given symbols
        parser.error_recovery(error_type, stopping_symbol_types=list(range(0)))
    with pytest.raises(ValueError):
        # Expected stopping symbol to be within range of given symbols
        parser.error_recovery(
            error_type, stopping_symbol_types=list(range(-8)))


def test_parser_error_recovery_check_built_in_error_handling(scanner_fixture, parser_fixture):
    """Test error_recovery returns None type"""
    scanner = scanner_fixture()
    parser = parser_fixture(scanner)
    symbol = parser.scanner.get_symbol()
    error_type = parser.syntax_errors[0]

    assert parser.error_recovery(error_type, proceed=True) is None


def test_parser_error_recovery_check_built_in_error_handling_semantic_error(scanner_fixture, parser_fixture):
    """Test error_recovery returns None type when semantic error is encountered"""
    scanner = scanner_fixture()
    parser = parser_fixture(scanner)
    symbol = parser.scanner.get_symbol()
    error_type = parser.syntax_errors[0]

    assert parser.error_recovery(error_type, syntax_error=False) is None


def test_parser_error_recovery_stops_when_stopping_symbol_or_EOF_is_encountered(create_testing_file_to_scan, parser_fixture):
    """Test error_recovery returns None when EOF symbol is encounterred"""
    scanner = create_testing_file_to_scan(
        """
    DEVICES {
        dtype1 = DTYPE;
        dtype2 = DTYPE;
        dtype3 = DTYPE;
        dtype4 = DTYPE;
        clock = CLK(25);
        data = SWITCH(0);
    }
    """, scan_through_all=False)
    parser = parser_fixture(scanner)
    parser.symbol = parser.scanner.get_symbol()
    error_type = parser.syntax_errors[0]

    assert parser.error_recovery(error_type, proceed=False) is None


@pytest.mark.parametrize("KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol", [
    ('DEVICES', 'scanner.names.lookup(["DEVICES"])[0]',
     'parser.NO_DEVICES_KEYWORD', 'dtype1 = DTYPE;', 'dtype1'),
    ('CONNECTIONS', 'scanner.names.lookup(["CONNECTIONS"])[0]',
     'parser.NO_CONNECTIONS_KEYWORD', 'dtype1.Q = dtype2.DATA;', 'dtype1'),
    ('MONITORS', 'scanner.names.lookup(["MONITORS"])[0]',
     'parser.NO_MONITORS_KEYWORD', 'dtype1.Q;', 'dtype1'),
])
def test_parser_initial_error_checks_case_1(parser_fixture, create_testing_file_to_scan, capfd, KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol):
    """Test initial_error_checks for Case 1:  KEYWORD { ..."""
    scanner = create_testing_file_to_scan(
        f"""
    {KEYWORD} {{ {correct_example}
    """
    )
    parser = parser_fixture(scanner)
    parser.symbol = parser.scanner.get_symbol()

    parser.initial_error_checks(eval(KEYWORD_ID), eval(missing_error_type))
    symbol_id = parser.symbol.id
    assert parser.names.get_name_string(symbol_id) == expected_symbol


@pytest.mark.parametrize("KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol, expected_message", [
    ('DVICES', 'scanner.names.lookup(["DEVICES"])[0]', 'parser.NO_DEVICES_KEYWORD', 'dtype1 = DTYPE;',
     'dtype1', '\n  Line 2: Syntax Error: Expected the keyword DEVICES\n \n        DVICES { dtype1 = DTYPE;'),
    ('CONNETIONS', 'scanner.names.lookup(["CONNECTIONS"])[0]', 'parser.NO_CONNECTIONS_KEYWORD', 'dtype1.Q = dtype2.DATA;',
     'dtype1', '\n  Line 2: Syntax Error: Expected the keyword CONNECTIONS\n \n        CONNETIONS { dtype1.Q = dtype2.DATA;'),
    ('MONITOS', 'scanner.names.lookup(["MONITORS"])[0]', 'parser.NO_MONITORS_KEYWORD', 'dtype1.Q;',
     'dtype1', '\n  Line 2: Syntax Error: Expected the keyword MONITORS\n \n        MONITOS { dtype1.Q;'),
])
def test_parser_initial_error_checks_case_2(parser_fixture, create_testing_file_to_scan, capfd, KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol, expected_message):
    """Test initial_error_checks for Case 2:  KYWORD { ..."""
    scanner = create_testing_file_to_scan(
        f"""
    {KEYWORD} {{ {correct_example}
    """
    )
    parser = parser_fixture(scanner)
    parser.symbol = parser.scanner.get_symbol()

    parser.initial_error_checks(eval(KEYWORD_ID), eval(missing_error_type))

    captured = capfd.readouterr()
    output_lines = captured.out.splitlines()
    semicolon_location = captured.out.index(";")
    # only up to and including the semicolon, i.e., ignore the caret/tilde/placement line
    printed_message = captured.out[:semicolon_location + 1]
    assert printed_message == expected_message

    symbol_id = parser.symbol.id
    assert parser.names.get_name_string(symbol_id) == expected_symbol


@pytest.mark.parametrize("KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol, expected_message", [
    ('DEVICES', 'scanner.names.lookup(["DEVICES"])[0]', 'parser.NO_DEVICES_KEYWORD', 'dtype1 = DTYPE;',
     'dtype1', '\n  Line 2: Syntax Error: Expected the keyword DEVICES\n \n        { dtype1 = DTYPE;'),
    ('CONNECTIONS', 'scanner.names.lookup(["CONNECTIONS"])[0]', 'parser.NO_CONNECTIONS_KEYWORD', 'dtype1.Q = dtype2.DATA;',
     'dtype1', '\n  Line 2: Syntax Error: Expected the keyword CONNECTIONS\n \n        { dtype1.Q = dtype2.DATA;'),
    ('MONITORS', 'scanner.names.lookup(["MONITORS"])[0]', 'parser.NO_MONITORS_KEYWORD', 'dtype1.Q;',
     'dtype1', '\n  Line 2: Syntax Error: Expected the keyword MONITORS\n \n        { dtype1.Q;'),
])
def test_parser_initial_error_checks_case_3(parser_fixture, create_testing_file_to_scan, capfd, KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol, expected_message):
    """Test initial_error_checks for Case 3:  { ..."""
    scanner = create_testing_file_to_scan(
        f"""
    {{ {correct_example}
    """
    )
    parser = parser_fixture(scanner)
    parser.symbol = parser.scanner.get_symbol()

    parser.initial_error_checks(eval(KEYWORD_ID), eval(missing_error_type))

    captured = capfd.readouterr()
    output_lines = captured.out.splitlines()
    semicolon_location = captured.out.index(";")
    # only up to and including the semicolon, i.e., ignore the caret/tilde placement line
    printed_message = captured.out[:semicolon_location + 1]
    assert printed_message == expected_message

    symbol_id = parser.symbol.id
    assert parser.names.get_name_string(symbol_id) == expected_symbol


@pytest.mark.parametrize("KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_message_1, expected_message_2", [
    ('DEVICES', 'scanner.names.lookup(["DEVICES"])[0]', 'parser.NO_DEVICES_KEYWORD', 'dtype1 = DTYPE;',
     '\n  Line 2: Syntax Error: Expected the keyword DEVICES\n \n        dtype1 = DTYPE;\n', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        dtype1 = DTYPE;\n"),
    ('CONNECTIONS', 'scanner.names.lookup(["CONNECTIONS"])[0]', 'parser.NO_CONNECTIONS_KEYWORD', 'dtype1.Q = dtype2.DATA;',
     '\n  Line 2: Syntax Error: Expected the keyword CONNECTIONS\n \n        dtype1.Q = dtype2.DATA;\n', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        dtype1.Q = dtype2.DATA;\n"),
    ('MONITORS', 'scanner.names.lookup(["MONITORS"])[0]', 'parser.NO_MONITORS_KEYWORD', 'dtype1.Q;',
     '\n  Line 2: Syntax Error: Expected the keyword MONITORS\n \n        dtype1.Q;\n', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        dtype1.Q;\n"),
])
def test_parser_initial_error_checks_case_4(parser_fixture, create_testing_file_to_scan, capfd, KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_message_1, expected_message_2):
    """Test initial_error_checks for Case 4:  ..."""
    scanner = create_testing_file_to_scan(
        f"""
    {correct_example}
    """
    )
    parser = parser_fixture(scanner)
    parser.symbol = parser.scanner.get_symbol()

    parser.initial_error_checks(eval(KEYWORD_ID), eval(missing_error_type))

    captured = capfd.readouterr()
    output_lines = captured.out.splitlines(True)
    # indexing done to ignore caret/tilde placement line
    first_printed_message = ''.join(output_lines[:4])
    # indexing done to ignore caret/tilde placement line
    second_printed_message = ''.join(output_lines[6:10])

    assert first_printed_message == expected_message_1
    assert second_printed_message == expected_message_2

    assert parser.symbol.type == parser.scanner.EOF


@pytest.mark.parametrize("KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol, expected_message", [
    ('DEVICES', 'scanner.names.lookup(["DEVICES"])[0]', 'parser.NO_DEVICES_KEYWORD', 'dtype1 = DTYPE;',
     'dtype1', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        DEVICES dtype1 = DTYPE;\n"),
    ('CONNECTIONS', 'scanner.names.lookup(["CONNECTIONS"])[0]', 'parser.NO_CONNECTIONS_KEYWORD', 'dtype1.Q = dtype2.DATA;',
     'dtype1', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        CONNECTIONS dtype1.Q = dtype2.DATA;\n"),
    ('MONITORS', 'scanner.names.lookup(["MONITORS"])[0]', 'parser.NO_MONITORS_KEYWORD', 'dtype1.Q;',
     'dtype1', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        MONITORS dtype1.Q;\n"),
])
def test_parser_initial_error_checks_case_5(parser_fixture, create_testing_file_to_scan, capfd, KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_symbol, expected_message):
    """Test initial_error_checks for Case 5:  { ..."""
    scanner = create_testing_file_to_scan(
        f"""
    {KEYWORD} {correct_example}
    """
    )
    parser = parser_fixture(scanner)
    parser.symbol = parser.scanner.get_symbol()

    parser.initial_error_checks(eval(KEYWORD_ID), eval(missing_error_type))

    captured = capfd.readouterr()
    output_lines = captured.out.splitlines(True)
    # indexing done to ignore caret/tilde placement line
    printed_message = ''.join(output_lines[:4])
    assert printed_message == expected_message

    symbol_id = parser.symbol.id
    assert parser.names.get_name_string(symbol_id) == expected_symbol


@pytest.mark.parametrize("KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_message_1, expected_message_2", [
    ('DEICES', 'scanner.names.lookup(["DEVICES"])[0]', 'parser.NO_DEVICES_KEYWORD', 'dtype1 = DTYPE;',
     '\n  Line 2: Syntax Error: Expected the keyword DEVICES\n \n        DEICES dtype1 = DTYPE;\n', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        DEICES dtype1 = DTYPE;\n"),
    ('CONNECTIOS', 'scanner.names.lookup(["CONNECTIONS"])[0]', 'parser.NO_CONNECTIONS_KEYWORD', 'dtype1.Q = dtype2.DATA;',
     '\n  Line 2: Syntax Error: Expected the keyword CONNECTIONS\n \n        CONNECTIOS dtype1.Q = dtype2.DATA;\n', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        CONNECTIOS dtype1.Q = dtype2.DATA;\n"),
    ('MOITORS', 'scanner.names.lookup(["MONITORS"])[0]', 'parser.NO_MONITORS_KEYWORD', 'dtype1.Q;',
     '\n  Line 2: Syntax Error: Expected the keyword MONITORS\n \n        MOITORS dtype1.Q;\n', "\n  Line 2: Syntax Error: Expected a '{' symbol\n \n        MOITORS dtype1.Q;\n"),
])
def test_parser_initial_error_checks_case_6(parser_fixture, create_testing_file_to_scan, capfd, KEYWORD, KEYWORD_ID, missing_error_type, correct_example, expected_message_1, expected_message_2):
    """Test initial_error_checks for Case 6:  { ..."""
    scanner = create_testing_file_to_scan(
        f"""
    {KEYWORD} {correct_example}
    """
    )
    parser = parser_fixture(scanner)
    parser.symbol = parser.scanner.get_symbol()

    parser.initial_error_checks(eval(KEYWORD_ID), eval(missing_error_type))

    captured = capfd.readouterr()
    output_lines = captured.out.splitlines(True)
    # indexing done to ignore caret/tilde placement line
    first_printed_message = ''.join(output_lines[:4])
    # indexing done to ignore caret/tilde placement line
    second_printed_message = ''.join(output_lines[6:10])

    assert first_printed_message == expected_message_1
    assert second_printed_message == expected_message_2

    assert parser.symbol.type == parser.scanner.EOF


# '''@pytest.mark.parametrize("example, expected", [
#     ("AND(12)", "(parser.symbol.id, 12)"),
#     ("XOR", "(parser.symbol.id, parser.symbol.type)"),
#     ("DTYPE", "(parser.symbol.id, parser.symbol.type)"),
# ])
# def test_parser_check_device_is_valid_correct_example(parser_fixture, create_testing_file_to_scan, example, expected):
#     scanner = create_testing_file_to_scan(
#     f"""
#     {example}
#     """
#     )
#     parser = parser_fixture(scanner)
#     parser.symbol = parser.scanner.get_symbol()
#     result = eval(expected)

#     assert parser.check_device_is_valid() == result'''


# @pytest.mark.parametrize("example, expected", [
#     ("AND(12", "  Line 3: Syntax Error: Expected a ')' for an input\n"),
#     ("AND(34)", "  Line 2: Semantic Error: Input number of gates is out of range. Must be an integer between 1 and 16\n"),
#     ("AND()", "  Line 2: Syntax Error: Expected a positive integer\n"),
#     ("AND 12)", "  Line 2: Syntax Error: Expected a '(' for an input\n"),
# ])
# def test_parser_check_device_is_valid_erroneous_examples(parser_fixture, create_testing_file_to_scan, capfd, example, expected):
#     scanner = create_testing_file_to_scan(
#         f"""
#     {example}
#     """
#     )
#     parser = parser_fixture(scanner)
#     parser.symbol = parser.scanner.get_symbol()
#     parser.check_device_is_valid()

#     captured = capfd.readouterr()
#     printed_message = captured.out.splitlines(True)[1]

#     assert printed_message == expected


# def test_parser_device_correct_parsing_of_device_list(parser_fixture, create_testing_file_to_scan):
#     scanner = create_testing_file_to_scan(
#         """
#     DEVICES {
#         dtype1 = DTYPE;
#         dtype2 = DTYPE;
#         dtype3 = DTYPE;
#         dtype4 = DTYPE;
#         clock = CLK(25);
#         data = SWITCH(0);
#     }
#     """, scan_through_all=False)

#     parser = parser_fixture(scanner)
#     assert parser.device_list() is None


# def test_delete_testing_file():
#     """This is an in-house helper function not strictly related to testing parse.py"""
#     if os.path.exists("testing_file.txt"):
#         os.remove("testing_file.txt")
#     else:
#         print("The file does not exist")
