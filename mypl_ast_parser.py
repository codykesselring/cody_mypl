"""MyPL AST parser implementation.

NAME: <your-name-here>
DATE: Spring 2024
CLASS: CPSC 326
"""

from mypl_error import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast import *


class ASTParser:

    def __init__(self, lexer):
        """Create a MyPL syntax checker (parser). 
        
        Args:
            lexer -- The lexer to use in the parser.

        """
        self.lexer = lexer
        self.curr_token = None
        self.in_method = False

        
    def parse(self):
        """Start the parser, returning a Program AST node."""
        program_node = Program([], [])
        self.advance()
        while not self.match(TokenType.EOS):
            if self.match(TokenType.STRUCT) or self.match(TokenType.CLASS):
                self.struct_def(program_node)
            else:
                self.fun_def(program_node, None, None, False, None)
        self.eat(TokenType.EOS, 'expecting EOF')
        return program_node

        
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
        """Returns true if the current token is a binary operator."""
        ts = [TokenType.PLUS, TokenType.MINUS, TokenType.TIMES, TokenType.DIVIDE,
              TokenType.AND, TokenType.OR, TokenType.EQUAL, TokenType.LESS,
              TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ,
              TokenType.NOT_EQUAL]
        return self.match_any(ts)


    #----------------------------------------------------------------------
    # Recursive descent functions
    #----------------------------------------------------------------------


    # TODO: Finish the recursive descent functions below. Note that
    # you should copy in your functions from HW-2 and then instrument
    # them to build the corresponding AST objects.
    
    def struct_def(self, program_node):
        class_bool = False
        if self.match(TokenType.CLASS):
            class_bool = True
        self.advance()
        if self.match(TokenType.ID):
            struct_name = self.curr_token
            self.advance()
            self.eat(TokenType.LBRACE, "expecting left brace")
        fields = self.fields(program_node, struct_name)
        while class_bool and not self.match(TokenType.RBRACE):
            self.fun_def(program_node, None, None, True, struct_name)
        self.eat(TokenType.RBRACE, "expecting rbrace")
        struct_def_node = StructDef(struct_name, fields)
        program_node.struct_defs.append(struct_def_node)

    def fields(self, program_node, struct_name):
        fields = []
        while not self.match(TokenType.RBRACE):
            data_type = self.data_type()
            var_name = self.curr_token
            self.eat(TokenType.ID, "expecting variable name")
            if self.match(TokenType.SEMICOLON):
                self.eat(TokenType.SEMICOLON, "expecting semicolon")
                var_def_node = VarDef(data_type, var_name)
                fields.append(var_def_node)
            elif self.match(TokenType.LPAREN): #it's a method
                self.advance()
                self.fun_def(program_node, data_type, var_name, True, struct_name)
                break

        return fields

    def data_type(self):
        if self.match(TokenType.ARRAY):
            self.advance()
            if self.match(TokenType.ID):
                type_name = self.curr_token
                self.advance()
            else:
                type_name = self.base_type()
                self.advance()
            return DataType(True, type_name)
        elif self.match(TokenType.ID):
            type_name = self.curr_token
            self.advance()
            return DataType(False, type_name)
        elif self.match(TokenType.VOID_TYPE):
            type_name = self.curr_token
            self.advance()
            return DataType(False, type_name)
        else:
            type_name = self.base_type()
            self.advance()
            return DataType(False, type_name)

    def base_type(self):
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE]):
            return self.curr_token
        else:
            self.error("not a base type")
    
    def fun_def(self, program_node, data_type, var_name, is_method, struct_name):
        if is_method:
            self.in_method = True
        if data_type == None and var_name == None:
            return_type = self.data_type()
            fun_name = self.curr_token
            self.eat(TokenType.ID, "expecting function name")
            self.eat(TokenType.LPAREN, "expect left paren")
        else :
            return_type = data_type
            fun_name = var_name
        params = self.params()
        self.eat(TokenType.RPAREN, "missing closing paren")
        self.eat(TokenType.LBRACE, "expect left brace")
        stmts = []
        while not self.match(TokenType.RBRACE):
            stmt = self.stmt()
            stmts.append(stmt)
        self.advance()
        if is_method:
            self.in_method = False
            fun_name.lexeme = fun_name.lexeme
            params.insert(0, VarDef(DataType(False, struct_name), Token(TokenType.ID, "this", struct_name.line, struct_name.column)))
            fun_def_node = FunDef(return_type, fun_name, params, stmts)
        else:
            fun_def_node = FunDef(return_type, fun_name, params, stmts)
        program_node.fun_defs.append(fun_def_node)
        
    def params(self):
        params = []
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY, TokenType.ID]):
            data_type = self.data_type()
            var_name = self.curr_token
            self.eat(TokenType.ID, "expecting id")
            params.append(VarDef(data_type, var_name))
            while self.match(TokenType.COMMA): 
                self.advance()
                data_type = self.data_type()
                var_name = self.curr_token
                self.eat(TokenType.ID, "expecting id")
                params.append(VarDef(data_type, var_name))
        return params

    def stmt(self):
        if self.match(TokenType.IF):
            c =  self.if_stmt()
        elif self.match(TokenType.WHILE):
            c = self.while_stmt()   
        elif self.match(TokenType.FOR):
            c = self.for_stmt()
        elif self.match(TokenType.RETURN):
            c = self.return_stmt()
            self.eat(TokenType.SEMICOLON, "expecting semicolon")
        elif self.match(TokenType.ID):
            id_token = self.curr_token
            self.advance()
            if self.match(TokenType.LPAREN):
                c = self.call_expr(id_token)
                self.eat(TokenType.SEMICOLON, "expecting semicolon")
            elif self.match(TokenType.ID):
                data_type_token = id_token
                c = self.vdecl_stmt(data_type_token)
                self.eat(TokenType.SEMICOLON, "expecting semiclon")
            else:
                c = self.assign_stmt(id_token)
                self.eat(TokenType.SEMICOLON, "expecting semicolon")
        else:
            c = self.vdecl_stmt(data_type_token=None)
            self.eat(TokenType.SEMICOLON, "expecting semicolon")
        return c
    
    def vdecl_stmt(self, data_type_token):
        if data_type_token is None:
            if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ARRAY]):
                if self.match(TokenType.ARRAY):
                    self.advance()
                    data_type_token = self.curr_token
                    self.advance()
                    data_type = DataType(True, data_type_token)
                else: 
                    data_type_token = self.curr_token
                    self.advance()
                    data_type = DataType(False, data_type_token)
        else:
            data_type = DataType(False, data_type_token)
        
        id_token = self.curr_token
        self.eat(TokenType.ID, "expecting vdecl id")
        var_def = VarDef(data_type, id_token)
                
        expr = None
        if self.match(TokenType.ASSIGN):
            self.advance()
            expr = self.expr()
        return VarDecl(var_def, expr)
    

    def return_stmt(self):
        self.advance()
        if self.match(TokenType.SEMICOLON):
            self.error("must have expression after return")
        return ReturnStmt(self.expr())
        

    def call_expr(self, id_token):
        self.advance()
        args = []
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.NULL_VAL, TokenType.NEW, TokenType.LPAREN, TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL, TokenType.ID]):
            args.append(self.expr())
            while not self.match(TokenType.RPAREN):
                self.eat(TokenType.COMMA, "expecting comma")
                args.append(self.expr())
        self.eat(TokenType.RPAREN, "expecting closing paren")
        return CallExpr(id_token, args)


    def assign_stmt(self, id_token):
        lvalue, is_call_expr = self.lvalue(id_token)
        
        if is_call_expr:
            return lvalue
        else:
            self.eat(TokenType.ASSIGN, "expecting assign")
            expr = self.expr()
            return AssignStmt(lvalue, expr)
    

    def lvalue(self, id_token):
        lvalue = []
        is_call_expr = False
        if id_token.lexeme == "this":
            if not self.in_method:
                self.error("Cannot use 'this' outside of a method.")
            else:
                lvalue.append(VarRef(id_token, None))
        else:
            var_name = id_token
            array_expr = None
            if self.match(TokenType.LBRACKET):
                self.advance()
                array_expr = self.expr()
                self.eat(TokenType.RBRACKET, "expecting left bracket")
            lvalue.append(VarRef(var_name, array_expr))
            
        while self.match(TokenType.DOT):
            array_expr = None
            self.advance()
            var_name = self.curr_token
            self.eat(TokenType.ID, "expecting id")
            if self.match(TokenType.LBRACKET):
                self.advance()
                array_expr = self.expr()
                self.eat(TokenType.RBRACKET, "expecting right bracket")
            elif self.match(TokenType.LPAREN):
                self.advance()
                fun_name = var_name
                args = []
                if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.NULL_VAL, TokenType.NEW, TokenType.LPAREN, TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL, TokenType.ID]):
                    args.append(self.expr())
                    while not self.match(TokenType.RPAREN):
                        self.eat(TokenType.COMMA, "expecting comma")
                        args.append(self.expr())
                if len(lvalue) == 1:
                    args.insert(0, VarRValue(lvalue))
                else:
                    args.insert(0, VarRValue(lvalue[:-1]))
                self.eat(TokenType.RPAREN, "expecting closing paren")
                is_call_expr = True
                return CallExpr(fun_name, args), is_call_expr
            lvalue.append(VarRef(var_name, array_expr))
        return lvalue, is_call_expr

    
    def expr(self):
        not_op = False
        if self.match(TokenType.NOT):
           not_op = True
           self.advance()
           first_term = self.r_value()
        elif self.match(TokenType.LPAREN):
            self.advance()
            first_term = ComplexTerm(self.expr())
            self.eat(TokenType.RPAREN, "expecting rparen")
        else:
            first_term = self.r_value()
        
        op = None
        rest = None
        if self.is_bin_op():
            op = self.curr_token
            self.advance()
            rest = self.expr()
        return Expr(not_op, first_term, op, rest)
    

    def r_value(self):
        if self.match_any([TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL, TokenType.NULL_VAL]):
            c = SimpleTerm(SimpleRValue(self.curr_token))
            self.advance()
            return c
        elif self.match(TokenType.NEW):
            self.advance()
            return SimpleTerm(self.new_rvalue())
        elif self.match(TokenType.ID):
            id_token = self.curr_token
            self.advance()
            if self.match(TokenType.LPAREN):
                return SimpleTerm(self.call_expr(id_token))
            else:
                return SimpleTerm(self.var_rvalue(id_token))
        else:
            return self.expr()

    def new_rvalue(self):
        if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.ID]):
            type_name = self.curr_token
            self.advance()
        else:
            self.error("data type should follow new keyword")
        array_expr = None
        struct_params = None
        if self.match(TokenType.LBRACKET):
            self.advance()
            array_expr = self.expr()
            self.eat(TokenType.RBRACKET, "expecting right bracket")
        
        elif self.match(TokenType.LPAREN):
            self.advance()
            struct_params = self.expr_list()
            self.eat(TokenType.RPAREN, "expecting right paren")
        
        return NewRValue(type_name, array_expr, struct_params)
    
    
    def var_rvalue(self, id_token):
        if id_token is None:
            var_name = self.curr_token
            self.advance()
        else:
            var_name = id_token
        
        path = []
        if self.match(TokenType.LBRACKET):
            self.advance()
            if self.match(TokenType.INT_VAL) or self.match(TokenType.ID):
                arr_expr = self.expr()
            self.eat(TokenType.RBRACKET, "expecting right bracket")
            path.append(VarRef(var_name, arr_expr))
        else:
            path.append(VarRef(var_name, None))
        
        while self.match_any([TokenType.DOT, TokenType.LBRACKET]):
            arr_expr = None
            if self.match(TokenType.DOT):
                self.advance()
                var_name = self.curr_token
                self.eat(TokenType.ID, "expecting var id")
                """if self.match(TokenType.LBRACKET): # for call expression on right side of assign_stmt
                    self.advance()
                    array_expr = self.expr()
                    self.eat(TokenType.RBRACKET, "expecting right bracket")"""
                if self.match(TokenType.LPAREN):
                    self.advance()
                    fun_name = var_name
                    args = []
                    if self.match_any([TokenType.INT_TYPE, TokenType.DOUBLE_TYPE, TokenType.BOOL_TYPE, TokenType.STRING_TYPE, TokenType.NULL_VAL, TokenType.NEW, TokenType.LPAREN, TokenType.INT_VAL, TokenType.DOUBLE_VAL, TokenType.BOOL_VAL, TokenType.STRING_VAL, TokenType.ID]):
                        args.append(self.expr())
                        while not self.match(TokenType.RPAREN):
                            self.eat(TokenType.COMMA, "expecting comma")
                            args.append(self.expr())
                    if len(path) == 1:
                        args.insert(0, VarRValue(path))
                    else:
                        args.insert(0, VarRValue(path[:-1]))
                    self.eat(TokenType.RPAREN, "expecting closing paren")
                    return CallExpr(fun_name, args)
            if self.match(TokenType.LBRACKET):
                self.advance()
                if self.match(TokenType.INT_VAL) or self.match(TokenType.ID):
                    arr_expr = self.expr()  
                self.eat(TokenType.RBRACKET, "expecting right bracket")
            path.append(VarRef(var_name, arr_expr))
        return VarRValue(path)


    def expr_list(self):
        expr_list = []
        if not self.match(TokenType.RPAREN):
            expr_list.append(self.expr())
            while self.match(TokenType.COMMA):
                self.advance()
                expr_list.append(self.expr())
        return expr_list
    

    def if_stmt(self):
        self.advance()
        self.eat(TokenType.LPAREN, "expecting left paren")
        if_part = self.basic_if()
        else_ifs, else_stmts = self.if_stmt_t()
        return IfStmt(if_part, else_ifs, else_stmts)
    
    def if_stmt_t(self):
        has_else = False
        else_ifs = []
        else_stmts = []
        while self.match_any([TokenType.ELSEIF, TokenType.ELSE]):
            if self.match(TokenType.ELSEIF):
                if has_else:
                    self.error("else out of order")
                self.advance()
                self.eat(TokenType.LPAREN, "expecting left paren")
                else_ifs.append(self.basic_if())
            elif self.match(TokenType.ELSE):
                if has_else:
                    self.error("else out of order")
                has_else = True
                self.advance()
                self.eat(TokenType.LBRACE, "expecting left brace")
                while not self.match(TokenType.RBRACE):
                    stmt = self.stmt()
                    else_stmts.append(stmt)
                self.advance()
        return else_ifs, else_stmts
    
    def basic_if(self):
        condition = self.expr()
        self.eat(TokenType.RPAREN, "expecting right paren")
        self.eat(TokenType.LBRACE, "expecting left brace")
        stmts = []
        while not self.match(TokenType.RBRACE):
            stmts.append(self.stmt())
        self.advance()
        return BasicIf(condition, stmts)
    
    def while_stmt(self):
        self.advance()
        self.eat(TokenType.LPAREN, "expecting left paren")
        if self.match(TokenType.RPAREN):
            self.error("while loop must have param")
        condition = self.expr()
        self.eat(TokenType.RPAREN, "expecting right paren")
        self.eat(TokenType.LBRACE, "expecting left brace")
        stmts = []
        while not self.match(TokenType.RBRACE):
            stmts.append(self.stmt())
        self.eat(TokenType.RBRACE, "expecting right brace")
        return WhileStmt(condition, stmts)
    
    def for_stmt(self):
        self.advance()
        self.eat(TokenType.LPAREN, "expecting left paren")
        var_decl = self.vdecl_stmt(None)
        self.eat(TokenType.SEMICOLON, "expecting semicolon")
        condition = self.expr()
        self.eat(TokenType.SEMICOLON, "expecting semicolon")
        id_token = self.curr_token
        self.eat(TokenType.ID, "expecting id   ")
        assign_stmt = self.assign_stmt(id_token)
        self.eat(TokenType.RPAREN, "expecting right paren")

        self.eat(TokenType.LBRACE, "expecting left brace")
        stmts = []
        while not self.match(TokenType.RBRACE):
            stmts.append(self.stmt())
        self.eat(TokenType.RBRACE, "expecting right brace")
        return ForStmt(var_decl, condition, assign_stmt, stmts)