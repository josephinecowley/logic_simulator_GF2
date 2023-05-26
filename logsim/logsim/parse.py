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

    display_error(self, symbol, error_type, proceed=False, stopping_symbol_type=6): Display the error message and where it occured.
    Calls the error handling method to resume from the next available point.

    error_recovery(self, error_type, proceed, stopping_symbol): Recover from an error by resuming parsing at an appropriate point specified by the stopping_symbol.

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

        # Count number of errors
        self.error_count = 0

        # List of syntax errors
        # JC! come back and change this to a dictionary such that manual changes to number of errors is unecessary
        [self.NO_DEVICES_KEYWORD, self.NO_CONNECTIONS_KEYWORD, self.NO_MONITORS_KEYWORD, self.NO_END_KEYWORD, self.NO_BRACE_OPEN, self.NO_BRACE_CLOSE,
            self.INVALID_NAME, self.NO_EQUALS, self.INVALID_COMPONENT, self.NO_BRACKET_OPEN, self.NO_BRACKET_CLOSE, self.NO_NUMBER, self.OUT_OF_RANGE,
            self.UNDEFINED_NAME, self.NO_FULLSTOP, self.NO_Q_OR_QBAR, self.NO_INPUT_SUFFIX, self.SYMBOL_AFTER_END, self.EMPTY_FILE] = self.names.unique_error_codes(19)

    # Stopping symbol is automatically assigned to a semi-colon
    def display_error(self,  symbol, error_type,  proceed=True, stopping_symbol_type=6):
        """Display the error message and where it occured

        Calls the error handling method to resume from the next available point."""

        # Exception handling
        if not isinstance(error_type, int):
            raise TypeError(
                "Expected error_type to be an integer type argument")
        elif error_type >= 19:
            raise ValueError(
                "Expected an error code within range of error types")
        elif error_type < 0:
            raise ValueError("Cannot have a negative error code")
        elif not isinstance(symbol, Symbol):
            raise TypeError("Expected an instance of the Symbol class")
        elif not isinstance(stopping_symbol_type,  int):
            raise TypeError(
                "Expected stopping symbol to be an integer type argument")
        elif ((stopping_symbol_type >= 12) or (stopping_symbol_type <= 0)):
            raise ValueError(
                "Expected stopping symbol to be within range of given symbols")
        elif not isinstance(proceed, bool):
            raise TypeError("Expected bool type argument for proceed")

        # Increase error count by one
        self.error_count += 1

        # Display location and type of error
        print(f"Line {self.symbol.line_number}:", end=" ")
        if error_type == self.NO_DEVICES_KEYWORD:
            print("Syntax Error: Expected the keyword DEVICES")
        elif error_type == self.NO_CONNECTIONS_KEYWORD:
            print("Syntax Error: Expected the keyword CONNECTIONS")
        elif error_type == self.NO_MONITORS_KEYWORD:
            print("Syntax Error: Expected the keyword MONITORS")
        elif error_type == self.NO_END_KEYWORD:
            print("Syntax Error: Expected the keyword END")
        elif error_type == self.NO_BRACE_OPEN:
            print("Syntax Error: Expected a '{' sign")
        elif error_type == self.NO_BRACE_CLOSE:
            print("Syntax Error: Expected a '}' sign")
        elif error_type == self.INVALID_NAME:
            print("Syntax Error: Invalid user name enterred")
        elif error_type == self.NO_EQUALS:
            print("Syntax Error: Expected an '=' sign")
        elif error_type == self.INVALID_COMPONENT:
            print("Syntax Error: Invalid component name enterred")
        elif error_type == self.NO_BRACKET_OPEN:
            print("Syntax Error: Expected a '(' for an input")
        elif error_type == self.NO_BRACKET_CLOSE:
            print("Syntax Error: Expected a ')' for an input")
        elif error_type == self.NO_NUMBER:
            print("Syntax Error: Expected an integer")
        elif error_type == self.OUT_OF_RANGE:
            print("Semantic Error: Input number is out of range")
        elif error_type == self.UNDEFINED_NAME:
            print("Semantic Error: Undefined device name given")
        elif error_type == self.NO_FULLSTOP:
            print("Syntax Error: Expected a full stop")
        elif error_type == self.NO_Q_OR_QBAR:
            print("Syntax Error: Expected a Q or QBAR after the full stop")
        elif error_type == self.NO_INPUT_SUFFIX:
            print("Syntax Error: Expected a valid input suffix")
        elif error_type == self.SYMBOL_AFTER_END:
            print("Syntax Error: There should not be any text after the keyword END")
        elif error_type == self.EMPTY_FILE:
            print("Syntax Error: Cannot parse an empty file")
        else:
            raise ValueError("Expected a valid error code")

        # Display error line and visual marker
        self.scanner.display_line_and_marker(self.symbol)
        # Call error recovery function to resume parsing at appropriate point
        self.error_recovery(error_type, proceed, stopping_symbol_type)

    def error_recovery(self, error_type, proceed=True, stopping_symbol_type=6):
        """Recover from an error by resuming parsing at an appropriate point."""

        # Exception handling
        if not isinstance(error_type, int):
            raise TypeError(
                "Expected error_type to be an integer type argument")
        # JC! need to fix this to not rely on a '19'
        elif error_type >= 19:
            raise ValueError(
                "Expected an error code within range of error types")
        elif error_type < 0:
            raise ValueError("Cannot have a negative error code")
        elif not isinstance(proceed, bool):
            raise TypeError("Expected bool type argument for proceed")
        elif not isinstance(stopping_symbol_type, int):
            raise TypeError(
                "Expected stopping symbol to be an integer type argument")
        elif ((stopping_symbol_type >= 12) or (stopping_symbol_type <= 0)):
            raise ValueError(
                "Expected stopping symbol to be within range of given symbols")

        # Check if we have already built in error handling (have done so for obvious semantic errors, e.g. missing KEYWORD). If so, just pass
        if proceed == True:
            return
        # Check if we need to skip symbols to recover parsing
        else:
            while ((self.symbol.type != stopping_symbol_type) and (self.symbol.type != self.scanner.EOF)):
                self.symbol = self.scanner.get_symbol()
            if self.symbol.type == stopping_symbol_type:
                return

    def device_list(self):
        """Parse device list."""
        DEVICES_ID = self.names.lookup(["DEVICES"])[0]
        # If DEVICES is missing, assume just missing and proceed to check if { is present
        if not (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == DEVICES_ID):
            self.display_error(self.symbol, self.NO_DEVICES_KEYWORD)
            self.symbol = self.scanner.get_symbol()
            # Check if there's also a missing { after missing DEVICES. If so just pass to next symbol
            if not (self.symbol.type == self.scanner.BRACE_OPEN):
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
            # If only missing DEVICES keyword, advance symbol to NAME
            else:
                self.symbol = self.scanner.get_symbol()
        # If DEVICES keyword is present
        else:
            self.symbol = self.scanner.get_symbol()
            # Check the next symbol is a "{". If not, assume missing and proceed to next symbol
            if not (self.symbol.type == self.scanner.BRACE_OPEN):
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
            # If not missing either, advance symbol to NAME
            else:
                self.symbol = self.scanner.get_symbol()
        # Parse device
        self.device()
        # Check all devices in list, which are all separated by semicolons
        while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
            self.symbol = self.scanner.get_symbol()
            # Incase a KEYWORD is enterred straight after a ';', assume '{' was missed
            if (self.symbol.type == self.scanner.KEYWORD):
                self.display_error(self.symbol, self.NO_BRACE_CLOSE)
                return
            self.device()
        # Check for the end of file symbol "}"
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            self.symbol = self.scanner.get_symbol()
            return
        # If something other than '}', assume it is simply missing
        else:
            self.display_error(self.symbol, self.NO_BRACE_CLOSE)

    def device(self):
        """Parse user defined device."""
        # Check that we have a valid user defined name
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            return
        elif self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check that the name is followed by an equals sign
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                # Check that we then get a valid component name
                # JC! May need to change this assignment, but atm I believe this will be useful for creating the network
                symbol_ID, device_input = self.check_device_is_valid()
            else:
                self.display_error(self.symbol, self.NO_EQUALS, proceed=False)
        else:
            self.display_error(self.symbol, self.INVALID_NAME, proceed=False)

    def check_device_is_valid(self):
        """Check if device is valid and return both device type ID and the input ID."""
        [AND_ID, NAND_ID, OR_ID, NOR_ID, XOR_ID, DTYPE_ID, SWITCH_ID, CLK_ID] = self.names.lookup(
            ["AND", "NAND", "OR", "NOR", "XOR", "DTYPE",  "SWITCH", "CLK"])
        one_to_sixteen = range(1, 16)
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
                        # JC! Might want to make this out of range more specific.
                        self.display_error(self.symbol, self.OUT_OF_RANGE,
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
                    if self.symbol.id in binary_digit:
                        switch_initial_state_ID = self.symbol.id
                        # Check that the next symbol is a closed bracket
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.BRACKET_CLOSE:
                            self.symbol = self.scanner.get_symbol()
                            return symbol_ID, switch_initial_state_ID
                        else:
                            self.display_error(
                                self.symbol, self.NO_BRACKET_CLOSE,
                                proceed=False)
                            return None, None
                    else:
                        # JC! Might want to make this out of range more specific
                        self.display_error(self.symbol, self.OUT_OF_RANGE,
                                           proceed=False, stopping_symbol_type=self.scanner.SEMICOLON)
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
                    number_of_cycles = self.symbol.id
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
                        # JC! Might want to make this out of range more specific
                        self.display_error(self.symbol, self.OUT_OF_RANGE,
                                           proceed=False, stopping_symbol_type=self.scanner.SEMICOLON)
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
        # If CONNECTIONS keyword is missing, proceed to next symbol
        if not ((self.symbol.type == self.scanner.KEYWORD) and (self.symbol.id == CONNECTIONS_ID)):
            self.display_error(self.symbol, self.NO_CONNECTIONS_KEYWORD)
            self.symbol = self.scanner.get_symbol()
            # If { is also missing, proceed to next symbol
            if not self.symbol.type == self.scanner.BRACE_OPEN:
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
            # If '{' is present
            else:
                self.symbol = self.scanner.get_symbol()
        # If CONNECTIONS keyword is present
        else:
            self.symbol = self.scanner.get_symbol()
            # If { is missing, proceed to next symbol
            if not self.symbol.type == self.scanner.BRACE_OPEN:
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
            # Both CONNECTIONS keyword and { are present
            else:
                self.symbol = self.scanner.get_symbol()
        # Parse a connection
        self.connection()
        # Repeat checking connections in list until the close brace "}"
        while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
            self.symbol = self.scanner.get_symbol()
            # Incase a KEYWORD is enterred straight after a ';', assume '{' was missed
            if (self.symbol.type == self.scanner.KEYWORD):
                self.display_error(self.symbol, self.NO_BRACE_CLOSE)
                return
            self.connection()
        # Check for the end of file symbol "}"
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            self.symbol = self.scanner.get_symbol()
            return
        # If something other than '}', assume it is missing
        else:
            self.display_error(
                self.symbol, self.NO_BRACE_CLOSE)

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
        # If after the semicolon we have a } , assume we can move onto the monitor_list
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
            self.display_error(self.symbol, self.UNDEFINED_NAME, proceed=False)

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
        # Check first symbol is "MONITORS". If not, assume missing and proceed to the next {
        if not ((self.symbol.type == self.scanner.KEYWORD) and (self.symbol.id == MONITORS_ID)):
            self.display_error(self.symbol, self.NO_MONITORS_KEYWORD)
            self.symbol = self.scanner.get_symbol()
            # If '{' is also missing, throw error and proceed to next symbol
            if not (self.symbol.type == self.scanner.BRACE_OPEN):
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
            # If '{' is present, proceed to next symbol
            else:
                self.symbol = self.scanner.get_symbol()
        # If MONITORS keyword is present
        else:
            self.symbol = self.scanner.get_symbol()
            # If '{' is missing, throw error and proceed to next symbol
            if not (self.symbol.type == self.scanner.BRACE_OPEN):
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
            # If neither MONITORS keyword nor { is missing, proceed to next symbol
            else:
                self.symbol = self.scanner.get_symbol()
        # Check a monitor is a valid output name
        self.output()
        # Repeat checking monitors in list until the close brace "}"
        while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
            self.symbol = self.scanner.get_symbol()
            self.output()
        # Check for the end of file symbol "}"
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            self.symbol = self.scanner.get_symbol()
            return
        # If something other than '}', assume it is missing
        else:
            self.display_error(self.symbol, self.NO_BRACE_CLOSE)

    def end(self):
        """Parse an END keyword and check there are no symbols afterwards."""
        # Check that the final symbol after the } is an END symbol
        END_ID = self.names.lookup(["END"])[0]
        if not (self.symbol.id == END_ID):
            self.display_error(self.symbol, self.NO_END_KEYWORD,
                               proceed=True, stopping_symbol_type=self.scanner.BRACE_OPEN)
        self.symbol = self.scanner.get_symbol()
        if self.symbol.type == self.scanner.EOF:
            # Will need to return error count, etc
            return
        else:
            self.display_error(self.symbol, self.SYMBOL_AFTER_END)

    def parse_network(self):
        """Parse the circuit definition file and return true if there are no files."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.

        self.symbol = self.scanner.get_symbol()
        # Check to see if file is empty
        if self.symbol.type == self.scanner.EOF:
            self.display_error(self.symbol, self.EMPTY_FILE)
        else:
            # Parse device list
            # self.device_list()

            # Parse connection list
            # self.connection_list()

            # Parse monitor list
            self.monitor_list()

            # Check for END keyword
            # self.end()

            # Check if there are errors, and return True if error count is zero, otherwise return falsex
            if self.error_count == 0:
                print("No errors detected")
                return True
            else:
                # Display total number of errors
                print(
                    f"Total of {str(self.error_count)} error(s) detected \n")
                return False


# JC! This will be deleted once develoment is complete
def main():
    # Check command line arguments
    file_path = "logsim/example1_logic_description.txt"
    names = Names()
    scanner = Scanner(file_path, names)
    parser = Parser(names, scanner)
    print(parser.parse_network())


if __name__ == "__main__":
    main()
