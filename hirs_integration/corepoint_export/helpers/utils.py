# Copyright: (c) 2022, Josh Carswell <josh.carswell@thecarswells.ca>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt) 

from . import config

class CSVSafe:
    def parse(self,input) -> str:
        try:
            getattr(self,type(input).__name__)(input)
            return self.__str__()
        except AttributeError:
            raise TypeError(f"{type(input)} is not valid for output")

    def str(self,input:str):
        self.value = input

    def int(self,input:int):
        self.value = str(input)

    def bool(self,input:bool):
        fmt = config.get_config(config.CAT_CONFIG,config.CONFIG_BOOL_EXPORT).split(',',2)
        if input:
            self.value = fmt[0]
        else:
            self.value = fmt[1]

    def bytes(self,input:bytes):
        self.str(input.decode('utf-8'))

    def float(self,input:float):
        self.value = str(input)

    def complex(self,input:complex):
        self.value = str(input.real)

    def bytearray(self,input:bytearray):
        self.bytes(input)

    def NoneType(self,input):
        self.value = ""

    def __str__(self):
        if (' ' in self.value or ',' in self.value or '\t' in self.value
            or '"' in self.value or '\'' in self.value):
            return f'"{self.value}"'
        else:
            return self.value
