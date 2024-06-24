"""The MyPL Lexer class.

NAME: Cody Kesselring
DATE: Spring 2024

"""


class StdInWrapper:
    """Standard input wrapper for reading and peeking."""

    def __init__(self, stream):
        self.stream = stream.buffer
        
    def read_char(self):
        """Returns and removes a single character in stream."""
        return self.stream.read(1).decode('utf-8')

    def peek_char(self):
        """Returns next character in stream to be read."""
        if not self.stream.peek(1):
            return ''
        return self.stream.peek(1).decode('utf-8')[0]

    def close(self):
        """Closes the stream."""
        pass # nothing to do


    
class FileWrapper:
    """File input wrapper for reading and peeking."""

    def __init__(self, stream):
        self.stream = stream

    def read_char(self):
        """Returns and removes a single character in stream."""
        return self.stream.read(1)

    def peek_char(self):
        """Returns next character in stream to be read."""
        loc = self.stream.tell()
        ch = self.read_char()
        self.stream.seek(loc)
        return ch

    def close(self):
        """Closes the stream."""
        self.stream.close()
        

