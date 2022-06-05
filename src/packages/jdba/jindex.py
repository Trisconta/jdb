# jindex.py  (c)2022  Henrique Moreira

""" AData/ DData indexing
"""

# pylint: disable=missing-function-docstring


class GeneralIndex():
    """ Abstract class for indexing
    """
    def __init__(self, name=""):
        assert isinstance(name, str)
        self.name = name
        self.byname = {}

class JIndex(GeneralIndex):
    """ J-son based indexing
    """
    def __init__(self, name=""):
        super().__init__(name)
        self._seqid = {}

    def get_sequence_ids(self) -> dict:
        return self._seqid

    def initialized(self) -> bool:
        return len(self.byname) > 0
