"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from names import Names
# Will need to add more imports once building network
from scanner import Scanner, Symbol

# JC! signifies a comment to Josephine for later development


class Parser:

    """Parse the definition file and build the logic network.

    The parser deals with error handling. It analyses the syntactic and
    semantic correctness of the symbols it receives from the scanner, and
    then builds the logic network. If there are errors in the definition file,
    the parser detects this and tries to recover from it, giving helpful
    error messages.

    Parameters
    ----------
    names: instance of the names.Names() class.
    devices: instance of the devices.Devices() class.
    network: instance of the network.Network() class.
    monitors: instance of the monitors.Monitors() class.
    scanner: instance of the scanner.Scanner() class.

    Public methods
    --------------

    display_error(self, symbol, error_type, proceed=True, stopping_symbol_types=[6]): Display the error message and where it occured.
    Calls the error handling method to resume from the next available point.

    error_recovery(self, error_type, proceed=True, stopping_symbol_types=[6]): Recover from an error by resuming parsing at an appropriate point specified by the stopping_symbol.

    initial_error_checks(self, KEYWORD_ID, missing_error_type): Check initial symbols for common errors. This function tests for 6 cases:

        ... represents the first line of the list. For cases 4 and 6, because it is difficult 
        to distinguish between them, we merely skip to the next stopping symbol.

        1. Correct - when both keyword and open brace are present: KEYWORD { ...
        2. First keyword is spelt wrong, but open brace follows: KYWORD { ...
        3. Missing first keyword, but open brace follows: { ...
        4. Missing both the first keyword and open brace: ... 
        5. First keyword is correct, but missing open brace: { ...
        6. First keyword is spelt wrong, and missing an open brace { ...

    device_list(self): Parse device list.

    device(self): Parse user defined device.

    check_device_is_valid(self): Check if device is valid and return both device type ID and the input ID.

    connection_list(self): Parse connection list.

    connection(self): Parse a connection.

    output(self): Parse a single device output.

    input(self): Parse a single device input.

    monitor_list(self): Parse monitor list.

    end(self): Parse an END keyword and check there are no symbols afterwards.

    parse_network(self): Parse the circuit definition file and return true if there are no files.

    """

