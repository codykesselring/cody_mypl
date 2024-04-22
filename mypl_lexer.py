"""The MyPL Lexer class.

NAME: <your name here>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_error import *


class Lexer:
    """For obtaining a token stream from a program."""

    def __init__(self, in_stream):
        """Create a Lexer over the given input stream.

        Args:
            in_stream -- The input stream. 

        """
        self.in_stream = in_stream
        self.line = 1
        self.column = 0


    def read(self):
        """Returns and removes one character from the input stream."""
        self.column += 1
        return self.in_stream.read_char()

    
    def peek(self):
        """Returns but doesn't remove one character from the input stream."""
        return self.in_stream.peek_char()

    
    def eof(self, ch):
        """Return true if end-of-file character"""
        return ch == ''

    
    def error(self, message, line, column):
        raise LexerError(f'{message} at line {line}, column {column}')

    
    def next_token(self):
        """Return the next token in the lexer's input stream."""
        # read initial character
        ch = self.read()
        lexeme = ""

        # TODO: finish the rest of the next_token function
        #removes empty space
        while(ch == "\n" or ch.isspace()):
            if ch == '\n':
                self.line += 1
                self.column = 0
            ch = self.read()
        
        #end of stream
        if self.eof(ch): 
            return Token(TokenType.EOS, "", self.line, self.column)
        
        
        #checks for comment
        if ch =='/' and self.peek() == '/': 
            start_column = self.column
            ch = self.read()
            while self.peek() != '\n' and not self.eof(ch):
                ch = self.read()
                lexeme += ch
            return Token(TokenType.COMMENT, lexeme, self.line, start_column)
        
        #checks for space
        if ch.isspace():
            return self.next_token


        #check for symbols
        if ch == ".":
            return Token(TokenType.DOT, ".", self.line, self.column)
        
        if ch == ",":
            return Token(TokenType.COMMA, ",", self.line, self.column)
        
        if ch == "(":
            return Token(TokenType.LPAREN, "(", self.line, self.column)
        
        if ch == ")":
            return Token(TokenType.RPAREN, ")", self.line, self.column)
        
        if ch == "[":
            return Token(TokenType.LBRACKET, "[", self.line, self.column)
        
        if ch == "]":
            return Token(TokenType.RBRACKET, "]", self.line, self.column)
        
        if ch == ";":
            return Token(TokenType.SEMICOLON, ";", self.line, self.column)
        
        if ch == "{":
            return Token(TokenType.LBRACE, "{", self.line, self.column)
    
        if ch == "}":
            return Token(TokenType.RBRACE, "}", self.line, self.column)
        
        if ch == "+":
            return Token(TokenType.PLUS, "+", self.line, self.column)
        
        if ch == "-":
            return Token(TokenType.MINUS, "-", self.line, self.column)
        
        if ch == "*":
            return Token(TokenType.TIMES, "*", self.line, self.column)
        
        if ch == "/":
            return Token(TokenType.DIVIDE, "/", self.line, self.column)
        
        if ch == "=":
            if(self.peek() == '='):
                self.read()
                return Token(TokenType.EQUAL, "==", self.line, self.column-1)
            else:
                return Token(TokenType.ASSIGN, "=", self.line, self.column)
                
        if ch == "!":
            if(self.peek() == '='):
                self.read()
                return Token(TokenType.NOT_EQUAL, "!=", self.line, self.column-1)
            
        if ch == "<":
            if self.peek() == '=':
                self.read()
                return Token(TokenType.LESS_EQ, "<=", self.line, self.column-1)
            
            else:
                return Token(TokenType.LESS, "<", self.line, self.column)
       
        if ch == ">":
            if self.peek() == '=':
                self.read()
                return Token(TokenType.GREATER_EQ, ">=", self.line, self.column-1)
            
            else:
                return Token(TokenType.GREATER, ">", self.line, self.column)
            
        
        #checks for string values
        if ch == '"':
            column_start = self.column
            line_start = self.line
            while self.peek() != '"':
                if self.peek() == '\n' or self.peek() == '':
                    self.error(f"Terminated string: {ch}", self.line, self.column)
                ch = self.read()
                lexeme += ch
            self.read()
            return Token(TokenType.STRING_VAL, lexeme, self.line, column_start)
            
            
        #checks for int or double
        if ch.isdecimal():
            column_start = self.column
            line_start = self.line
            num = ch
            double_bool = 0
            if ch == '0' and self.peek().isdecimal():
                 self.error(f"No leading 0's: {ch}", self.line, self.column)
                 
            while self.peek().isdecimal() or (self.peek() == '.' and double_bool == 0):
                if self.peek() == '.':
                    double_bool +=1
                    ch = self.read()
                    if not self.peek().isdecimal():
                            self.error(f"Only digits in numbers: {ch}", self.line, self.column)
                else:
                    ch = self.read()
                num+=ch
            if double_bool == 1:
                 return Token(TokenType.DOUBLE_VAL, num, line_start, column_start)
            return Token(TokenType.INT_VAL, num, line_start, column_start)
        
            
        #checks for alphabet char
        if ch.isalpha():
            column_start = self.column
            line_start = self.line
            total_string = ch

            while self.peek().isalpha() or self.peek().isdecimal() or self.peek() == "_":
                ch = self.read()
                total_string += ch

            if total_string == "struct":
                return Token(TokenType.STRUCT, total_string, line_start, column_start)
            if total_string == "array":
                return Token(TokenType.ARRAY, total_string, line_start, column_start)
            if total_string == "for":
                return Token(TokenType.FOR, total_string, line_start, column_start)
            if total_string == "while":
                return Token(TokenType.WHILE, total_string, line_start, column_start)
            if total_string == "if":
                return Token(TokenType.IF, total_string, line_start, column_start)
            if total_string == "elseif":
                return Token(TokenType.ELSEIF, total_string, line_start, column_start)
            if total_string == "else":
                return Token(TokenType.ELSE, total_string, line_start, column_start)
            if total_string == "new":
                return Token(TokenType.NEW, total_string, line_start, column_start)
            if total_string == "return":
                return Token(TokenType.RETURN, total_string, line_start, column_start)
            if total_string == "true" or total_string == "false":
                return Token(TokenType.BOOL_VAL, total_string, line_start, column_start)
            if total_string == "and":
                return Token(TokenType.AND, total_string, line_start, column_start)
            if total_string == "or":
                return Token(TokenType.OR, total_string, line_start, column_start)
            if total_string == "not":
                return Token(TokenType.NOT, total_string, line_start, column_start)
            if total_string == "void":
                return Token(TokenType.VOID_TYPE, total_string, line_start, column_start)
            if total_string == "int":
                return Token(TokenType.INT_TYPE, total_string, line_start, column_start)
            if total_string == "double":
                return Token(TokenType.DOUBLE_TYPE, total_string, line_start, column_start)
            if total_string == "bool":
                return Token(TokenType.BOOL_TYPE, total_string, line_start, column_start)
            if total_string == "string":
                return Token(TokenType.STRING_TYPE, total_string, line_start, column_start)
            if total_string == "null":
                return Token(TokenType.NULL_VAL, total_string, line_start, column_start)
            if total_string == "null":
                return Token(TokenType.NULL_VAL, total_string, line_start, column_start)
            if total_string == "class":
                return Token(TokenType.CLASS, total_string, line_start, column_start)
            else:
                return Token(TokenType.ID, total_string, line_start, column_start)
            
        
        self.error(f"Unexpected character: {ch}", self.line, self.column)
        