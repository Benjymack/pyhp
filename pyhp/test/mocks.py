from pyhp.pyhp import PyhpProtocol


class MockPyhp(PyhpProtocol):
    def __init__(self, debug: bool = False):
        self._debug = debug

    @property
    def debug(self) -> bool:
        return self._debug