#    def __init__(self, names, devices, network, monitors, scanner):
    def __init__(self, names, scanner):
        """Initialise constants."""
        self.names = names
        self.scanner = scanner

        # Initial symbol
        self.symbol = None

        # Count number of errors
        self.error_count = 0

        # List of syntax errors
        self.syntax_errors = [self.NO_DEVICES_KEYWORD, self.NO_CONNECTIONS_KEYWORD, self.NO_MONITORS_KEYWORD, self.NO_END_KEYWORD, self.NO_BRACE_OPEN, self.NO_BRACE_CLOSE,
                              self.INVALID_NAME, self.NO_EQUALS, self.INVALID_COMPONENT, self.NO_BRACKET_OPEN, self.NO_BRACKET_CLOSE, self.NO_NUMBER, self.CLK_OUT_OF_RANGE, self.SWITCH_OUT_OF_RANGE,
                              self.UNDEFINED_NAME, self.NO_FULLSTOP, self.NO_SEMICOLON, self.NO_Q_OR_QBAR, self.NO_INPUT_SUFFIX, self.SYMBOL_AFTER_END, self.EMPTY_FILE, self.TERMINATE] = self.names.unique_error_codes(22)

    # Stopping symbols automatically assigned to semi-colons, braces and keywords
    def display_error(self,  symbol, error_type,  proceed=True, stopping_symbol_types=[2, 3, 6, 8]):
        """Display the error message and where it occured

        Calls the error handling method to resume from the next available point."""

        # Exception handling
        if not isinstance(error_type, int):
            raise TypeError(
                "Expected error_type to be an integer type argument")
        elif error_type >= len(self.syntax_errors):
            raise ValueError(
                "Expected an error code within range of error types")
        elif error_type < 0:
            raise ValueError("Cannot have a negative error code")
        elif not isinstance(symbol, Symbol):
            raise TypeError("Expected an instance of the Symbol class")
        elif not isinstance(stopping_symbol_types,  list):
            raise TypeError(
                "Expected stopping symbol to be an integer type argument")
        elif ((len(stopping_symbol_types) >= 12) or (len(stopping_symbol_types) <= 0)):
            raise ValueError(
                "Expected stopping symbol to be within range of given symbols")
        elif not isinstance(proceed, bool):
            raise TypeError("Expected bool type argument for proceed")

        # Increase error count by one
        self.error_count += 1

        # Display location and type of error
        print(f"\n  Line {symbol.line_number}:", end=" ")
        if error_type == self.NO_DEVICES_KEYWORD:
            print("Syntax Error: Expected the keyword DEVICES", end="\n \n")
        elif error_type == self.NO_CONNECTIONS_KEYWORD:
            print("Syntax Error: Expected the keyword CONNECTIONS", end="\n \n")
        elif error_type == self.NO_MONITORS_KEYWORD:
            print("Syntax Error: Expected the keyword MONITORS", end="\n \n")
        elif error_type == self.NO_END_KEYWORD:
            print(
                "Syntax Error: Expected the keyword END straight after monitors list", end="\n \n")
        elif error_type == self.NO_BRACE_OPEN:
            print("Syntax Error: Expected a '{' symbol", end="\n \n")
        elif error_type == self.NO_BRACE_CLOSE:
            print("Syntax Error: Expected a '}' symbol", end="\n \n")
        elif error_type == self.INVALID_NAME:
            print("Syntax Error: Invalid user name entered", end="\n \n")
        elif error_type == self.NO_EQUALS:
            print("Syntax Error: Expected an '=' symbol", end="\n \n")
        elif error_type == self.INVALID_COMPONENT:
            print("Syntax Error: Invalid component name entered", end="\n \n")
        elif error_type == self.NO_BRACKET_OPEN:
            print("Syntax Error: Expected a '(' for an input", end="\n \n")
        elif error_type == self.NO_BRACKET_CLOSE:
            print("Syntax Error: Expected a ')' for an input", end="\n \n")
        elif error_type == self.NO_NUMBER:
            print("Syntax Error: Expected a positive integer", end="\n \n")
        elif error_type == self.CLK_OUT_OF_RANGE:
            print(
                "Semantic Error: Input clock half period is out of range. Must be a positive integer", end="\n \n")
        elif error_type == self.SWITCH_OUT_OF_RANGE:
            print(
                "Semantic Error: Input switch number is out of range. Must be either 1 or 0", end="\n \n")
        elif error_type == self.UNDEFINED_NAME:
            print("Syntax Error: Undefined device name given", end="\n \n")
        elif error_type == self.NO_FULLSTOP:
            print("Syntax Error: Expected a full stop", end="\n \n")
        elif error_type == self.NO_SEMICOLON:
            print("Syntax Error: Expected a semicolon", end="\n \n")
        elif error_type == self.NO_Q_OR_QBAR:
            print("Syntax Error: Expected a Q or QBAR after the full stop", end="\n \n")
        elif error_type == self.NO_INPUT_SUFFIX:
            print("Syntax Error: Expected a valid input suffix", end="\n \n")
        elif error_type == self.SYMBOL_AFTER_END:
            print(
                "Syntax Error: There should not be any text after the keyword END", end="\n \n")
        elif error_type == self.EMPTY_FILE:
            print("Syntax Error: Cannot parse an empty file", end="\n \n")
        elif error_type == self.TERMINATE:
            print(
                "Syntax Error: Could not find parsing point to restart, program terminated early", end="\n \n")
        else:
            raise ValueError("Expected a valid error code")

        # Display error line and visual marker
        if symbol.type == self.scanner.EOF:
            return
        self.scanner.display_line_and_marker(symbol)
        # Call error recovery function to resume parsing at appropriate point
        self.error_recovery(error_type, proceed, stopping_symbol_types)
        return

    def error_recovery(self, error_type, proceed=True, stopping_symbol_types=[2, 3, 6, 8]):
        """Recover from an error by resuming parsing at an appropriate point."""

        # Exception handling
        if not isinstance(error_type, int):
            raise TypeError(
                "Expected error_type to be an integer type argument")
        elif error_type >= len(self.syntax_errors):
            raise ValueError(
                "Expected an error code within range of error types")
        elif error_type < 0:
            raise ValueError("Cannot have a negative error code")
        elif not isinstance(proceed, bool):
            raise TypeError("Expected bool type argument for proceed")
        elif not isinstance(stopping_symbol_types, list):
            raise TypeError(
                "Expected stopping symbol to be an integer type argument")
        elif ((len(stopping_symbol_types) >= 12) or (len(stopping_symbol_types) <= 0)):
            raise ValueError(
                "Expected stopping symbol to be within range of given symbols")

        # Check if we have already built in error handling (have done so for obvious semantic errors, e.g. missing KEYWORD)
        if proceed == True:
            return
        # Check if we need to skip symbols to recover parsing
        else:
            while ((self.symbol.type not in stopping_symbol_types) and (self.symbol.type != self.scanner.EOF)):
                self.symbol = self.scanner.get_symbol()
            # Stop when stopping symbol is encountered
            if self.symbol.type in stopping_symbol_types:
                return
            elif self.symbol.type == self.scanner.EOF:
                self.display_error(self.symbol, self.TERMINATE)
                return

    def initial_error_checks(self, KEYWORD_ID, missing_error_type):
        """Check initial symbols for common errors. This function tests for 6 cases:

        ... represents the first line of the list. For cases 4 and 6, because it is difficult 
        to distinguish between them, we merely skip to the next stopping symbol.

        1. Correct - when both keyword and open brace are present: KEYWORD { ...
        2. First keyword is spelt wrong, but open brace follows: KYWORD { ...
        3. Missing first keyword, but open brace follows: { ...
        4. Missing both the first keyword and open brace: ... 
        5. First keyword is correct, but missing open brace: { ...
        6. First keyword is spelt wrong, and missing an open brace { ...
        """
        # If keyword is wrong
        if not (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == KEYWORD_ID):
            # If first symbol is a NAME type
            if not (self.symbol.type == self.scanner.NAME):
                # If open brace '{'
                if self.symbol.type == self.scanner.BRACE_OPEN:
                    # Case 3: { ...
                    self.display_error(self.symbol, missing_error_type)
                    self.symbol = self.scanner.get_symbol()
            else:
                self.symbol = self.scanner.get_symbol()
                # If open brace '{'
                if not (self.symbol.type == self.scanner.BRACE_OPEN):
                    # Case 4: ...
                    # and Case 6: D ...
                    self.display_error(self.symbol, missing_error_type)
                    self.display_error(
                        self.symbol, self.NO_BRACE_OPEN, proceed=False)
                    self.symbol = self.scanner.get_symbol()
                else:
                    # Case 2: D { ...
                    self.display_error(
                        self.symbol, missing_error_type)
                    self.symbol = self.scanner.get_symbol()
        # If keyword is present
        else:
            self.symbol = self.scanner.get_symbol()
            # If open brace '{'
            if not (self.symbol.type == self.scanner.BRACE_OPEN):
                # Case 5. KEYWORD ...
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
            else:
                # Case 1. KEYWORD{ ...
                self.symbol = self.scanner.get_symbol()

    def device_list(self):
        """Parse device list."""
        DEVICES_ID = self.names.lookup(["DEVICES"])[0]
        # Common initial error handling
        self.initial_error_checks(DEVICES_ID, self.NO_DEVICES_KEYWORD)
        # Parse device
        self.device()
        # Check if semicolon is missing but next symbol is a NAME type
        if self.symbol.type != self.scanner.SEMICOLON:
            self.display_error(
                self.symbol, self.NO_SEMICOLON, proceed=False)
        # Check all devices in list, which are all separated by a ';'
        while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
            self.symbol = self.scanner.get_symbol()
            # Incase a KEYWORD is entered straight after a ';', assume '}' was missed and go on to monitor list
            if (self.symbol.type == self.scanner.KEYWORD):
                self.display_error(self.symbol, self.NO_BRACE_CLOSE)
                return
            # Incase now a brace, leave while loop
            if self.symbol.type == self.scanner.BRACE_CLOSE:
                self.symbol = self.scanner.get_symbol()
                return
            self.device()
            # If semicolon is missing, but new NAME type symbol is entered, call error and parse to next stopping symbol
            if self.symbol.type == self.scanner.NAME:
                self.display_error(self.symbol, self.NO_SEMICOLON,
                                   proceed=False)
                # If stopping symbol reached is a semicolon, need to pass, else if brace, need to return
                if self.symbol.type == self.scanner.BRACE_CLOSE:
                    self.symbol = self.scanner.get_symbol()
                    return
                elif self.symbol.type == self.scanner.SEMICOLON:
                    pass
            # If semicolon is missing, and symbol is now a brace
            elif self.symbol.type == self.scanner.BRACE_CLOSE:
                self.display_error(self.symbol, self.NO_SEMICOLON)
                self.symbol = self.scanner.get_symbol()
                return
            # If semicolon missing and unknown symbol (including EOF)
            elif self.symbol.type != self.scanner.SEMICOLON:
                self.display_error(self.symbol, self.NO_SEMICOLON)
                return

    def device(self):
        """Parse user defined device."""
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            return
        # Check that we have a valid user defined name
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check that the name is followed by an equals sign
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                # Check that we then get a valid component name
                # JC! May need to change this assignment, but atm I believe this will be useful for creating the network
                symbol_ID, device_input = self.check_device_is_valid()

            else:
                self.display_error(
                    self.symbol, self.NO_EQUALS, proceed=False)
        else:
            self.display_error(self.symbol, self.INVALID_NAME, proceed=False)

    def check_device_is_valid(self):
        """Check if device is valid and return both device type ID and the input ID."""
        [AND_ID, NAND_ID, OR_ID, NOR_ID, XOR_ID, DTYPE_ID, SWITCH_ID, CLK_ID] = self.names.lookup(
            ["AND", "NAND", "OR", "NOR", "XOR", "DTYPE",  "SWITCH", "CLK"])
        one_to_sixteen = range(1, 17)
        binary_digit = [0, 1]
        # Check that name is either a AND, NAND, OR, NOR gate
        if self.symbol.id in [AND_ID, NAND_ID, OR_ID, NOR_ID]:
            symbol_ID = self.symbol
            self.symbol = self.scanner.get_symbol()
            # Check that gate is followed by open bracket symbol
            if self.symbol.type == self.scanner.BRACKET_OPEN:
                self.symbol = self.scanner.get_symbol()
                # Check that number of inputs is an integer
                if self.symbol.type == self.scanner.NUMBER:
                    # Check that number is within range
                    if self.symbol.id in one_to_sixteen:
                        number_of_inputs_ID = self.symbol.id
                        self.symbol = self.scanner.get_symbol()
                        # Check that next symbol is a close bracket ")"
                        if self.symbol.type == self.scanner.BRACKET_CLOSE:
                            self.symbol = self.scanner.get_symbol()
                            return symbol_ID, number_of_inputs_ID
                        else:
                            self.display_error(
                                self.symbol, self.NO_BRACKET_CLOSE,
                                proceed=False)
                            return None, None
                    else:
                        self.display_error(self.symbol, self.CLK_OUT_OF_RANGE,
                                           proceed=False)
                        return None, None
                else:
                    self.display_error(self.symbol, self.NO_NUMBER,
                                       proceed=False)
                    return None, None
            else:
                self.display_error(self.symbol, self.NO_BRACKET_OPEN,
                                   proceed=False)
                return None, None
        # Check if symbol is an XOR or DTYPE (with no inputs)
        elif self.symbol.id == XOR_ID or self.symbol.id == DTYPE_ID:
            self.symbol = self.scanner.get_symbol()
            return self.symbol.id, self.symbol.type
        # Check if symbol is a SWITCH type
        elif self.symbol.id == SWITCH_ID:
            symbol_ID = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            # Check that gate is followed by open bracket symbol
            if self.symbol.type == self.scanner.BRACKET_OPEN:
                self.symbol = self.scanner.get_symbol()
                # Check that number of inputs is an integer
                if self.symbol.type == self.scanner.NUMBER:
                    # Check that number is within range
                    switch_initial_state = int(
                        self.names.get_name_string(self.symbol.id))
                    if switch_initial_state in binary_digit:
                        # Check that the next symbol is a closed bracket
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.BRACKET_CLOSE:
                            self.symbol = self.scanner.get_symbol()
                            return symbol_ID, switch_initial_state
                        else:
                            self.display_error(
                                self.symbol, self.NO_BRACKET_CLOSE,
                                proceed=False)
                            return None, None
                    else:
                        self.display_error(self.symbol, self.SWITCH_OUT_OF_RANGE,
                                           proceed=False)
                        return None, None
                else:
                    self.display_error(self.symbol, self.NO_NUMBER,
                                       proceed=False)
                    return None, None
            else:
                self.display_error(self.symbol, self.NO_BRACKET_OPEN,
                                   proceed=False)
                return None, None
        # Check if symbol is a CLK
        elif self.symbol.id == CLK_ID:
            symbol_ID = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            # Check that the gate is followed by an open bracket symbol
            if self.symbol.type == self.scanner.BRACKET_OPEN:
                self.symbol = self.scanner.get_symbol()
                # Check that number of inputs is an integer
                if self.symbol.type == self.scanner.NUMBER:
                    number_of_cycles = int(self.names.get_name_string(
                        self.symbol.id))
                    # Check that input number is negative (this is a semantic check!)
                    if number_of_cycles > 0:
                        # Check that the next symbol is a close bracket
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.BRACKET_CLOSE:
                            self.symbol = self.scanner.get_symbol()
                            return symbol_ID, number_of_cycles
                        else:
                            self.display_error(
                                self.symbol, self.NO_BRACKET_CLOSE,
                                proceed=False)
                            return None, None
                    else:
                        self.display_error(self.symbol, self.CLK_OUT_OF_RANGE,
                                           proceed=False)
                        return None, None
                else:
                    self.display_error(self.symbol, self.NO_NUMBER,
                                       proceed=False)
                    return None, None
            else:
                self.display_error(self.symbol, self.NO_BRACKET_OPEN,
                                   proceed=False)
                return None, None
        else:
            self.display_error(self.symbol, self.INVALID_COMPONENT,
                               proceed=False)
            return None, None

    def connection_list(self):
        """Parse connection list."""
        CONNECTIONS_ID = self.names.lookup(["CONNECTIONS"])[0]
        # Common initial error handling
        self.initial_error_checks(CONNECTIONS_ID, self.NO_CONNECTIONS_KEYWORD)
        # Parse a connection
        self.connection()
        # Check if semicolon is missing but next symbol is a NAME type
        if self.symbol.type != self.scanner.SEMICOLON:
            self.display_error(
                self.symbol, self.NO_SEMICOLON, proceed=False)
        # Repeat checking connections in list until the close brace "}"
        while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
            self.symbol = self.scanner.get_symbol()
            # Incase a KEYWORD is entered straight after a ';', assume '{' was missed
            if (self.symbol.type == self.scanner.KEYWORD):
                self.display_error(self.symbol, self.NO_BRACE_CLOSE)
                return
            # Incase now a brace, leave while loop
            if self.symbol.type == self.scanner.BRACE_CLOSE:
                self.symbol = self.scanner.get_symbol()
                return
            self.connection()
            # If semicolon is missing, but new NAME type symbol is entered, call error and parse to next stopping symbol
            if self.symbol.type == self.scanner.NAME:
                self.display_error(self.symbol, self.NO_SEMICOLON,
                                   proceed=False)
                # If stopping symbol reached is a semicolon, need to pass, else if brace, need to return
                if self.symbol.type == self.scanner.BRACE_CLOSE:
                    self.symbol = self.scanner.get_symbol()
                    return
                elif self.symbol.type == self.scanner.SEMICOLON:
                    pass
            # If semicolon is missing, and symbol is now a brace
            elif self.symbol.type == self.scanner.BRACE_CLOSE:
                self.display_error(self.symbol, self.NO_SEMICOLON)
                self.symbol = self.scanner.get_symbol()
                return
            # If semicolon missing and unknown symbol (including EOF)
            elif self.symbol.type != self.scanner.SEMICOLON:
                self.display_error(self.symbol, self.NO_SEMICOLON)
                return

    def connection(self):
        """Parse a connection."""
        # self.symbol = self.scanner.get_symbol()
        # If after the semicolon we have a } , assume we can move onto the monitor_list
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            return
        else:
            self.output()
            # Incase we have had to error handle and recover, such that the symbol is now a ';'
            while self.symbol.type == self.scanner.SEMICOLON:
                self.symbol = self.scanner.get_symbol()
                self.output()
            # Check ouput connection is followed by an equals sign "="
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                self.input()
            else:
                self.display_error(self.symbol, self.NO_EQUALS,
                                   proceed=False)

    def output(self):
        """Parse a single device output."""
        valid_output_id_list = self.names.lookup(["Q", "QBAR"])
        # If after the semicolon we have a '}' , assume we can move onto the monitor_list
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            return
        # Check that the output to be connected is an already user-defined name
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check if gate is followed by a full stop
            if self.symbol.type == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                # Check that output suffix is Q or QBAR
                # JC! this may need to be redone to ensure semantic checking of non dtypes don't have fullstops after them
                if self.symbol.id in valid_output_id_list:
                    self.symbol = self.scanner.get_symbol()
                    return
                else:
                    self.display_error(self.symbol, self.NO_Q_OR_QBAR,
                                       proceed=False)
        else:
            self.display_error(self.symbol, self.INVALID_NAME, proceed=False)

    def input(self):
        """Parse a single device input."""
        valid_input_suffix_id_list = self.names.lookup(["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9",
                                                        "I10", "I11", "I12", "I13", "I14", "I15", "I16", "DATA", "CLK", "SET", "CLEAR"])
        # Check that the input is valid syntax
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check that the input is followed by a fullstop
            if self.symbol.type == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                # Check that name is a valid input suffix
                # JC! Need to include an input suffix out of range semantic error
                if self.symbol.id in valid_input_suffix_id_list:
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.display_error(self.symbol, self.NO_INPUT_SUFFIX,
                                       proceed=False)
            else:
                self.display_error(self.symbol, self.NO_FULLSTOP,
                                   proceed=False)
        else:
            self.display_error(self.symbol, self.UNDEFINED_NAME,
                               proceed=False)

    def monitor_list(self):
        """Parse monitor list."""
        MONITORS_ID = self.names.lookup(["MONITORS"])[0]
        # Common initial error handling
        self.initial_error_checks(MONITORS_ID, self.NO_MONITORS_KEYWORD)
        # Parse a monitor
        self.output()
        # Check if semicolon is missing but next symbol is a NAME type
        if self.symbol.type != self.scanner.SEMICOLON:
            self.display_error(
                self.symbol, self.NO_SEMICOLON, proceed=False)
        # Repeat checking monitors in list until the close brace "}"
        while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
            self.symbol = self.scanner.get_symbol()
            # Incase a KEYWORD is entered straight after a ';', assume '}' was missed and go on to END function
            if (self.symbol.type == self.scanner.KEYWORD):
                self.display_error(self.symbol, self.NO_BRACE_CLOSE)
                return
            # Incase now a brace, leave while loop
            elif self.symbol.type == self.scanner.BRACE_CLOSE:
                self.symbol = self.scanner.get_symbol()
                return
            self.output()
            # If semicolon is missing, but new NAME type symbol is entered, call error and parse to next stopping symbol
            if self.symbol.type == self.scanner.NAME:
                self.display_error(self.symbol, self.NO_SEMICOLON,
                                   proceed=False)
                # If stopping symbol reached is a semicolon, need to pass, else if brace, need to return
                if self.symbol.type == self.scanner.BRACE_CLOSE:
                    self.symbol = self.scanner.get_symbol()
                    return
                elif self.symbol.type == self.scanner.SEMICOLON:
                    pass
            # If semicolon is missing, and symbol is now a brace
            elif self.symbol.type == self.scanner.BRACE_CLOSE:
                self.display_error(self.symbol, self.NO_SEMICOLON)
                self.symbol = self.scanner.get_symbol()
                return
            # If semicolon missing and unknown symbol (including EOF)
            elif self.symbol.type != self.scanner.SEMICOLON:
                self.display_error(self.symbol, self.NO_SEMICOLON)
                return

    def end(self):
        """Parse an END keyword and check there are no symbols afterwards."""
        # Check that the final symbol is the keyword END
        END_ID = self.names.lookup(["END"])[0]
        # If nothing after monitors class, assume missing, display error and end program
        if self.symbol.type == self.scanner.EOF:
            self.display_error(self.symbol, self.NO_END_KEYWORD)
            return
        # If symbol is anything other than END, display error and pass until END keyword
        elif not (self.symbol.id == END_ID):
            self.display_error(self.symbol, self.NO_END_KEYWORD)
            self.symbol = self.scanner.get_symbol()
            # If after incorrect keyword END there is nothing, pass
            if self.symbol.type == self.scanner.EOF:
                return
            while ((self.symbol.id != END_ID) and (self.symbol.type != self.scanner.EOF)):
                self.symbol = self.scanner.get_symbol()
            # If EOF is reached and no keyword END is encountered
            if self.symbol.type == self.scanner.EOF:
                self.display_error(self.symbol, self.TERMINATE)
                return
        # If symbol is keyword END
        else:
            return

    def parse_network(self):
        """Parse the circuit definition file and return true if there are no files."""

        self.symbol = self.scanner.get_symbol()
        # Check to see if file is empty
        if self.symbol.type == self.scanner.EOF:
            self.display_error(self.symbol, self.EMPTY_FILE)
        else:
            # Parse device list
            self.device_list()

            # Parse connection list
            self.connection_list()

            # Parse monitor list
            self.monitor_list()

            # Check for END keyword
            self.end()

            # Check if there are errors, and return True if error count is zero, otherwise return falsex
            if self.error_count == 0:
                print("No errors detected ")
                return True
            elif self.error_count == 1:
                print("1 error detected")
                return False
            else:
                # Display total number of errors
                print(
                    f"Total of {str(self.error_count)} error(s) detected")
                return False


# JC! This will be deleted once development is complete
def main():
    # Check command line arguments
    file_path = "logsim/example1_logic_description.txt"
    names = Names()
    scanner = Scanner(file_path, names)
    parser = Parser(names, scanner)
    print(parser.parse_network())


if __name__ == "__main__":
    main()
