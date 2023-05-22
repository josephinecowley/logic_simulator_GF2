"""Parse the definition file and build the logic network.

Used in the Logic Simulator project to analyse the syntactic and semantic
correctness of the symbols received from the scanner and then builds the
logic network.

Classes
-------
Parser - parses the definition file and builds the logic network.
"""
from names import Names
# Will need to add more imports
from scanner import Scanner


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

    def __init__(self, names, devices, network, monitors, scanner):
        """Initialise constants."""
        self.names = names
        self.scanner = scanner

    def device_list(self):
        """Parse device list"""
        DEVICES_ID = self.names.lookup(["DEVICES"])
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
                    self.devce()
                # Check for the end of file symbol "}"
                if self.symbol.type == self.scanner.BRACE_CLOSE:
                    self.symbol = self.scanner.get_symbol()
                else:
                    error("Expected a } to close the devices list")
            else:
                error("expected an open brace")

        else:
            error("expected \"DEVICES\" as keyword")

    def device():
        """Parse user defined devices"""
        # Check that we have a valid user defined name
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check that the name is followed by an equals sign
            if self.symbol.type == self.scanner.EQUALS:
                self.symbol = self.scanner.get_symbol()
                # Check that we then get a device name
                if self.symbol.type == self.scanner.NAME:
                    symbol_ID, device_input = self.check_device_is_valid()
                    self.symbol = self.scanner.get_symbol()
            else:
                error("Expected an equals sign after user name for device")
        else:
            error("Expected a user defined name.")

    def check_device_is_valid():
        """Returns the device type and the input"""
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
                        number_of_inputs = self.symbol
                        self.symbol = self.scanner.get_symbol()
                        # Check that next symbol is a close bracket ")"
                        if self.symbol.type == self.scanner.RIGHT_BRACKET:
                            return symbol_ID, number_of_inputs
                        else:
                            error("Expected a close bracket after input number")
                            return None, None
                    else:
                        error("Expected an input number between 1 and 16 inclusive")
                        return None, None
                else:
                    error("Expected a number as an input")
                    return None, None
            else:
                error("Expected bracket then an input for AND NAND NOR OR gates")
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
                        switch_initial_state = self.symbol
                        return symbol_ID, switch_initial_state
                    else:
                        error(
                            "Expected a binary digit to specify initial switch state")
                        return None, None
                else:
                    error("Expected a number as an input")
                    return None, None
            else:
                error("Expected bracket then an input for AND NAND NOR OR gates")
                return None, None

        # Check if symbol is a CLK

        else:
            error("Ensure your device name is one of the valid device names")
            return None, None

    def connection_list():
        """Parse connection list"""
        CONNECTIONS_ID = self.names.lookup(["CONNECTIONS"])
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
                    error("Expected a } after connections list")
            else:
                error("Expected a { after CONNECTIONS")
        else:
            error("expected \"CONNECTIONS\" keyword")

    def connection():
        """Parse a single connection line"""
        self.output()
        # Check ouput connection is followed by an equals sign "="
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.getsymbol()
            self.input()
        else:
            error("Need to follow the output connection with an equals")

    def output():
        """Parse a single device output"""
        valid_dtype_output_id_list = self.names.lookup(["Q", "QBAR"])
        # Check that the output to be connected is a name
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check if output is followed by a full stop
            if self.symbol.type == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                # Check that the next symbol is a name
                if self.symbol.type == self.scanner.NAME:
                    # Check that output suffix is Q or QBAR
                    if self.symbol.id in valid_dtype_output_id_list:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        error("Expected name to be either Q or QBAR.")
                else:
                    error("Expected name after fullstop")
        else:
            error("Expected a device name")

    def input():
        """Parse a single device input"""
        valid_input_suffix_id_list = self.names.lookup(["I1", "I2", "I3", "I4", "I5", "I6", "I7", "I8", "I9",
                                                        "I10", "I11", "I12", "I13", "I14", "I15", "I16", "DATA", "CLK", "SET", "CLEAR"])
        # Check that the input is valid syntax
        if self.symbol.type == self.scanner.NAME:
            self.symbol = self.scanner.get_symbol()
            # Check that the input is followed by a fullstop
            if self.symbol.type == self.scanner.FULLSTOP:
                self.symbol = self.scanner.get_symbol()
                # Check that there is an input suffix
                if self.symbol.type == self.scanner.NAME:
                    # Check that name is a valid input suffix
                    if self.symbol.id in valid_input_suffix_id_list:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        error("Expected a valid input suffix")
            else:
                error("Expected a full stop followed by an input suffix")
        else:
            error("Expected a device name to specify the input for")

    def monitor_list():
        pass

    def error(string):
        print(string)

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.symbol = self.scanner.getsymbol()
        # Check to see if file is empty
        # if file empty, throw an error
        if self.symbol.type == self.scanner.EOF:
            error("Cannot parse an empty text file.")
        else:
            # Parse device list
            self.device_list()

            # Parse connection list
            self.connection_list()

            # Parse monnitor list
            self.monitor_list()

            # Check for the END of file

            # Return True if error count is zero, otherwise return false

        return True
