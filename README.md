# MyPL Language Overview  
This repository contains a python interpreter of my own programming language 'MyPl', which is syntactically similar to java and c++ with the filetype .mypl. This interpretter creates a token stream in the lexer, passes the token stream into the paser, which looks for syntax errors and creates an abstract search tree that is passed into the semantic checker that primarily looks for type errors. Once the front end of the compilation pipeline is complete, the abstract search tree is passed into a code generator that simplifies the code into opcodes that dissects the program and takes it down a level of abstraction, these are down using a stack system instead of assembly. Once the code generation is complete, it is then executed on a VM. 
# Executing Files
To run programs on the myPL interpreter, type 'python mypl.py [path/file_name]' into the command line, which will run the program; console outputs will be displayed in the terminal.  

There are test programs in the directory that display the capabilities of my languae, these files are inside the 'examples' folder and can be ran like so in the command line: 'python mypl.py exec-17-tree.mypl' will execute the file exec-17-tree.mypl and output  
Tree Values: 1 2 5 7 10 12 13 14 15  
Tree Height: 5 into the terminal  

