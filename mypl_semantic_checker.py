"""Semantic Checker Visitor for semantically analyzing a MyPL program.

NAME: <your name here>
DATE: Spring 2024
CLASS: CPSC 326

"""

from dataclasses import dataclass
from mypl_error import *
from mypl_token import Token, TokenType
from mypl_ast import *
from mypl_symbol_table import SymbolTable


BASE_TYPES = ['int', 'double', 'bool', 'string']
BUILT_INS = ['print', 'input', 'itos', 'itod', 'dtos', 'dtoi', 'stoi', 'stod',
             'length', 'get']

class SemanticChecker(Visitor):
    """Visitor implementation to semantically check MyPL programs."""

    def __init__(self):
        self.structs = {}
        self.functions = {}
        self.symbol_table = SymbolTable()
        self.curr_type = None
        self.func_return_type = None
        self.return_encountered = False

    # Helper Functions

    def error(self, msg, token):
        """Create and raise a Static Error."""
        if token is None:
            raise StaticError(msg)
        else:
            m = f'{msg} near line {token.line}, column {token.column}'
            raise StaticError(m)


    def get_field_type(self, struct_def, field_name):
        """Returns the DataType for the given field name of the struct
        definition.

        Args:
            struct_def: The StructDef object 
            field_name: The name of the field

        Returns: The corresponding DataType or None if the field name
        is not in the struct_def.

        """
        for var_def in struct_def.fields:
            if var_def.var_name.lexeme == field_name:
                return var_def.data_type
        return None

        
    # Visitor Functions
    def visit_program(self, program):
        # check and record struct defs
        for struct in program.struct_defs:
            struct_name = struct.struct_name.lexeme
            if struct_name in self.structs:
                self.error(f'duplicate {struct_name} definition', struct.struct_name)
            self.structs[struct_name] = struct
        # check and record function defs
        for fun in program.fun_defs:
            fun_name = fun.fun_name.lexeme
            if fun_name in self.functions: 
                self.error(f'duplicate {fun_name} definition', fun.fun_name)
            if fun_name in BUILT_INS:
                self.error(f'redefining built-in function', fun.fun_name)
            if fun_name == 'main' and fun.return_type.type_name.lexeme != 'void':
                self.error('main without void type', fun.return_type.type_name)
            if fun_name == 'main' and fun.params: 
                self.error('main function with parameters', fun.fun_name)
            self.functions[fun_name] = fun
        # check main function
        if 'main' not in self.functions:
            self.error('missing main function', None) 
        # check each struct
        for struct in self.structs.values():
            struct.accept(self)
        # check each function
        for fun in self.functions.values():
            fun.accept(self)
        
        
    def visit_struct_def(self, struct_def):
        # TODO
        struct_name = struct_def.struct_name.lexeme
        self.structs[struct_name] = struct_def
    
        self.symbol_table.push_environment()
        for field in struct_def.fields:
            field.accept(self)
            field_name = field.var_name.lexeme
            field_type = field.data_type
            if field_type.type_name.lexeme not in BASE_TYPES and field_type.type_name.lexeme not in self.structs:
                self.error(f'undefined field "{field_name}" in struct "{struct_name}"', field.var_name)
        self.symbol_table.pop_environment()


    def visit_fun_def(self, fun_def):
        # TODO
        fun_name = fun_def.fun_name.lexeme
        self.func_return_type = fun_def.return_type
        if fun_def.return_type.type_name.lexeme not in BASE_TYPES and fun_def.return_type.type_name.lexeme != 'void':
            self.error("bad function return type", fun_def.return_type.type_name)
        self.functions[fun_name] = fun_def
        self.symbol_table.push_environment()
        self.symbol_table.add(fun_name, fun_def.return_type)

        self.return_encountered = False
        if fun_def.params:
            for param_def in fun_def.params:
                param_def.accept(self)
                self.curr_type = param_def.data_type

        if fun_def.stmts:
            for stmt in fun_def.stmts:
                stmt.accept(self)

        self.symbol_table.pop_environment()
        if fun_def.return_type.type_name.lexeme == 'void':
            pass
        else:
            if not self.return_encountered:
                pass
            elif self.curr_type.type_name.token_type == TokenType.VOID_TYPE:
                pass
            elif self.func_return_type.type_name.token_type != self.curr_type.type_name.token_type:
                self.error(f"Return type '{self.curr_type}' does not match the function's declared return type '{self.func_return_type}", fun_def.return_type.type_name)


    def visit_return_stmt(self, return_stmt):
        # TODO
         return_stmt.expr.accept(self)
         self.return_encountered = True
         if self.curr_type.type_name.token_type == None or self.curr_type.type_name.token_type == TokenType.VOID_TYPE:
             pass
         elif self.func_return_type.type_name.token_type != self.curr_type.type_name.token_type: 
             self.error(f"Return type does not match the function's declared return type,{self.func_return_type.type_name.token_type} != {self.curr_type.type_name}", self.curr_type.type_name)
        
            
    def visit_var_decl(self, var_decl):
        # TODO
        var_name = var_decl.var_def.var_name.lexeme
        data_type = var_decl.var_def.data_type

        if self.symbol_table.exists_in_curr_env(var_name):
            self.error("var decl shadowing error", var_decl.var_def.var_name)

        if var_decl.expr:
            var_decl.expr.accept(self)

            if data_type.type_name.token_type != self.curr_type.type_name.token_type and self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
                self.error(f"type mismatch {data_type} != {self.curr_type}", var_decl.var_def.data_type.type_name)
            
            if self.curr_type.is_array != data_type.is_array and self.curr_type.type_name.token_type != TokenType.VOID_TYPE:
               self.error(f"array initialization should be a 'new' object, {self.curr_type} != {data_type}", var_decl.var_def.var_name)
        self.symbol_table.add(var_name, data_type)

        
    def visit_assign_stmt(self, assign_stmt):
        # TODO
        lhs = None
        if self.symbol_table.get(assign_stmt.lvalue[0].var_name.lexeme):
            var_type = self.symbol_table.get(assign_stmt.lvalue[0].var_name.lexeme)
            var_ref = assign_stmt.lvalue[0]
            if var_ref.array_expr:
                var_ref.array_expr.accept(self)
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error('Array index must be an integer', var_ref.array_expr)

            for i in range(1, len(assign_stmt.lvalue)):
                var_name = assign_stmt.lvalue[i].var_name.lexeme
                if not var_type.type_name.lexeme in self.structs:
                    self.error(f'path must be a struct {var_type}', var_ref.array_expr)
                struct_def = self.structs[var_type.type_name.lexeme]
                var_type = self.get_field_type(struct_def, var_name)
                var_ref = assign_stmt.lvalue[i]
                if var_ref.array_expr:
                    var_ref.array_expr.accept(self)
                    if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                        self.error('Array index must be an integer', var_ref.array_expr)
            lhs = var_type
        else:
            self.error(f"Variable '{var_name}' not found", var_ref.var_name)


        if assign_stmt.expr:
            assign_stmt.expr.accept(self)
            rhs_type = self.curr_type
            if lhs.type_name.token_type != rhs_type.type_name.token_type and lhs.type_name.token_type != TokenType.VOID_TYPE and rhs_type.type_name.token_type != TokenType.VOID_TYPE:
                self.error(f"type mismatch {lhs.type_name.token_type } != {rhs_type.type_name.token_type}", self.curr_type.type_name)
             
    def visit_while_stmt(self, while_stmt):
        # TODO
        self.symbol_table.push_environment()
        while_stmt.condition.accept(self)
        if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
            self.error("while condition must be a bool", self.curr_type.type_name)


        for stmt in while_stmt.stmts:
            stmt.accept(self)

        self.symbol_table.pop_environment()

        
    def visit_for_stmt(self, for_stmt):
        # TODO
        self.symbol_table.push_environment()
        for_stmt.var_decl.accept(self)
        for_stmt.condition.accept(self)
        if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
            self.error("for statement condition must be bool", self.curr_type.type_name)
        for_stmt.assign_stmt.accept(self)
        for stmt in for_stmt.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()

    def visit_if_stmt(self, if_stmt):
        # TODO
        if_stmt.if_part.condition.accept(self)
        
        if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
            self.error("if condition must have bool type", self.curr_type.type_name)
            
        self.symbol_table.push_environment()
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        self.symbol_table.pop_environment()
        
        for else_if in if_stmt.else_ifs:
            else_if.condition.accept(self)
            if self.curr_type.type_name.token_type != TokenType.BOOL_TYPE or self.curr_type.is_array == True:
                self.error("if condition must have bool type", self.curr_type.type_name)
            
            self.symbol_table.push_environment()
            for stmt in else_if.stmts:
                stmt.accept(self)
            self.symbol_table.pop_environment()
        
        if if_stmt.else_stmts:
            self.symbol_table.push_environment()
            for stmt in if_stmt.else_stmts:
                stmt.accept(self)
            self.symbol_table.pop_environment()

    def visit_expr(self, expr):
        expr.first.accept(self)
        lhs_type = self.curr_type
        if expr.op:
            expr.rest.accept(self)
            rhs_type = self.curr_type
            operator = expr.op.lexeme

            if operator in ['+', '-', '*', '/']:
                if lhs_type.type_name.token_type != rhs_type.type_name.token_type:
                    self.error(f"type mismatch {lhs_type.type_name} != {rhs_type.type_name}", expr.op)
                self.curr_type = rhs_type

            elif operator in [ '==', '!=']:
                if rhs_type.type_name.token_type == TokenType.VOID_TYPE:
                    pass
                elif lhs_type.type_name.lexeme != rhs_type.type_name.lexeme:
                    self.error(f"type mismatch, {lhs_type.type_name} != {rhs_type.type_name}", expr.op)
                self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', expr.op.line, expr.op.column))

            elif operator in ['>', '>=', '<', '<=']:
                if lhs_type.type_name.lexeme != rhs_type.type_name.lexeme:
                    self.error(f"type mismatch, {lhs_type.type_name} != {rhs_type.type_name}", expr.op)
                elif lhs_type.type_name.token_type ==  TokenType.BOOL_TYPE or rhs_type.type_name.token_type == TokenType.BOOL_TYPE:
                    self.error(f"cannot compare bools, {lhs_type.type_name} op {rhs_type.type_name}", expr.op)
                self.curr_type = DataType(False, Token(TokenType.BOOL_TYPE, 'bool', expr.op.line, expr.op.column))

            elif operator in ['and', 'or']:
                if lhs_type.type_name.lexeme != 'bool' and rhs_type.type_name.lexeme != 'bool':
                    self.error("and/or operands must have bool types", expr.op)
                self.curr_type = rhs_type

        if expr.not_op:
            if self.curr_type.type_name.lexeme != 'bool':
                self.error(f"not operator must associate with bool, type = '{self.curr_type.type_name}'", expr.op)
        

    def visit_data_type(self, data_type):
        # note: allowing void (bad cases of void caught by parser)
        name = data_type.type_name.lexeme
        if name == 'void' or name in BASE_TYPES or name in self.structs:
            self.curr_type = data_type
        else: 
            self.error(f'invalid type "{name}"', data_type.type_name)
            
    def visit_var_def(self, var_def):
        # TODO
        var_name = var_def.var_name.lexeme
        
        if self.symbol_table.exists_in_curr_env(var_name):
            self.error(f'duplicate variable declaration for "{var_name}"', var_def.var_name)
        
        self.symbol_table.add(var_name, var_def.data_type)
        self.curr_type = self.symbol_table.get(var_name)
        
    def visit_simple_term(self, simple_term):
        # TODO
        simple_term.rvalue.accept(self)
    
    def visit_complex_term(self, complex_term):
        # TODO
        complex_term.expr.accept(self)

    def visit_simple_rvalue(self, simple_rvalue):
        value = simple_rvalue.value
        line = simple_rvalue.value.line
        column = simple_rvalue.value.column
        type_token = None 
        if value.token_type == TokenType.INT_VAL:
            type_token = Token(TokenType.INT_TYPE, 'int', line, column)
        elif value.token_type == TokenType.DOUBLE_VAL:
            type_token = Token(TokenType.DOUBLE_TYPE, 'double', line, column)
        elif value.token_type == TokenType.STRING_VAL:
            type_token = Token(TokenType.STRING_TYPE, 'string', line, column)
        elif value.token_type == TokenType.BOOL_VAL:
            type_token = Token(TokenType.BOOL_TYPE, 'bool', line, column)
        elif value.token_type == TokenType.NULL_VAL:
            type_token = Token(TokenType.VOID_TYPE, 'null', line, column)
        self.curr_type = DataType(False, type_token)
        
    def visit_new_rvalue(self, new_rvalue):
        # TODO
        type_name = new_rvalue.type_name.lexeme
        struct_params = new_rvalue.struct_params
        struct_def = None
        array_bool = False
        self.curr_type = DataType(False, Token(TokenType.VOID_TYPE, 'void', new_rvalue.type_name.line, new_rvalue.type_name.column))
        if new_rvalue.array_expr:
            new_rvalue.array_expr.accept(self)
            if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                self.error(f'array reference must be an integer, type = {self.curr_type.type_name}', new_rvalue.type_name)
            array_bool = True
        else:
            struct_def = self.structs[type_name]

            if type_name not in self.structs:
                self.error(f'undefined struct type "{type_name}"', new_rvalue.type_name)
            if len(struct_params) != len(struct_def.fields):
                self.error(f'incorrect number of parameters for struct "{type_name}"', new_rvalue.type_name)
            
            
            for field, param in zip(struct_def.fields, struct_params):
                param.accept(self)
                param_type = self.curr_type
                if param_type.type_name.token_type != field.data_type.type_name.token_type and param_type.type_name.token_type != TokenType.VOID_TYPE:
                    self.error(f'struct argument does not match parameter "{field.var_name}"', None)

                self.symbol_table.add(field.var_name.lexeme, param_type)

        self.curr_type = DataType(array_bool, new_rvalue.type_name)
            
    def visit_var_rvalue(self, var_rvalue):
        # TODO
        if self.symbol_table.get(var_rvalue.path[0].var_name.lexeme):
            arr_expr_bool = False
            var_type = self.symbol_table.get(var_rvalue.path[0].var_name.lexeme)
            var_ref = var_rvalue.path[0]
            if var_ref.array_expr:
                arr_expr_bool = True
                var_ref.array_expr.accept(self)
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error('Array index must be an integer', var_ref.array_expr)
            self.curr_type = var_type
            if arr_expr_bool:
                self.curr_type.is_array = False

            for i in range(1, len(var_rvalue.path)):
                var_name = var_rvalue.path[i].var_name.lexeme
                if not var_type.type_name.lexeme in self.structs:
                    self.error(f'path must be a struct {var_type}', var_ref.array_expr)
                struct_def = self.structs[var_type.type_name.lexeme]
                var_type = self.get_field_type(struct_def, var_name)
                var_ref = var_rvalue.path[i]
                if var_ref.array_expr:
                    arr_expr_bool = True
                    var_ref.array_expr.accept(self)
                    if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                        self.error('Array index must be an integer', var_ref.array_expr)
                self.curr_type = var_type
                if arr_expr_bool:
                    self.curr_type.is_array = False
        else:
            self.error(f"Variable '{var_rvalue.path[0].var_name}' not found", var_rvalue.path[0].var_name)
                
    def visit_call_expr(self, call_expr):
        # TODO
        fun_name = call_expr.fun_name.lexeme
        args = call_expr.args

        if fun_name not in BUILT_INS and fun_name not in self.functions:
            self.error(f'undefined function "{fun_name}"', call_expr.fun_name)
        elif fun_name in BUILT_INS:
            pass
        elif len(self.functions[fun_name].params) != len(args):
            self.error(f'mismatch # of func call args to definition params"{fun_name}", {len(self.functions[fun_name].params)} != {len(args)}', call_expr.fun_name)

        if fun_name in self.functions:
            for i in range(len(args)):
                arg = args[i]
                param = self.functions[fun_name].params[i]
                arg.accept(self)
                param_type = param.data_type.type_name
                if self.curr_type.type_name.token_type == TokenType.VOID_TYPE:
                    pass
                elif self.curr_type.type_name.lexeme != param_type.lexeme:
                    self.error(f"Function call arguments do not match function definition params  {self.curr_type} != {param_type}", self.curr_type.type_name)
            self.curr_type = self.functions[fun_name].return_type
        
        elif fun_name == 'print':
            if not args:
                self.error('print function expects at least one argument', None)
            if len(args)>1:
                self.error("print takes 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.lexeme in self.structs:
                    self.error("Cannot print entire objects", call_expr.fun_name)
                elif self.curr_type.is_array:
                    self.error("cannot print array object", self.curr_type.type_name)

        elif fun_name == 'input':
            if len(args) != 0:
                self.error("input() has no arguments", None)
            self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))

        elif fun_name == 'itos':
            if len(args) != 1:
                self.error("itos must have 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error(f"int to string must have integer input, type = {self.curr_type.type_name}", None)
                self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))

        elif fun_name == 'itod':
            if len(args) != 1:
                self.error("itod must have 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                    self.error(f"int to double must have integer input, type = {self.curr_type.type_name}", None)
                self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'double', call_expr.fun_name.line, call_expr.fun_name.column))
        elif fun_name == 'dtos':
            if len(args) != 1:
                self.error("dtos must have 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.token_type != TokenType.DOUBLE_TYPE:
                    self.error("double to string must have double input", None)
                self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))

        elif fun_name == 'dtoi':
            if len(args) != 1:
                self.error("dtoi must have 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.token_type != TokenType.DOUBLE_TYPE:
                    self.error("double to int must have double input", None)
                self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', call_expr.fun_name.line, call_expr.fun_name.column))
                    

        elif fun_name == 'stoi':
            if len(args) != 1:
                self.error("stoi must have 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.token_type != TokenType.STRING_TYPE:
                    self.error(f"string to int must have string input, type = {self.curr_type.type_name}", None)
                self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', call_expr.fun_name.line, call_expr.fun_name.column))

        elif fun_name == 'stod':
            if len(args) != 1:
                self.error("stod must have 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.token_type != TokenType.STRING_TYPE:
                    self.error(f"stod must have string input, type = {self.curr_type.type_name}", None)
                self.curr_type = DataType(False, Token(TokenType.DOUBLE_TYPE, 'double', call_expr.fun_name.line, call_expr.fun_name.column))
        
        elif fun_name == 'length':
            if len(args) != 1:
                self.error("length must have 1 argument", None)
            for arg in args:
                arg.accept(self)
                if self.curr_type.type_name.token_type not in [TokenType.DOUBLE_TYPE, TokenType.INT_TYPE, TokenType.STRING_TYPE, TokenType.ID] or (self.curr_type.is_array == False and self.curr_type.type_name.token_type == TokenType.DOUBLE_TYPE):
                    self.error(f"Length function must use an element with a length, type = {self.curr_type}", self.curr_type.type_name)
                elif self.curr_type.type_name.token_type == TokenType.ID:
                    if not self.symbol_table.exists(self.curr_type.token_type.lexeme):
                        self.error("Element ID not initialized or found", arg.first.lexeme)
            self.curr_type = DataType(False, Token(TokenType.INT_TYPE, 'int', call_expr.fun_name.line, call_expr.fun_name.column))
        elif fun_name == 'get':
            if len(args) != 2:
                self.error("get must have 2 arguments", None)
            args[0].accept(self)
            if self.curr_type.type_name.token_type != TokenType.INT_TYPE:
                self.error("First argument of get() function must be an integer representing the index", call_expr.fun_name)
            args[1].accept(self)
            if self.curr_type.type_name.token_type != TokenType.STRING_TYPE or self.curr_type.is_array:
                self.error("Second argument of get() function must be a string", call_expr.fun_name)
            self.curr_type = DataType(False, Token(TokenType.STRING_TYPE, 'string', call_expr.fun_name.line, call_expr.fun_name.column))
