To run programs on the myPL interpreter, type 'python mypl.py [path/file_name]' into the command line, which will run the program; console outputs will be displayed in the terminal.

<<<<<<< HEAD
There are test programs in the directory that display the capabilities of classes, these are named 'test_[rest].mypl' for example: 'python mypl.py test_class_bst.mypl' will execute the file test_class_bst.mypl and output Tree Values: 1 2 5 7 10 12 13 14 15 Tree Height: 5 into the terminal

For my myPL addition I chose classes, which are syntactically defined like this:

![image](https://github.com/Gonzaga-CPSC-326-Spring-2024/project-codykesselring/assets/115512973/720790c2-5c05-4d74-a8d4-a0d5ac30f68a)

which is similar to the initialization and definition of structs, except with associated methods within the definition that can be called elsewhere.

video explanation link: https://youtu.be/zx_h64VoTJc 
=======
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
>>>>>>> b84a1f7d8aeac269cb8ae912145faeb10501b1c2
