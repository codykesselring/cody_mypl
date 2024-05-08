"""Implementation of the MyPL Virtual Machine (VM).

NAME: <your name here>
DATE: Spring 2024
CLASS: CPSC 326

"""

from mypl_error import *
from mypl_opcode import *
from mypl_frame import *


class VM:

    def __init__(self):
        """Creates a VM."""
        self.struct_heap = {}        # id -> dict
        self.array_heap = {}         # id -> list
        self.next_obj_id = 2024      # next available object id (int)
        self.frame_templates = {}    # function name -> VMFrameTemplate
        self.call_stack = []         # function call stack

    
    def __repr__(self):
        """Returns a string representation of frame templates."""
        s = ''
        for name, template in self.frame_templates.items():
            s += f'\nFrame {name}\n'
            for instr in template.instructions:
                s += f'  {id}: {instr}\n'
        return s

    
    def add_frame_template(self, template):
        """Add the new frame info to the VM. 

        Args: 
            frame -- The frame info to add.

        """
        self.frame_templates[template.function_name] = template

    
    def error(self, msg, frame=None):
        """Report a VM error."""
        if not frame:
            raise VMError(msg)
        pc = frame.pc - 1
        instr = frame.template.instructions[pc]
        name = frame.template.function_name
        msg += f' (in {name} at {pc}: {instr})'
        raise VMError(msg)

    
    #----------------------------------------------------------------------
    # RUN FUNCTION
    #----------------------------------------------------------------------
    
    def run(self, debug=False):
        """Run the virtual machine."""

        # grab the "main" function frame and instantiate it
        if not 'main' in self.frame_templates:
            self.error('No "main" functrion')
        frame = VMFrame(self.frame_templates['main'])
        self.call_stack.append(frame)

        # run loop (continue until run out of call frames or instructions)
        while self.call_stack and frame.pc < len(frame.template.instructions):
            # get the next instruction
            instr = frame.template.instructions[frame.pc]
            # increment the program count (pc)
            frame.pc += 1
            # for debugging:
            if debug:
                print('\n')
                print('\t FRAME.........:', frame.template.function_name)
                print('\t PC............:', frame.pc)
                print('\t INSTRUCTION...:', instr)
                val = None if not frame.operand_stack else frame.operand_stack[-1]
                print('\t NEXT OPERAND..:', val)
                cs = self.call_stack
                fun = cs[-1].template.function_name if cs else None
                print('\t NEXT FUNCTION..:', fun)

            #------------------------------------------------------------
            # Literals and Variables
            #------------------------------------------------------------

            if instr.opcode == OpCode.PUSH:
                frame.operand_stack.append(instr.operand)

            elif instr.opcode == OpCode.POP:
                frame.operand_stack.pop()
                

            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.STORE:
                x = frame.operand_stack.pop()
                mem_addr = instr.operand
                while len(frame.variables) <= mem_addr:
                    frame.variables.append(None)
                frame.variables[mem_addr] = x
            
            elif instr.opcode == OpCode.LOAD:
                mem_addr = instr.operand
                frame.operand_stack.append(frame.variables[mem_addr])
                

            
            #------------------------------------------------------------
            # Operations
            #------------------------------------------------------------

            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.ADD:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                result = y + x
                if type(x) == int or type(y) == int:
                    result = int(result)
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.SUB:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                result = y - x
                if type(x) == int or type(y) == int:
                    result = int(result)
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.MUL:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                result = y * x
                if type(x) == int or type(y) == int:
                    result = int(result)
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.DIV:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                elif x == 0:
                    self.error("can't divide by 0", None)
                result = y / x
                if type(x) == int or type(y) == int:
                    result = int(result)
                
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.CMPLT:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                result = y < x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.CMPLE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                result = y <= x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.CMPEQ:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                result = y == x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.CMPNE:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                result = y != x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.AND:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                result = y and x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.OR:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("operands cant be None during operator use", None)
                result = y or x
                frame.operand_stack.append(result)

            elif instr.opcode == OpCode.NOT:
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("operands cant be None during operator use", None)
                result = not x
                frame.operand_stack.append(result)
            

            #------------------------------------------------------------
            # Branching
            #------------------------------------------------------------


            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.JMP:
                offset = instr.operand
                frame.pc = offset
            elif instr.opcode == OpCode.JMPF:
                x = frame.operand_stack.pop()
                if x == False:
                    offset = instr.operand
                    frame.pc = offset
            
                    
            #------------------------------------------------------------
            # Functions
            #------------------------------------------------------------


            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.CALL:
                fun_name = instr.operand
                new_frame_template = self.frame_templates[fun_name]
                new_frame = VMFrame(new_frame_template)
                self.call_stack.append(new_frame)
                i = new_frame_template.arg_count
                while i > 0:
                    arg = frame.operand_stack.pop()
                    new_frame.operand_stack.append(arg)
                    i -= 1
                frame = new_frame
            
            elif instr.opcode == OpCode.RET:
                return_val = frame.operand_stack.pop()
                self.call_stack.pop()
                if self.call_stack:
                    frame = self.call_stack[-1]
                    frame.operand_stack.append(return_val)
                else:
                    return
                    
            #------------------------------------------------------------
            # Built-In Functions
            #------------------------------------------------------------

            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.WRITE:
                msg = frame.operand_stack.pop()
                if msg == None:
                    msg = "null"
                elif isinstance(msg, bool):
                    if msg:
                        msg = "true"
                    else :
                        msg = "false"
                else:
                    msg = str(msg)
                print(msg, end='')

            elif instr.opcode == OpCode.READ:
                x = input()
                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.LEN:
                x = frame.operand_stack.pop()
                if x == self.next_obj_id -1:
                    x = self.array_heap[x]
                if x == None:
                    self.error("cant find length of nothing")
                elif type(x) != str and type(x) != list:
                    x = str(x)
                length = len(x)
                frame.operand_stack.append(length)

            elif instr.opcode == OpCode.GETC:
                x = frame.operand_stack.pop()
                y = frame.operand_stack.pop()
                if x == None or y == None:
                    self.error("string index error")
                elif y > len(x)-1 or y<0:
                    self.error("string index error")
                frame.operand_stack.append(x[y])

            elif instr.opcode == OpCode.TOINT:
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("None cant become int")
                try:
                    int_value = int(x)
                    frame.operand_stack.append(int_value)
                except ValueError:
                    self.error("Value cannot be converted to int")
                frame.operand_stack.append(int(x))

            elif instr.opcode == OpCode.TODBL:
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("None cant become double")
                try:
                    float_value = float(x)
                    frame.operand_stack.append(float_value)
                except ValueError:
                    self.error("Value cannot be converted to double")
                frame.operand_stack.append(float(x))

            elif instr.opcode == OpCode.TOSTR:
                x = frame.operand_stack.pop()
                if x == None:
                    self.error("None cant become string")
                frame.operand_stack.append(str(x))

            #------------------------------------------------------------
            # Heap
            #------------------------------------------------------------

            # TODO: Fill in rest of ops
            elif instr.opcode == OpCode.ALLOCS:
                oid = self.next_obj_id
                self.next_obj_id += 1
                struct_obj = {}
                self.struct_heap[oid] = struct_obj
                frame.operand_stack.append(oid)

            elif instr.opcode == OpCode.SETF:
                value = frame.operand_stack.pop()
                oid = frame.operand_stack.pop()
                field = instr.operand
                if field == None or oid == None:
                    self.error("struct access can't have None type")
                elif oid not in self.struct_heap:
                    self.error("Invalid object ID for struct access")
                self.struct_heap[oid][field] = value

            elif instr.opcode == OpCode.GETF:
                oid = frame.operand_stack.pop()
                field = instr.operand
                if oid == None:
                    self.error("struct access can't have None type")
                value = self.struct_heap[oid][field]
                if oid not in self.struct_heap:
                    self.error("Invalid object ID for struct access")
                frame.operand_stack.append(value)

            elif instr.opcode == OpCode.ALLOCA:
                arr_len = frame.operand_stack.pop()
                if arr_len is None or arr_len < 0:
                    self.error("Invalid size for array allocation")
                array_obj = [None] * arr_len
                oid = self.next_obj_id
                self.next_obj_id += 1
                self.array_heap[oid] = array_obj
                frame.operand_stack.append(oid)
            
            elif instr.opcode == OpCode.SETI:
                value = frame.operand_stack.pop()
                index = frame.operand_stack.pop()
                oid = frame.operand_stack.pop()
                if index == None or oid == None:
                    self.error(f"array access can't have None type, value={value}, index={index}, oid={oid}")
                elif oid not in self.array_heap or index < 0 or index >= len(self.array_heap[oid]):
                    self.error(f"Invalid index or object ID for array access {value} {index} {oid} {len(self.array_heap[oid])}")
                self.array_heap[oid][index] = value
            
            elif instr.opcode == OpCode.GETI:
                index = frame.operand_stack.pop()
                oid = frame.operand_stack.pop()
                if index == None or oid == None:
                    self.error("array access can't have None type")
                elif oid not in self.array_heap:
                    self.error(f"Invalid object ID for array access, oid = {oid}")
                elif index < 0 or index >= len(self.array_heap[oid]):
                    self.error(f"Invalid index for array access, index = {index}")
                value = self.array_heap[oid][index]
                frame.operand_stack.append(value)
            #------------------------------------------------------------
            # Special 
            #------------------------------------------------------------

            elif instr.opcode == OpCode.DUP:
                x = frame.operand_stack.pop()
                frame.operand_stack.append(x)
                frame.operand_stack.append(x)

            elif instr.opcode == OpCode.NOP:
                # do nothing
                pass

            else:
                self.error(f'unsupported operation {instr}')
