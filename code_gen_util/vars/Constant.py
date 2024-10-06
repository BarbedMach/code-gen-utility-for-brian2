from code_gen_util.detail.interfaces.IDefinition import IDefinition
from code_gen_util.detail.global_var import GlobalVar

class Constant(GlobalVar, IDefinition):
    def __init__(self, type: str, name: str, value):
        super().__init__(name, value)
        self.type = type

    def generateDefinition(self):
        return f'static const {self.type} {self.name} = {self.value};\n'
