import pytest
import io

from mypl_error import *
from mypl_iowrapper import *
from mypl_token import *
from mypl_lexer import *
from mypl_ast_parser import *
from mypl_semantic_checker import *
from mypl_symbol_table import *
from mypl_var_table import *
from mypl_code_gen import *
from mypl_vm import *


#----------------------------------------------------------------------
# Basic Function Definitions
#----------------------------------------------------------------------
def build(program):
    in_stream = FileWrapper(io.StringIO(program))
    vm = VM()
    cg = CodeGenerator(vm)
    ASTParser(Lexer(FileWrapper(io.StringIO(program)))).parse().accept(cg)
    return vm

def test_simple_class_with_instance_variable():
    in_stream = FileWrapper(io.StringIO(
        'class Test{\n'
        '    int x; \n'
        '}\n'
    ))
    p = ASTParser(Lexer(in_stream)).parse()
    assert len(p.struct_defs) == 1
    assert len(p.struct_defs[0].fields) == 1
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'x'

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
    assert p.struct_defs[0].fields[0].var_name.lexeme == 'name'
    assert p.fun_defs[0].fun_name.lexeme == 'nothing'

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

def test_simple_method():
    in_stream = FileWrapper(io.StringIO(
        'class Test{\n'
            'int y;\n'
            'void add(int x){\n'
                'this.y = this.y + x;\n'
            '}\n'
        '}\n'
        'void main(){\n'
            'Test obj = new Test(4);\n'
            'obj.add(3);\n'
        '}\n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_array_of_classes_semantics():
    in_stream = FileWrapper(io.StringIO(
        ' class Person{\n'
        '   string name;\n'
        '   int age;\n'
        '   void print_info(){\n'
        '     print(this.name);\n'
        '     print(" is ");\n'
        '     print(this.age);\n'
        '     print(" years old!");\n'
        '   }\n'
        ' }\n'
        ' void main(){\n'
        '   array Person people = new Person[2];\n'
        '   people[0] = new Person("Cody", 20);\n'
        '   people[1] = new Person("Johnquavious", 103);\n'
        '   people[0].print_info();\n'
        '   people[1].print_info();\n'
        ' }\n'
    ))
    ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())

def test_bad_class_method_use():
    in_stream = FileWrapper(io.StringIO(
        'class Test{\n'
        '  int x;\n'
        '  void add(int y){\n'
        '    this.x = this.x + y;\n'
        '  }\n'
        '}\n'
        'struct Test2{int x;}\n'
        'void main(){\n'
        '  Test obj = new Test(4);\n'
        '  Test2 obj2 = new Test2(5);\n'
        '  obj2.add(3);\n'
        '}\n'))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_bad_class_init():
    in_stream = FileWrapper(io.StringIO(
        'class Person{\n'
        '  string name;\n'
        '  void nothing(){}\n'
        '}\n'
        'void main(){\n'
        '  Person finn = new Person(123);\n'
        '}\n'
    ))
    with pytest.raises(MyPLError) as e:
        ASTParser(Lexer(in_stream)).parse().accept(SemanticChecker())
    assert str(e.value).startswith('Static Error:')

def test_multiple_method_params(capsys):
    program = (
        'class Test{\n'
        '  int x;\n'
        '  void add_mult(int y, int z){\n'
        '    this.x = this.x + y;\n'
        '    this.x = this.x * z;\n'
        '  }\n'
        '}\n'
        'void main(){\n'
        '  Test obj = new Test(4);\n'
        '  obj.add_mult(3, 2);\n'
        '  print(obj.x);\n'
        '}\n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '14'

def test__method_print(capsys):
    program = (
         'class Test{\n'
        '    void method_print(){\n'
        '        print("testing, testing...");\n'
        '    }\n'
        '}\n'
        'void main(){\n'
        '    Test obj = new Test(); \n'
        '    obj.method_print(); \n'
        '}\n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'testing, testing...'

def test_two_field_class_with_method(capsys):
    program = (
        'class Test{\n'
        '  int x;\n'
        '  int y;\n'
        '  void add_1(){\n'
        '    this.x = this.x + 1;\n'
        '    this.y = this.y + 1;\n'
        '  }\n'
        '}\n'
        'void main(){\n'
        '  Test obj = new Test(4, 3);\n'
        '  obj.add_1();\n'
        '  print(obj.x);\n'
        '  print(obj.y);\n'
        '}\n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '54'

def test_two_classes(capsys):
    program = (
        'class Animal{\n'
        '  string animal;\n'
        '  void give_birth(){\n'
        '    print(this.animal);\n'
        '    print(" has given birth!");\n'
        '  }\n'
        '}\n'
        'class Person{\n'
        '  string name;\n'
        '  void eat(string food){\n'
        '    print(this.name);\n'
        '    print(" ate ");\n'
        '    print(food);\n'
        '  }\n'
        '}\n'
        'void main(){\n'
        '  Person finn = new Person("finn");\n'
        '  Animal cow = new Animal("cow");\n'
        '  finn.eat("legumes");\n'
        '  cow.give_birth();\n'
        '}\n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'finn ate legumescow has given birth!'

def test_array_of_classes_output(capsys):
    program = (
        ' class Person{\n'
        '   string name;\n'
        '   int age;\n'
        '   void print_info(){\n'
        '     print(this.name);\n'
        '     print(" is ");\n'
        '     print(this.age);\n'
        '     print(" years old!");\n'
        '   }\n'
        ' }\n'
        ' void main(){\n'
        '   array Person people = new Person[2];\n'
        '   people[0] = new Person("Cody", 20);\n'
        '   people[1] = new Person("Johnquavious", 103);\n'
        '   people[0].print_info();\n'
        '   print(" ");\n'
        '   people[1].print_info();\n'
        ' }\n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'Cody is 20 years old! Johnquavious is 103 years old!'

def test_method_assign_expr(capsys):
    program = (
        'class Room{\n'
        '    double length;\n'
        '    double width;\n'
        '    double calculate_area(){\n'
        '        return this.length * this.width;\n'
        '    }\n'
        '}\n'
        'void main(){\n'
        '    Room my_bedroom = new Room(14.0, 10.0);\n'
        '    double room_area = my_bedroom.calculate_area();\n'
        '    print("The area of my_bedroom is: ");\n'
        '    print(room_area);\n'
        '}\n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == 'The area of my_bedroom is: 140.0'

def test_recursive_method_field(capsys):
    program = (
        'class Node {\n'
        '    int data;\n'
        '    array Node next;\n'
        '}\n'
        'void main(){\n'
        '    Node root = new Node(20, new Node[2]);\n'
        '    root.next[0] = new Node(10, new Node[1]);\n'
        '    print(root.data);\n'
        '    print(root.next[0].data);\n'
        '}\n'
    )
    build(program).run()
    captured = capsys.readouterr()
    print(captured.out)
    assert captured.out == '2010'