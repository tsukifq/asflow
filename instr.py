class Instruction:
    def __init__(self):
        self._name = ""
        self._description = ""

    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, name):
        self._name = name

    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, description):
        self._description = description

