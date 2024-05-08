"""IR code generator for converting MyPL to VM Instructions. 

NAME: <your name here>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_token import *
from mypl_ast import *
from mypl_var_table import *
from mypl_frame import *
from mypl_opcode import *
from mypl_vm import *


class CodeGenerator (Visitor):

    def __init__(self, vm):
        """Creates a new Code Generator given a VM. 
        
        Args:
            vm -- The target vm.
        """
        # the vm to add frames to
        self.vm = vm
        # the current frame template being generated
        self.curr_template = None
        # for var -> index mappings wrt to environments
        self.var_table = VarTable()
        # struct name -> StructDef for struct field info
        self.struct_defs = {}

    
    def add_instr(self, instr):
        """Helper function to add an instruction to the current template."""
        self.curr_template.instructions.append(instr)

        
    def visit_program(self, program):
        for struct_def in program.struct_defs:
            struct_def.accept(self)
        for fun_def in program.fun_defs:
            fun_def.accept(self)

    
    def visit_struct_def(self, struct_def):
        # remember the struct def for later
        self.struct_defs[struct_def.struct_name.lexeme] = struct_def

        
    def visit_fun_def(self, fun_def):
        # TODO
        self.curr_template = VMFrameTemplate(fun_def.fun_name.lexeme, len(fun_def.params))

        self.var_table.push_environment()

        for param in fun_def.params:
            self.var_table.add(param.var_name.lexeme)
            index = self.var_table.get(param.var_name.lexeme)
            self.add_instr(STORE(index))
        
        for stmt in fun_def.stmts:
            stmt.accept(self)

        if not self.curr_template.instructions or self.curr_template.instructions[-1].opcode != OpCode.RET:
            self.add_instr(PUSH(None))
            self.add_instr(RET())
        
        self.var_table.pop_environment()
        self.vm.add_frame_template(self.curr_template)
        self.curr_template = None

    
    def visit_return_stmt(self, return_stmt):
        # TODO
        if return_stmt.expr:
            return_stmt.expr.accept(self)
        else:
            self.add_instr(PUSH(None))            
        self.add_instr(RET())
        
    def visit_var_decl(self, var_decl):
        # TODO
        self.var_table.add(var_decl.var_def.var_name.lexeme)
        if var_decl.expr:
            var_decl.expr.accept(self)
        else:
            self.add_instr(PUSH(None))
        
        index = self.var_table.get(var_decl.var_def.var_name.lexeme)
        self.add_instr(STORE(index))
    

    def visit_assign_stmt(self, assign_stmt):
        # TODO
        if len(assign_stmt.lvalue) == 1:
            # Simple variable assignment
            var_name = assign_stmt.lvalue[0].var_name.lexeme
            index = self.var_table.get(var_name)
            if assign_stmt.lvalue[0].array_expr:
                oid = self.var_table.get(var_name)
                self.add_instr(LOAD(oid))
                assign_stmt.lvalue[0].array_expr.accept(self)
                assign_stmt.expr.accept(self)
                self.add_instr(SETI())
            else:
                assign_stmt.expr.accept(self)
                self.add_instr(STORE(index))
        else:
            var_name = assign_stmt.lvalue[0].var_name.lexeme
            index = self.var_table.get(var_name)
            if assign_stmt.lvalue[0].array_expr:
                # If it's an array element, handle it differently
                self.add_instr(LOAD(index))
                assign_stmt.lvalue[0].array_expr.accept(self)
                self.add_instr(GETI())
            else:
                self.add_instr(LOAD(index))
            
            for var_ref in assign_stmt.lvalue[1:-1]: #skips first and last var_ref
                field_name = var_ref.var_name.lexeme
                self.add_instr(GETF(field_name))
                if var_ref.array_expr:
                    var_ref.array_expr.accept(self)
                    self.add_instr(GETI())
            
            
            
            assign_field = assign_stmt.lvalue[-1].var_name.lexeme
            if assign_stmt.lvalue[-1].array_expr:
                self.add_instr(GETF(assign_field))
                assign_stmt.lvalue[-1].array_expr.accept(self)
                assign_stmt.expr.accept(self)
                self.add_instr(SETI())
            else:
                assign_stmt.expr.accept(self)
                self.add_instr(SETF(assign_field))
            
        
    def visit_while_stmt(self, while_stmt):
        # TODO
        start_index = len(self.curr_template.instructions)
        while_stmt.condition.accept(self)

        jmp_instr = JMPF(-1)
        jmp_instr_index = len(self.curr_template.instructions)
        self.add_instr(jmp_instr)

        self.var_table.push_environment()
        for stmt in while_stmt.stmts:
            stmt.accept(self)
        self.var_table.pop_environment()

        self.add_instr(JMP(start_index))
        self.add_instr(NOP())
        end_index = len(self.curr_template.instructions)
        self.curr_template.instructions[jmp_instr_index].operand = end_index

        
    def visit_for_stmt(self, for_stmt):
        # TODO
        self.var_table.push_environment()

        for_stmt.var_decl.accept(self)
        loop_start_index = len(self.curr_template.instructions)
        for_stmt.condition.accept(self)

        jmp_instr = JMPF(-1)
        jmp_instr_index = len(self.curr_template.instructions)
        self.add_instr(jmp_instr)

        for stmt in for_stmt.stmts:
            stmt.accept(self)
        for_stmt.assign_stmt.accept(self)
        self.add_instr(JMP(loop_start_index))

        end_index = len(self.curr_template.instructions)
        self.curr_template.instructions[jmp_instr_index].operand = end_index

        self.var_table.pop_environment()


    
    def visit_if_stmt(self, if_stmt):
        # TODO
        else_if_bool = False
        if_stmt.if_part.condition.accept(self)
        
        jmp_instr_if = JMPF(-1)
        jmp_instr = len(self.curr_template.instructions)
        self.add_instr(jmp_instr_if)

        self.var_table.push_environment()
        for stmt in if_stmt.if_part.stmts:
            stmt.accept(self)
        jmp_end_if = JMP(-1)
        jmp_end_if_index = len(self.curr_template.instructions)
        self.add_instr(jmp_end_if)
        end_index_if = len(self.curr_template.instructions)
        self.var_table.pop_environment()
        
        # Update the jmpf
        self.curr_template.instructions[jmp_instr].operand = end_index_if
        
        index_arr = []
        for else_if in if_stmt.else_ifs:
            else_if_bool = True
            else_if.condition.accept(self)

            jmp_instr_else_if = JMPF(-1)
            jmp_instr = len(self.curr_template.instructions)
            self.add_instr(jmp_instr_else_if)

            self.var_table.push_environment()
            for stmt in else_if.stmts:
                stmt.accept(self)
            
            self.var_table.pop_environment()

            jmp_outside_if = JMP(-1)
            jmp_outside_if_index = len(self.curr_template.instructions)
            self.add_instr(jmp_outside_if)
            index_arr.append(jmp_outside_if_index)

            end_index_else_if = len(self.curr_template.instructions)
            self.curr_template.instructions[jmp_instr].operand = end_index_else_if
            # Update the jump instructions at the end of the if block to skip the else-if and else blocks
            self.curr_template.instructions[jmp_end_if_index].operand = end_index_else_if

        if if_stmt.else_stmts:
                else_start = len(self.curr_template.instructions)
                self.curr_template.instructions[jmp_instr].operand = else_start
                self.var_table.push_environment()
                for stmt in if_stmt.else_stmts:
                    stmt.accept(self)
                self.var_table.pop_environment()
        
                self.add_instr(NOP())
                end_index_else = len(self.curr_template.instructions)

        end_index = len(self.curr_template.instructions)
        self.curr_template.instructions[jmp_end_if_index].operand = end_index
        for i in range(len(index_arr)):
            self.curr_template.instructions[index_arr[i]].operand = end_index
                    
    
    def visit_call_expr(self, call_expr):
        # TODO
        for arg in call_expr.args:
            arg.accept(self)
        
        if call_expr.fun_name.lexeme == "print":
            self.add_instr(WRITE())
        elif call_expr.fun_name.lexeme == "length":
            self.add_instr(LEN())
        elif call_expr.fun_name.lexeme == "get":
            self.add_instr(GETC())
        elif call_expr.fun_name.lexeme == "input":
            self.add_instr(READ())
        elif call_expr.fun_name.lexeme == "itos" or call_expr.fun_name.lexeme == "dtos":
            self.add_instr(TOSTR())
        elif call_expr.fun_name.lexeme == "stoi" or call_expr.fun_name.lexeme == "dtoi":
            self.add_instr(TOINT())
        elif call_expr.fun_name.lexeme == "stod" or call_expr.fun_name.lexeme == "itod":
            self.add_instr(TODBL())
        else:
            self.add_instr(CALL(call_expr.fun_name.lexeme))

        
    def visit_expr(self, expr):
        # TODO
        expr.first.accept(self)

        if expr.not_op:
            self.add_instr(NOT())

        if expr.op:
            expr.rest.accept(self)
            if expr.op.token_type == TokenType.PLUS:
                self.add_instr(ADD())
            elif expr.op.token_type == TokenType.MINUS:
                self.add_instr(SUB())
            elif expr.op.token_type == TokenType.TIMES:
                self.add_instr(MUL())
            elif expr.op.token_type == TokenType.DIVIDE:
                self.add_instr(DIV())
            elif expr.op.token_type == TokenType.AND:
                self.add_instr(AND())
            elif expr.op.token_type == TokenType.OR:
                self.add_instr(OR())
            elif expr.op.token_type == TokenType.EQUAL:
                self.add_instr(CMPEQ())
            elif expr.op.token_type == TokenType.NOT_EQUAL:
                self.add_instr(CMPNE())
            elif expr.op.token_type == TokenType.LESS:
                self.add_instr(CMPLT())
            elif expr.op.token_type == TokenType.LESS_EQ:
                self.add_instr(CMPLE())
            elif expr.op.token_type == TokenType.GREATER:
                self.add_instr(STORE(100))  # Store the top item
                self.add_instr(STORE(99))  # Store the second item
                self.add_instr(LOAD(100))   # Load the top item
                self.add_instr(LOAD(99))   # Load the second item
                self.add_instr(CMPLT()) 
            elif expr.op.token_type == TokenType.GREATER_EQ:
                self.add_instr(STORE(100))  # Store the top item
                self.add_instr(STORE(99))  # Store the second item
                self.add_instr(LOAD(100))   # Load the top item
                self.add_instr(LOAD(99))   # Load the second item
                self.add_instr(CMPLE()) 


            
    def visit_data_type(self, data_type):
        # nothing to do here
        pass

    
    def visit_var_def(self, var_def):
        # nothing to do here
        pass

    
    def visit_simple_term(self, simple_term):
        simple_term.rvalue.accept(self)

        
    def visit_complex_term(self, complex_term):
        complex_term.expr.accept(self)

        
    def visit_simple_rvalue(self, simple_rvalue):
        val = simple_rvalue.value.lexeme
        if simple_rvalue.value.token_type == TokenType.INT_VAL:
            self.add_instr(PUSH(int(val)))
        elif simple_rvalue.value.token_type == TokenType.DOUBLE_VAL:
            self.add_instr(PUSH(float(val)))
        elif simple_rvalue.value.token_type == TokenType.STRING_VAL:
            val = val.replace('\\n', '\n')
            val = val.replace('\\t', '\t')
            self.add_instr(PUSH(val))
        elif val == 'true':
            self.add_instr(PUSH(True))
        elif val == 'false':
            self.add_instr(PUSH(False))
        elif val == 'null':
            self.add_instr(PUSH(None))

    
    def visit_new_rvalue(self, new_rvalue):
        # TODO
        if new_rvalue.array_expr:
            new_rvalue.array_expr.accept(self)
            self.add_instr(ALLOCA())
        else:
            struct_name = new_rvalue.type_name.lexeme
            struct_def = self.struct_defs[struct_name]

            self.add_instr(ALLOCS())
            field_index = 0
            for param in new_rvalue.struct_params:
                self.add_instr(DUP())
                param.accept(self)
                field_name = struct_def.fields[field_index].var_name.lexeme
                field_index += 1
                self.add_instr(SETF(field_name))
                
            
    def visit_var_rvalue(self, var_rvalue):
        # TODO
        if len(var_rvalue.path) == 1:
            # Simple variable assignment
            var_name = var_rvalue.path[0].var_name.lexeme 
            index = self.var_table.get(var_name)
            if var_rvalue.path[0].array_expr:
                iod = self.var_table.get(var_name)
                self.add_instr(LOAD(iod))
                var_rvalue.path[0].array_expr.accept(self)
                self.add_instr(GETI())
            else:
                self.add_instr(LOAD(index))
        else:
            var_name = var_rvalue.path[0].var_name.lexeme
            index = self.var_table.get(var_name)
            if var_rvalue.path[0].array_expr:
                self.add_instr(LOAD(index))
                var_rvalue.path[0].array_expr.accept(self)
                self.add_instr(GETI())
            else:
                self.add_instr(LOAD(index))
            
            for var_ref in var_rvalue.path[1:]: #excludes first and last element
                field_name = var_ref.var_name.lexeme
                self.add_instr(GETF(field_name))
                if var_ref.array_expr:
                    var_ref.array_expr.accept(self)
                    self.add_instr(GETI())
            


