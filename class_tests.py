import pytest
import io

from mypl_error import *
from mypl_iowrapper import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast_parser import *


#----------------------------------------------------------------------
# Basic Function Definitions
#----------------------------------------------------------------------

def test_empty_input():
    in_stream = FileWrapper(io.StringIO(''))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 0
    assert len(p.struct_defs) == 0

def test_if_statement_with_body():
    in_stream = FileWrapper(io.StringIO(
        'void main() { \n'
        '  if (true) {int x = 0;} \n'
        '} \n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs[0].stmts) == 1
    stmt = p.fun_defs[0].stmts[0]
    assert stmt.if_part.condition.first.rvalue.value.lexeme == 'true'
    assert len(stmt.if_part.stmts) == 1
    assert len(stmt.else_ifs) == 0
    assert len(stmt.else_stmts) == 0

def test_simple_class():
    in_stream = FileWrapper(io.StringIO(
        'class Test{\n'
        '    string name; \n'
        '    int id; \n'
        '    \n'
        '    void nothing(){\n'
        '    }\n'
        '}\n'
        'void main(){\n'
        '}\n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 1

def test_simple_class_with_body():
    in_stream = FileWrapper(io.StringIO(
        'class Test{\n'
        '    string name; \n'
        '    int id; \n'
        '    \n'
        '    void nothing(){\n'
        '         int x = 3;\n'
        '         int y = x;\n'
        '    }\n'
        '}\n'
        'void main(){\n'
        '}\n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.fun_defs) == 2
    assert len(p.struct_defs) == 1
