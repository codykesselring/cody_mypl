# MyPL Language Overview  
This repository contains a python interpreter of my own programming language 'MyPL', which is syntactically similar to java and c++ with the filetype .mypl. This interpretter creates a token stream in the lexer, passes the token stream into the parser, which looks for syntax errors and creates an abstract search tree that is passed into the semantic checker that primarily looks for type errors. Once the front end of the compilation pipeline is complete, the abstract search tree is passed into a code generator that simplifies the code into opcodes that dissects the program and takes it down a level of abstraction, these are down using a stack system instead of assembly. Once the code generation is complete, it is then executed on a VM. 
# Executing Files
To run programs on the myPL interpreter, type 'python mypl.py [path/file_name]' into the command line, which will run the program; console outputs will be displayed in the terminal.  

There are test programs in the directory that display the capabilities of my languae, these files are inside the 'examples' folder and can be ran like so in the command line: 'python mypl.py exec-17-tree.mypl' will execute the file exec-17-tree.mypl and output  
Tree Values: 1 2 5 7 10 12 13 14 15  
Tree Height: 5 into the terminal  

Too see what the opcode code generation looks like for a given program, add --ir to the end of the command on the command line like so: 'python mypl.py examples/exec-9-fib.mypl --r'  
This will output the list of low-level commands that represent the high level code, this is what the opcodes look for examples/exec-9-fib.mypl:  
Frame fib  
  <built-in function id>: OpCode.STORE(0)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.PUSH(1)  
  <built-in function id>: OpCode.CMPLE()  
  <built-in function id>: OpCode.JMPF(8)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.RET()  
  <built-in function id>: OpCode.JMP(19)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.PUSH(2)  
  <built-in function id>: OpCode.SUB()  
  <built-in function id>: OpCode.CALL(fib)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.PUSH(1)  
  <built-in function id>: OpCode.SUB()  
  <built-in function id>: OpCode.CALL(fib)  
  <built-in function id>: OpCode.ADD()  
  <built-in function id>: OpCode.RET()  
  <built-in function id>: OpCode.NOP()  
  <built-in function id>: OpCode.PUSH()  
  <built-in function id>: OpCode.RET()  

Frame main  
  <built-in function id>: OpCode.PUSH(0)  
  <built-in function id>: OpCode.STORE(0)  
  <built-in function id>: OpCode.PUSH(26)  
  <built-in function id>: OpCode.STORE(1)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.LOAD(1)  
  <built-in function id>: OpCode.CMPLT()  
  <built-in function id>: OpCode.JMPF(18)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.CALL(fib)  
  <built-in function id>: OpCode.CALL(print_result)  
  <built-in function id>: OpCode.LOAD(0)  
  <built-in function id>: OpCode.PUSH(1)  
  <built-in function id>: OpCode.ADD()  
  <built-in function id>: OpCode.STORE(0)  
  <built-in function id>: OpCode.JMP(4)  
  <built-in function id>: OpCode.NOP()  
  <built-in function id>: OpCode.PUSH()  
  <built-in function id>: OpCode.RET()  

