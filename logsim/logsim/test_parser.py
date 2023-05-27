"""Test the parser class"""

from names import Names
from scanner import Scanner
from parse import Parser
import pytest


@pytest.fixture
def path_fixture():
    return "logsim/logsim/example1_logic_description.txt"


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


def test_correct_initialisation(parser_fixture):
    assert parser_fixture.error_count == 0
