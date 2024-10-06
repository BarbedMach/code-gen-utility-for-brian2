from code_gen_util.detail.interfaces.IDefinition import IDefinition
from code_gen_util.detail.interfaces.IArray import IArray
from code_gen_util.detail.global_var import GlobalVar
import platform

class Array2D(GlobalVar, IDefinition, IArray):
    def __init__(self, name: str, size_list: list[int], value, addr: int):
        super().__init__(name, value)
        self.size_list = size_list 
        self.addr = addr

    def generateDefinition(self):
        return f'static inline double** {self.name} = nullptr;\n'
    
    def generateAllocationBlock(self):
        result = ''
        
        if platform.system() == 'Windows':
            result += f'LPVOID {self.name}_addr = (LPVOID){self.addr};\n'
            result += f'SIZE_T {self.name}_size = sizeof(double*) * {len(self.size_list)};\n'
            result += f'DWORD {self.name}_flags = MEM_COMMIT | MEM_RESERVE;\n'
            result += f'DWORD {self.name}_prot = PAGE_READWRITE;\n'
    
        elif platform.system() == 'Linux':
            result += f'void* {self.name}_addr = (void*){self.addr};\n'
            result += f'size_t {self.name}_size = sizeof(double*) * {len(self.size_list)};\n'
            result += f'int {self.name}_flags = MAP_SHARED | MAP_ANONYMOUS | MAP_FIXED_NOREPLACE;\n'
            result += f'int {self.name}_prot = PROT_READ | PROT_WRITE;\n'
        
        return result
    
    def generateInitializerFunction(self):
        result = ''

        if platform.system() == 'Windows':
            result += f'int init_{self.name}() {{\n'
            result += f'MEMORY_BASIC_INFORMATION memInfo;\n'
            result += f'SIZE_T result = VirtualQuery({self.name}_addr, &memInfo, sizeof(memInfo));\n'
            result += 'if (memInfo.State == MEM_FREE) {\n'
            result += f'LPVOID {self.name}_memory = VirtualAlloc({self.name}_addr, {self.name}_size, {self.name}_flags, {self.name}_prot);\n'
            result += f'{self.name} = (double**){self.name}_memory;\n'
            result += '} else {\n'
            result += f'{self.name} = (double**){self.name}_addr;\n'
            result += '}\n'
            result += f"std::cout << {self.name} << std::endl;\n"
        
        elif platform.system() == 'Linux':
            result += f'int init_{self.name}() {{\n'
            result += f'void* ptr_{self.name} = (void*) mmap({self.name}_addr, {self.name}_size, {self.name}_prot, {self.name}_flags, -1, 0);\n'
            result += f'if (ptr_{self.name} != MAP_FAILED) {{\n'
            result += f'{self.name} = (double**)ptr_{self.name};\n'
            result += '} else {\n'
            result += f'{self.name} = (double**){self.name}_addr;\n'
            result += '}\n'
            result += f"std::cout << {self.name} << std::endl;\n"

        for idx, sz in enumerate(self.size_list):
            result += f'auto* ptr_{idx} = new double[{sz}];\n'
            result += f'{self.name}[{idx}] = ptr_{idx};\n'
            result += f'for (int i = 0; i < {sz}; ++i) {{\n'
            result += f'ptr_{idx}[i] = {self.value};\n'
            result += '}\n'

        result += 'return 0;\n'
        result += '}\n'

        return result
    
    def generateCallToInitializer(self):
        return f'int {self.name}_init_call = init_{self.name}();\n'

    def generateDeleteCall(self):
        result = f'auto d_p_{self.name} = (double**){self.addr};\n'

        for idx, sz in enumerate(self.size_list):
            result += f'delete[] d_p_{self.name}[{idx}];\n'

        if platform.system() == 'Windows':
            result += f"VirtualFree((LPVOID)d_p_{self.name}, 0, MEM_RELEASE);\n"

        elif platform.system() == 'Linux':
            result += f"munmap((void*)d_p_{self.name}, {len(self.size_list)});\n"

        return result