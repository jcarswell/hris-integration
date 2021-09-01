from . import config

class CSVSafe:
    def __init__(self,input) -> str:
        try:
            getattr(self,type(input).__name__)(input)
        except AttributeError:
            raise TypeError(f"{type(input)} is not valid for output")

    def str(self,input:str):
        self.value = input

    def int(self,input:int):
        self.value = str(input)

    def bool(self,input:bool):
        fmt = config.get_config(config.CAT_CONFIG,config.CONFIG_BOOL_EXPORT).split(',',2)
        if input:
            self.value = fmt[1]
        else:
            self.value = fmt[2]

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
