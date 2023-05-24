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
from scanner import Scanner

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
    parse_network(self): Parses the circuit definition file.
    """

#    def __init__(self, names, devices, network, monitors, scanner):
    def __init__(self, names, scanner):
        """Initialise constants."""
        self.names = names
        self.scanner = scanner

        # Count number of errors
        self.error_count = 0

        # List of syntax errors
        [self.NO_DEVICES_KEYWORD, self.NO_CONNECTIONS_KEYWORD, self.NO_MONITORS_KEYWORD, self.NO_END_KEYWORD, self.NO_BRACE_OPEN, self.NO_BRACE_CLOSE,
            self.INVALID_NAME, self.NO_EQUALS, self.INVALID_COMPONENT, self.NO_LEFT_BRACKET, self.NO_RIGHT_BRACKET, self.NO_NUMBER, self.OUT_OF_RANGE,
            self.UNDEFINED_NAME, self.NO_FULLSTOP, self.NO_Q_OR_QBAR, self.NO_INPUT_SUFFIX, self.SYMBOL_AFTER_END, self.EMPTY_FILE] = self.names.unique_error_codes(19)

    def display_error(self, error_type, symbol, syntax_error=True):
        """Display the error message and where it occured

        Calls the error handling method to resume from the next available point."""
        # Increase error count by one
        self.error_count += 1

        # Display location of error
        print(f"Line {self.symbol.line_number}:", end=" ")

        if error_type == self.NO_DEVICES_KEYWORD:
            print("Syntax Error: Expected the keyword DEVICES")
        if error_type == self.NO_CONNECTIONS_KEYWORD:
            print("Syntax Error: Expected the keyword CONNECTIONS")
        if error_type == self.NO_MONITORS_KEYWORD:
            print("Syntax Error: Expected the keyword MONITORS")
        if error_type == self.NO_END_KEYWORD:
            print("Syntax Error: Expected the keyword END")
        elif error_type == self.NO_BRACE_OPEN:
            print("Sytax Error: Expected a '{' sign")
        elif error_type == self.NO_BRACE_CLOSE:
            print("Sytax Error: Expected a '}' sign")
        elif error_type == self.INVALID_NAME:
            print("Sytax Error: Invalid user name enterred")
        elif error_type == self.NO_EQUALS:
            print("Sytax Error: Expected an '=' sign")
        elif error_type == self.INVALID_COMPONENT:
            print("Sytax Error: Invalid component name enterred")
        elif error_type == self.NO_LEFT_BRACKET:
            print("Sytax Error: Expected a '(' for an input")
        elif error_type == self.NO_RIGHT_BRACKET:
            print("Sytax Error: Expected a '(' for an input")
        elif error_type == self.NO_NUMBER:
            print("Sytax Error: Expected an integer")
        elif error_type == self.OUT_OF_RANGE:
            print("Semantic Error: Input number is out of range")
        elif error_type == self.UNDEFINED_NAME:
            print("Semantic Error: Undefined device name given")
        elif error_type == self.NO_FULLSTOP:
            print("Syntax Error: Expected a full stop")
        elif error_type == self.NO_Q_OR_QBAR:
            print("Syntax Error: Expected a Q or QBAR after the full stop")
        elif error_type == self.NO_INPUT_SUFFIX:
            print("Syntax Error: Expected an input suffix")
        elif error_type == self.SYMBOL_AFTER_END:
            print("Syntax Error: There should not be any text after the keyword END")
        elif error_type == self.EMPTY_FILE:
            print("Syntax Error: Cannot parse an empty file")
        else:
            raise ValueError("Expected a valid error code")

        self.scanner.display_line_and_marker(self.symbol)
        self.error_recovery(error_type)

    def error_recovery(self, error_type):
        """Recovers from an error by resuming parsing at an appropriate point."""
        pass

    def device_list(self):
        """Parse device list"""
        DEVICES_ID = self.names.lookup(["DEVICES"])[0]
        # Check first entry in file is DEVICES
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == DEVICES_ID:
            self.symbol = self.scanner.get_symbol()
            # Check the next symbol is a "{"
            if self.symbol.type == self.scanner.BRACE_OPEN:
                self.symbol = self.scanner.get_symbol()
                self.device()
                # Check all devices in list, which are all separated by semicolons
                while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
                    self.symbol = self.scanner.get_symbol()
                    self.device()
                # Check for the end of file symbol "}"
                if self.symbol.type == self.scanner.BRACE_CLOSE:
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.display_error(self.symbol, self.NO_BRACE_CLOSE)
            else:
                self.display_error(self.symbol, self.NO_BRACE_OPEN)
        else:
            self.display_error(self.symbol, self.NO_DEVICES_KEYWORD)

    def device(self):
        """Parse user defined devices"""
        # Check that we have a valid user defined name
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check that the name is followed by an equals sign
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                # Check that we then get a valid component name
                symbol_ID, device_input = self.check_device_is_valid()
                self.symbol = self.scanner.get_symbol()
            else:
                self.display_error(self.symbol, self.NO_EQUALS)
        else:
            self.display_error(self.symbol, self.INVALID_NAME)

    def check_device_is_valid(self):
        """Returns both device type ID and the input ID"""
        [AND_ID, NAND_ID, OR_ID, NOR_ID, XOR_ID, DTYPE_ID, SWITCH_ID, CLK_ID] = self.names.lookup(
            ["AND", "NAND", "OR", "NOR", "XOR", "DTYPE",  "SWITCH", "CLK"])
        one_to_sixteen = self.names.lookup([
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"])
        binary_digit = self.names.lookup(["0", "1"])
        # Check that name is either a AND, NAND, OR, NOR gate
        if self.symbol.id in [AND_ID, NAND_ID, OR_ID, NOR_ID]:
            symbol_ID = self.symbol
            self.symbol = self.scanner.get_symbol()
            # Check that gate is followed by open bracket symbol
            if self.symbol.type == self.scanner.LEFT_BRACKET:
                self.symbol = self.scanner.get_symbol()
                # Check that number of inputs is an integer
                if self.symbol.type == self.scanner.NUMBER:
                    # Check that number is within range
                    if self.symbol.id in one_to_sixteen:
                        number_of_inputs_ID = self.symbol.id
                        self.symbol = self.scanner.get_symbol()
                        # Check that next symbol is a close bracket ")"
                        if self.symbol.type == self.scanner.RIGHT_BRACKET:
                            return symbol_ID, number_of_inputs_ID
                        else:
                            self.display_error(
                                self.symbol, self.NO_RIGHT_BRACKET)
                            return None, None
                    else:
                        # JC! Might want to make this out of range more specific
                        self.display_error(self.symbol, self.OUT_OF_RANGE)
                        return None, None
                else:
                    self.display_error(self.symbol, self.NO_NUMBER)
                    return None, None
            else:
                self.display_error(self.symbol, self.NO_LEFT_BRACKET)
                return None, None
        # Check if symbol is an XOR or DTYPE (with no inputs)
        elif self.symbol.id == XOR_ID or self.symbol.id == DTYPE_ID:
            symbol_ID = self.symbol.id
            return symbol_ID, None
        # Check if symbol is a SWITCH type
        elif self.symbol.id == SWITCH_ID:
            symbol_ID = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            # Check that gate is followed by open bracket symbol
            if self.symbol.type == self.scanner.LEFT_BRACKET:
                self.symbol = self.scanner.get_symbol()
                # Check that number of inputs is an integer
                if self.symbol.type == self.scanner.NUMBER:
                    # Check that number is within range
                    if self.symbol.id in binary_digit:
                        switch_initial_state = self.symbol.id
                        # Check that the next symbol is a closed bracket
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.RIGHT_BRACKET:
                            return symbol_ID, switch_initial_state_ID
                        else:
                            self.display_error(
                                self.symbol, self.NO_RIGHT_BRACKET)
                            return None, None
                    else:
                        # JC! Might want to make this out of range more specific
                        self.display_error(self.symbol, self.OUT_OF_RANGE)
                        return None, None
                else:
                    self.display_error(self.symbol, self.NO_NUMBER)
                    return None, None
            else:
                self.display_error(self.symbol, self.NO_LEFT_BRACKET)
                return None, None
        # Check if symbol is a CLK
        elif self.symbol.id == CLK_ID:
            symbol_ID = self.symbol.id
            self.symbol = self.scanner.get_symbol()
            # Check that the gate is followed by an open bracket symbol
            if self.symbol.type == self.scanner.LEFT_BRACKET:
                self.symbol = self.scanner.get_symbol()
                # Check that number of inputs is an integer
                if self.symbol.type == self.scanner.NUMBER:
                    number_of_cycles_ID = self.symbol.id
                    number_of_cycles = int(
                        self.names.get_name_string(self.symbol.id))
                    # Check that input number is negative (this is a semantic check!)
                    if number_of_cycles > 0:
                        # Check that the next symbol is a close bracket
                        self.symbol = self.scanner.get_symbol()
                        if self.symbol.type == self.scanner.RIGHT_BRACKET:
                            return symbol_ID, number_of_cycles_ID
                        else:
                            self.display_error(
                                self.symbol, self.NO_RIGHT_BRACKET)
                            return None, None
                    else:
                        # JC! Might want to make this out of range more specific
                        self.display_error(self.symbol, self.OUT_OF_RANGE)
                        return None, None
                else:
                    self.display_error(self.symbol, self.NO_NUMBER)
                    return None, None
            else:
                self.display_error(self.symbol, self.NO_LEFT_BRACKET)
                return None, None
        else:
            self.display_error(self.symbol, self.INVALID_COMPONENT)
            return None, None

    def connection_list(self):
        """Parse connection list"""
        CONNECTIONS_ID = self.names.lookup(["CONNECTIONS"])[0]
        # Check first symbol is "CONNECTIONS"
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == CONNECTIONS_ID:
            self.symbol = self.scanner.get_symbol()
            # Check next symbol is an open brace "{"
            if self.symbol.type == self.scanner.BRACE_OPEN:
                self.symbol = self.scanner.get_symbol()
                self.connection()
                # Repeat checking connections in list until the close brace "}"
                while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
                    self.symbol = self.scanner.get_symbol()
                    self.connection()
                if self.symbol.type == self.scanner.BRACE_CLOSE:
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.display_error(
                        self.symbol, self.NO_RIGHT_BRACKET)
            else:
                self.display_error(
                    self.symbol, self.NO_BRACE_OPEN)
        else:
            self.display_error(self.symbol, self.NO_CONNECTIONS_KEYWORD)

    def connection(self):
        """Parse a single connection line"""
        self.output(self)
        # Check ouput connection is followed by an equals sign "="
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.input(self)
        else:
            self.display_error(self.symbol, self.NO_EQUALS)

    def output(self):
        """Parse a single device output"""
        # DTYPE_ID = self.names.lookup(["DTYPE"])[0]
        valid_dtype_output_id_list = self.names.lookup(["Q", "QBAR"])
        # Check that the output to be connected is an already user-defined name
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check if gate is followed by a full stop
            if self.symbol.type == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                # Check that output suffix is Q or QBAR
                # JC! this may need to be redone to ensure semantic checking of non dtypes don't have fullstops after them
                if self.symbol.id in valid_dtype_output_id_list:
                    self.symbol = self.scanner.get_symbol()
                else:
                    self.display_error(self.symbol, self.NO_Q_OR_QBAR)

        else:
            self.display_error(self.symbol, self.UNDEFINED_NAME)

    def input(self):
        """Parse a single device input"""
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
                    self.display_error(self.symbol, self.NO_INPUT_SUFFIX)
            else:
                self.display_error(self.symbol, self.NO_FULLSTOP)
        else:
            self.display_error(self.symbol, self.UNDEFINED_NAME)

    def monitor_list(self):
        """Parse monitor list"""
        MONITORS_ID = self.names.lookup(["MONITORS"])[0]
        # Check first symbol is "MONITORS"
        if self.symbol.type == self.scanner.KEYWORD and self.symbol.id == MONITORS_ID:
            self.symbol = self.scanner.get_symbol()
            # Check that the first is a valid output name
            self.output()
            # Repeat checking monitors in list until the close brace "}"
            while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
                self.symbol = self.scanner.get_symbol()
                self.output()
            if self.symbol.type == self.scanner.BRACE_CLOSE:
                self.symbol = self.scanner.get_symbol()
        else:
            self.display_error(self.symbol, self.NO_MONITORS_KEYWORD)

    def end(self):
        """Parse an END symbol"""
        # Check that the final symbol after the } is an END symbol
        END_ID = self.names.lookup(["END"])[0]
        if self.symbol.id == END_ID:
            self.symbol = self.scanner.get_symbol()
            if self.symbol.id == self.scanner.EOF:
                # Will need to return error count, etc
                return True
            else:
                self.display_error(self.symbol, self.SYMBOL_AFTER_END)
        else:
            self.display_error(self.symbol, self.NO_END_KEYWORD)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.symbol = self.scanner.get_symbol()
        # Check to see if file is empty
        if self.symbol.type == self.scanner.EOF:
            self.display_error(self.symbol, self.EMPTY_FILE)
        else:
            # Parse device list
            self.device_list()

            # Parse connection list
            self.connection_list()

            # Parse monnitor list
            self.monitor_list()

            # Check for END keyword
            self.end()

            # Chck if there are errors
            if self.error_count == 0:
                return True
            else:
                # Display total number of errors
                print(
                    f"Total of {str(self.error_count)} error(s) detected \n")
                return False


# Return True if error count is zero, otherwise return false

# This will be deleted once develoment is complete
def main():
    # Check command line arguments
    file_path = "logsim/example1_logic_description.txt"
    names = Names()
    scanner = Scanner(file_path, names)
    parser = Parser(names, scanner)
    print(parser.parse_network())


if __name__ == "__main__":
    main()
