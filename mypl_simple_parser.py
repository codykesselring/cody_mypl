"""MyPL simple syntax checker (parser) implementation.

NAME: <your-name-here>
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *


class SimpleParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None

        
    def parse(self):
        """Start the parser."""
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT):
                self.struct_def()
            else:
                self.fun_def()
        self.eat(TokenType.EOS, 'expecting EOF')

        
    #----------------------------------------------------------------------
    # Helper functions
    #----------------------------------------------------------------------

    def error(self, message):
        """Raises a formatted parser error.

        Args:
            message -- The basic message (expectation)

        """
        lexeme = self.curr_token.lexeme
        line = self.curr_token.line
        column = self.curr_token.column
        err_msg = f'{message} found "{lexeme}" at line {line}, column {column}'
        raise ParserError(err_msg)


    def advance(self):
        """Moves to the next token of the lexer."""
        self.curr_token = self.lexer.next_token()
        # skip comments
        while self.match(TokenType.COMMENT):
            self.curr_token = self.lexer.next_token()

            
    def match(self, token_type):
        """True if the current token type matches the given one.

        Args:
            token_type -- The token type to match on.

        """
        return self.curr_token.token_type == token_type

    
    def match_any(self, token_types):
        """True if current token type matches on of the given ones.

        Args:
            token_types -- Collection of token types to check against.

        """
        for token_type in token_types:
            if self.match(token_type):
                return True
        return False

    
    def eat(self, token_type, message):
        """Advances to next token if current tokey type matches given one,
        otherwise produces and error with the given message.

        Args: 
            token_type -- The totken type to match on.
            message -- Error message if types don't match.

        """
        if not self.match(token_type):
            self.error(message)
        self.advance()

        
    def is_bin_op(self):
        """Returns true if the current token is a binary operation token."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)

    
    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------
        
    def struct_def(self):
        """Check for well-formed struct definition."""
        # TODO
        self.advance()
        self.eat(TokenType.ID, "expecting struct name")
        self.eat(TokenType.LBRACE, "expecting left brace")
        self.fields()
        self.eat(TokenType.RBRACE, "expecting closing brace")
        
    def fields(self):
        """Check for well-formed struct fields."""
        # TODO
        while not self.match(TokenType.RBRACE):
            self.data_type()
            self.eat(TokenType.ID, "expecting variable name")
            self.eat(TokenType.SEMICOLON, "expecting semicolon")
           
            
    def fun_def(self):
        """Check for well-formed function definition."""
        # TODO
        if self.match_any([TokenType.ID,TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.VOID_TYPE]):
            self.advance()
        else:
            self.error("function needs data type")
        self.eat(TokenType.ID, "expecting id")
        self.eat(TokenType.LPAREN, "expect left paren")
        self.params()
        self.eat(TokenType.RPAREN, "missing closing paren")
        self.eat(TokenType.LBRACE, "expect left brace")
        while not self.match(TokenType.RBRACE):
            self.stmt()
        self.advance()


    def params(self):
        """Check for well-formed function formal parameters."""
        # TODO
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.VOID_TYPE, TokenType.ARRAY, TokenType.ID]):
            self.data_type()
            self.eat(TokenType.ID, "expecting id")
            while not self.match(TokenType.RPAREN):
                self.eat(TokenType.COMMA, "expecting comma")
                self.data_type()
                self.eat(TokenType.ID, "expecting id")


        
    # TODO: Define the rest of the needed recursive descent functions
    def parse(self):
        self.advance()
        self.program()
        self.eat(TokenType.EOS, "expecting eos")

    def program(self):
        while self.match_any([TokenType.ARRAY, TokenType.ID,TokenType.STRUCT, TokenType.VOID_TYPE, TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            if self.match(TokenType.ARRAY):
                self.advance()
            if self.match_any([TokenType.ID, TokenType.VOID_TYPE, TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
                self.fun_def()
            else:
                self.struct_def()

    def data_type(self):
        if self.match(TokenType.ARRAY):
            self.advance()
            if self.match(TokenType.ID):
                self.advance()
            else:
                self.base_type()
        elif self.match(TokenType.ID):
            self.advance()
        else:
            self.base_type()

    def base_type(self):
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            self.advance()
        else:
            self.error("not a base type")

    def stmt(self):
        if self.match(TokenType.IF):
            self.if_stmt()
        elif self.match(TokenType.WHILE):
            self.while_stmt()   
        elif self.match(TokenType.FOR):
            self.for_stmt()
        elif self.match(TokenType.RETURN):
            self.return_stmt()
            self.eat(TokenType.SEMICOLON, "expecting semicolon")

        elif self.match_any([TokenType.ID, TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY]):
            self.lvalue()
            if self.match(TokenType.RPAREN):
                self.eat(TokenType.SEMICOLON, "expecting semicolon")
            elif self.match(TokenType.ASSIGN):
                self.assign_stmt()
                self.eat(TokenType.SEMICOLON, "expecting semicolonn")
            elif self.match_any([TokenType.ID, TokenType.SEMICOLON, TokenType.DOT]):
                self.vdecl_stmt()
        else:
            self.error("invalid statement")

    def if_stmt(self):
        self.advance()
        self.eat(TokenType.LPAREN, "expecting left paren")
        if self.match(TokenType.RPAREN):
            self.error("must have expr in if statement")
        self.expr()
        self.eat(TokenType.RPAREN, "expecting right paren")
        self.eat(TokenType.LBRACE, "expecting left brace")
        while not self.match(TokenType.RBRACE):
            self.stmt()
        self.eat(TokenType.RBRACE, "expecting clsoing brace")
        self.if_stmt_t()
    
    def if_stmt_t(self):
        has_else = False
        while self.match_any([TokenType.ELSEIF, TokenType.ELSE]):
            if self.match(TokenType.ELSEIF):
                if has_else:
                    self.error("else out of order")
                self.advance()
                self.eat(TokenType.LPAREN, "expecting left paren")
                self.expr()
                self.eat(TokenType.RPAREN, "expecting right paren")
                self.eat(TokenType.LBRACE, "expecting left brace")
                while not self.match(TokenType.RBRACE):
                    self.stmt()
                self.advance()
                self.if_stmt_t()
            elif self.match(TokenType.ELSE):
                if has_else:
                    self.error("else out of order")
                has_else = True
                self.advance()
                self.eat(TokenType.LBRACE, "expecting left brace")
                while not self.match(TokenType.RBRACE):
                    self.stmt()
                self.advance()
    
    def while_stmt(self):
        self.advance()
        self.eat(TokenType.LPAREN, "expecting elft paren")
        if self.match(TokenType.RPAREN):
            self.error("while loop must have param")
        self.expr()
        self.eat(TokenType.RPAREN, "expecting right paren")
        self.eat(TokenType.LBRACE, "expecting left brace")
        while not self.match(TokenType.RBRACE):
            self.stmt()
        self.advance()
    
    def for_stmt(self):
        self.advance()
        self.eat(TokenType.LPAREN, "expecting left paren")
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY, TokenType.ID]):
            self.advance()
        self.eat(TokenType.ID, "expecting id")
        self.vdecl_stmt()
        self.expr()
        self.eat(TokenType.SEMICOLON, "expecting semicolon")
        self.eat(TokenType.ID, "expecting id")
        self.assign_stmt()
        self.eat(TokenType.RPAREN, "expecting right paren")
        self.eat(TokenType.LBRACE, "expecting left brace")
        while not self.match(TokenType.RBRACE):
            self.stmt()
        self.advance()
    
    def return_stmt(self):
        self.advance()
        if self.match(TokenType.SEMICOLON):
            self.error("must have expression after return")
        

    def vdecl_stmt(self):
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID, TokenType.ARRAY]):
            self.advance()
        
        if self.match(TokenType.DOT):
            while self.match(TokenType.DOT):
                self.var_rvalue()
            
            
        if self.match(TokenType.ASSIGN):
            self.advance()
            if self.match(TokenType.SEMICOLON):
                self.error("must have expression")
            self.expr()
        self.eat(TokenType.SEMICOLON, "expecting semicolon2")
    
    def assign_stmt(self):
        self.eat(TokenType.ASSIGN, "expecting assignnnn")
        if self.match(TokenType.SEMICOLON):
            self.error("must have expression")
        self.expr()

    def lvalue(self):
        if self.match(TokenType.ARRAY):
                self.advance()
        self.advance()

        if self.match(TokenType.LBRACKET):
            self.advance()
            self.expr()
            self.eat(TokenType.RBRACKET, "expecting right bracket")
        
        if self.match(TokenType.DOT):
            while not self.match(TokenType.DOT):
                self.var_rvalue()
        elif self.match(TokenType.LPAREN):
            self.call_expr()

    def call_expr(self):
        self.advance()
        if not self.match(TokenType.RPAREN):
            if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.NULL_VAL, TokenType.NEW, TokenType.ID, TokenType.LPAREN, TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL]):
                self.expr()
                while not self.match(TokenType.RPAREN):
                    self.eat(TokenType.COMMA, "expecting comma")
                    self.expr()
        self.eat(TokenType.RPAREN, "expecting right paren")
            

    def rvalue(self):
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.NULL_VAL, TokenType.DOT, TokenType.NEW, TokenType.ID, TokenType.LPAREN, TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL]):
            if self.match(TokenType.NEW):
                self.new_rvalue()
            elif self.match(TokenType.ID):
                self.var_rvalue()
            elif self.match(TokenType.LPAREN):
                self.call_expr()
            else:
                self.advance()

    def new_rvalue(self):
        self.advance()
        if self.match_any([TokenType.ID, TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            self.advance()
            if self.match(TokenType.LPAREN):
                self.advance()
                if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.NULL_VAL, TokenType.NEW, TokenType.ID, TokenType.LPAREN, TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL]):
                    self.expr()
                    while not self.match(TokenType.RPAREN):
                        self.eat(TokenType.COMMA, "expecting comma")
                        self.expr()

            elif self.match(TokenType.LBRACKET):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, "expecting closing bracket")
        if self.match(TokenType.RPAREN):
            self.advance()

    def var_rvalue(self):
        self.advance()
        if self.match(TokenType.ID):
            self.advance()

        if self.match(TokenType.LBRACKET):
            self.advance()
            self.expr()
            self.eat(TokenType.RBRACKET, "expecting closing bracket")

        if self.match(TokenType.DOT):
            self.advance()
            self.eat(TokenType.ID, "expecting id")
            if self.match(TokenType.DOT):
                while self.match(TokenType.DOT):
                    self.eat(TokenType.DOT, "expecting dot")
                    self.eat(TokenType.ID, "expecting id")
                    if self.match(TokenType.LBRACKET):
                        self.advance()
                        self.expr()
                        self.eat(TokenType.RBRACKET, "expecting closing bracket")
            elif self.match(TokenType.LBRACKET):
                self.advance()
                self.expr()
                self.eat(TokenType.RBRACKET, "expecting closing bracket")
        elif self.match(TokenType.LPAREN):
            self.call_expr()
            
                    
        

    def expr(self):
        if self.match(TokenType.NOT):
            self.advance()
            self.expr()
        elif self.match(TokenType.LPAREN):
            self.advance()
            self.expr()
            if not self.match(TokenType.RPAREN):
                self.error("unmatched parentheses")
            self.advance()
        else:
            self.rvalue()

        if self.match_any([TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE, TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ, TokenType.NOT_EQUAL]):
            self.bin_op()
            if self.match(TokenType.SEMICOLON):
                self.error("must have expr after op")
            self.expr()
            

    def bin_op(self):
         if self.match_any([TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,TokenType.AND,TokenType.OR,TokenType.EQUAL,TokenType.LESS,TokenType.GREATER,TokenType.LESS_EQ,TokenType.GREATER_EQ,TokenType.NOT_EQUAL]):
             self.advance()
             if self.match_any([TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,TokenType.AND,TokenType.OR,TokenType.EQUAL,TokenType.LESS,TokenType.GREATER,TokenType.LESS_EQ,TokenType.GREATER_EQ,TokenType.NOT_EQUAL]):
                 self.error("too many ops")