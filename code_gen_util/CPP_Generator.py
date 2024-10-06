from code_gen_util.vars.Constant import Constant
from code_gen_util.vars.Array1D import Array1D
from code_gen_util.vars.Array2D import Array2D
from code_gen_util.AddressHandler import AddressHandler
import platform

class CPP_Generator:
    def __init__(self, initial_addr: int = 0x00400000):
        self.address_handler = AddressHandler(initial_addr)
        self.headers: list[str] = []
        self.constants: list[Constant] = []
        self.array1Ds: list[Array1D] = []
        self.array2Ds: list[Array2D] = []
        self.functions: list[str] = []

    def add_header(self, header: str):
        self.headers.append(f'#include "{header}"\n')

    def new_constant(self, type: str, name: str, value):
        self.constants.append(Constant(type, name, value))

    def new_array1d(self, name: str, size: int, value):
        address = self.address_handler.push(size)
        self.array1Ds.append(Array1D(name, size, value, address))

    def new_array2d(self, name: str, size_list: list[int], value):
        address = self.address_handler.push(len(size_list))
        self.array2Ds.append(Array2D(name, size_list, value, address))

    def add_cpp_func(self, function_as_string):
        self.functions.append(function_as_string)


    def generate_delete_call(self):
        result = ""

        for arrd1 in self.array1Ds:
            result += arrd1.generateDeleteCall()

        for arrd2 in self.array2Ds:
            result += arrd2.generateDeleteCall()

        return result

    def generate(self, file_id):
        with open(file_id, 'w') as file:
            file.write('''#pragma once\n#include <iostream>\n''')
            
            if platform.system() == 'Windows':
                file.write('#include <Windows.h>\n')
            elif platform.system() == 'Linux':
                file.write('#include <sys/mman.h>\n')

            file.write('''\n//Headers: \n//---------------------\n\n''')
            for header in self.headers:
                file.write(header)

            file.write('''\n//Global Constants: \n//---------------------\n\n''')
            for c in self.constants:
                file.write(c.generateDefinition())
            
            for arrayd1 in self.array1Ds:
                file.write(arrayd1.generateDefinition())
            
            for arrayd2 in self.array2Ds:
                file.write(arrayd2.generateDefinition())

            file.write('''\n//Allocation Chunks: \n//---------------------\n\n''')

            for arrayd1 in self.array1Ds:
                file.write(arrayd1.generateAllocationBlock())

            for arrayd2 in self.array2Ds:
                file.write(arrayd2.generateAllocationBlock())

            file.write('''\n//Initializers: \n//---------------------\n\n''')

            for arrayd1 in self.array1Ds:
                file.write(arrayd1.generateInitializerFunction())
            
            for arrayd2 in self.array2Ds:
                file.write(arrayd2.generateInitializerFunction())

            file.write('''\n//Call to Initializers: \n//---------------------\n\n''')

            for arrayd1 in self.array1Ds:
                file.write(arrayd1.generateCallToInitializer())
            
            for arrayd2 in self.array2Ds:
                file.write(arrayd2.generateCallToInitializer())

            file.write('''\n//Functions: \n//---------------------\n\n''')

            for function in self.functions:
                file.write(function + '\n')
            
        

            


            

            

            
        