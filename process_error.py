"""

    Custom Error

"""


class ProcessError(Exception):

    def __init__(self, *args):
        super().__init__(args)

