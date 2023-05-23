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
                    print("Expected a } to close the devices list")
            else:
                print("expected an open brace")
        else:
            print("expected \"DEVICES\" as keyword")

    def device(self):
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
                    print(
                        "Expected a valid name specifying a device, starting with a letter")
            else:
                print("Expected an equals sign after user name for device")
        else:
            print("Expected a user defined name.")

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
                            print("Expected a close bracket after input number")
                            return None, None
                    else:
                        print("Expected an input number between 1 and 16 inclusive")
                        return None, None
                else:
                    print("Expected a number as an input")
                    return None, None
            else:
                print("Expected bracket then an input for AND NAND NOR OR gates")
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
                        return symbol_ID, switch_initial_state_ID
                    else:
                        print(
                            "Expected a binary digit to specify initial switch state")
                        return None, None
                else:
                    print("Expected a number as an input")
                    return None, None
            else:
                print("Expected bracket then an input for AND NAND NOR OR gates")
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
                        print("Expected a positive integer")
                        return None, None
                else:
                    print(
                        "Expected an integer for number of cycles of each clock half period")
                    return None, None
            else:
                print("Expected bracket then an input for AND NAND NOR OR gates")
                return None, None
        else:
            print("Ensure your device name is one of the valid device names")
            return None, None

    def connection_list(self):
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
                    print("Expected a } after connections list")
            else:
                print("Expected a { after CONNECTIONS")
        else:
            print("expected \"CONNECTIONS\" keyword")

    def connection(self):
        """Parse a single connection line"""
        self.output()
        # Check ouput connection is followed by an equals sign "="
        if self.symbol.type == self.scanner.EQUALS:
            self.symbol = self.scanner.get_symbol()
            self.input()
        else:
            error("Need to follow the output connection with an equals")

    def output(self):
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
                        print("Expected name to be either Q or QBAR.")
                else:
                    print("Expected name after fullstop")
        else:
            print("Expected a device name")

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
                # Check that there is an input suffix
                if self.symbol.type == self.scanner.NAME:
                    # Check that name is a valid input suffix
                    if self.symbol.id in valid_input_suffix_id_list:
                        self.symbol = self.scanner.get_symbol()
                    else:
                        print("Expected a valid input suffix")
            else:
                print("Expected a full stop followed by an input suffix")
        else:
            print("Expected a device name to specify the input for")

    def monitor_list(self):
        """Parse monitor list"""
        # Check that the first is a valid output name
        self.output()
        # Repeat checking connections in list until the close brace "}"
        while ((self.symbol.type == self.scanner.SEMICOLON) and (self.symbol.type != self.scanner.BRACE_CLOSE)):
            self.symbol = self.scanner.get_symbol()
            self.output()
        if self.symbol.type == self.scanner.BRACE_CLOSE:
            self.symbol = self.scanner.get_symbol()

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
                print("Cannot have any text after END symbol")
        else:
            print("Expected END keyword to signify end of file")

    def parse_network(self):
        """Parse the circuit definition file."""
        # For now just return True, so that userint and gui can run in the
        # skeleton code. When complete, should return False when there are
        # errors in the circuit definition file.
        self.symbol = self.scanner.get_symbol()
        # Check to see if file is empty
        if self.symbol.type == self.scanner.EOF:
            print("Cannot parse an empty text file.")
        else:
            # Parse device list
            self.device_list()
            # Parse connection list
            self.connection_list()

            # Parse monnitor list
            self.monitor_list()

            # Check for END keyword
            self.end()
        return True


# Return True if error count is zero, otherwise return false


def main():
    # Check command line arguments
    file_path = "logsim/example1_logic_description.txt"
    names = Names()
    scanner = Scanner(file_path, names)
    parser = Parser(names, scanner)
    print(parser.parse_network())


if __name__ == "__main__":
    main()
