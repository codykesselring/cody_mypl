To run programs on the myPL interpreter, type 'python mypl.py [path/file_name]' into the command line, which will run the program; console outputs will be displayed in the terminal.

There are test programs in the directory that display the capabilities of classes, these are named 'test_[rest].mypl'
for example:
'python mypl.py test_class_bst.mypl' will execute the file test_class_bst.mypl and output
Tree Values: 1 2 5 7 10 12 13 14 15 
Tree Height: 5
into the terminal


For my myPL addition I chose classes, which are syntactically defined like this:
class myClass{
    double test0;
    int test1;
    void example_method(){
      print(this.test1)
    }
    int example_return(int x){
      this.test1 = this.test1 + x;
      return this.test1
    }
}
void main(){
    myClass example = new myClass(14.0, 10);
    int assign = example.example_return();
    example.example_method();
}
which is similar to the initialization and definition of structs, except with associated methods within the definition that can be called elsewhere.
