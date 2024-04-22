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
        pass

    def visit_fun_def(self, fun_def):
        pass

    def visit_return_stmt(self, return_stmt):
        pass

    def visit_var_decl(self, var_decl):
        pass

    def visit_assign_stmt(self, assign_stmt):
        pass

    def visit_while_stmt(self, while_stmt):
        pass

    def visit_for_stmt(self, for_stmt):
        pass

    def visit_if_stmt(self, if_stmt):
        pass
    
    def visit_call_expr(self, call_expr):
        pass
    
    def visit_expr(self, expr):
        pass
    
    def visit_data_type(self, data_type):
        pass

    def visit_var_def(self, var_def):
        pass

    def visit_simple_term(self, simple_term):
        pass

    def visit_complex_term(self, complex_term):
        pass

    def visit_simple_rvalue(self, simple_rvalue):
        pass
    
    def visit_new_rvalue(self, new_rvalue):
        pass

    def visit_var_rvalue(self, var_rvalue):
        pass