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
        names = Names()

    def device_list(self):
        """Parse device list"""
        DEVICES_ID = self.names.lookup(["DEVICES"])
        if (self.symbol.type == self.scanner.KEYWORD and self.symbol.id == DEVICES_ID):
            self.symbol = self.scanner.get_symbol()
            if (self.symbol.type == self.scanner.BRACE_OPEN):
                self.symbol = self.scanner.get_symbol()
            else:
                error("expected an open brace")

        else:
            error("expected \"DEVICES\" as keyword")
        pass

    def device():
        pass

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
                while self.symbol.type == self.scanner.SEMICOLON and != self.scanner.BRACE_CLOSE:
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

    def input():
        """Parse a single device output"""
        pass

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
        # if file empty: throw error

        # Parse device list
        self.device_list()

        # Parse connection list
        self.connection_list()

        # Parse monnitor list
        self.monitor_list()

        return True
