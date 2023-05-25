"""Map variable names and string names to unique integers.

Used in the Logic Simulator project. Most of the modules in the project
use this module either directly or indirectly.

Classes
-------
Names - maps variable names and string names to unique integers.
"""


class Names:

    """Map variable names and string names to unique integers.

    This class deals with storing grammatical keywords and user-defined words,
    and their corresponding name IDs, which are internal indexing integers. It
    provides functions for looking up either the name ID or the name string.
    It also keeps track of the number of error codes defined by other classes,
    and allocates new, unique error codes on demand.

    Parameters
    ----------
    No parameters.

    Public methods
    -------------
    unique_error_codes(self, num_error_codes): Returns a list of unique integer
                                               error codes.

    query(self, name_string): Returns the corresponding name ID for the
                        name string. Returns None if the string is not present.

    lookup(self, name_string_list): Returns a list of name IDs for each
                        name string. Adds a name if not already present.

    get_name_string(self, name_id): Returns the corresponding name string for
                        the name ID. Returns None if the ID is not present.
    """

    def __init__(self):
        """Initialise names list."""
        self.error_code_count = 0  # how many error codes have been declared
        self.names_list = []  # initiate names_list

    def unique_error_codes(self, num_error_codes):
        """Return a list of unique integer error codes."""
        if not isinstance(num_error_codes, int):
            raise TypeError("Expected num_error_codes to be an integer.")
        elif num_error_codes < 0:
            raise ValueError(
                "Expected num_error_codes to be a positive integer.")
        self.error_code_count += num_error_codes
        return range(self.error_code_count - num_error_codes,
                     self.error_code_count)

    def query(self, name_string):
        """Return the corresponding name ID for name_string.

        If the name string is not present in the names list, return None.
        """
        # Check if name_string is a string
        if not isinstance(name_string, str):
            raise TypeError('Expected name_string to be a string argument.')
        # Return None if name_string is not in names_list
        elif name_string not in self.names_list:
            return None
        return self.names_list.index(name_string)

    def lookup(self, name_string_list):
        """Return a list of name IDs for each name string in name_string_list.

        If the name string is not present in the names list, add it.
        """
        name_ID_list = []
        # Check if name_string_list is a list
        if not isinstance(name_string_list, list):
            raise TypeError('Expected name_string_list to be a list argument.')
        else:
            for name in name_string_list:
                # Check if name in name_string_list is a string
                if not isinstance(name, str):
                    raise TypeError(
                        'Expected name in name_string_list to be a string argument.')
                # If name is not in names_list, append it
                elif name not in self.names_list:
                    self.names_list.append(name)
                # Append name ID to name_ID_list
                name_ID_list.append(self.names_list.index(name))
            return name_ID_list

    def get_name_string(self, name_id):
        """Return the corresponding name string for name_id.

        If the name_id is not an index in the names list, return None.
        """
        # Check if name_id is an integer, else raise an error
        if not isinstance(name_id, int):
            raise TypeError('Expected name_id to be an integer argument.')
        # Check if name_id is positive, else raise an error
        elif name_id < 0:
            raise ValueError(
                'Expected name_id to be a positive integer argument.')
        # Check if name_id is within the index range of names_list, else return None
        elif name_id >= len(self.names_list):
            return None
        return self.names_list[name_id]
