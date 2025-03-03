from abc import ABC, abstractmethod
from enum import Enum
from lexer.token import Position


class Environment():
    """解释器运行环境"""
    def __init__(self):
        self.store: dict[str, MonkeyObj] = {}
    
    def get(self, name: str):
        return self.store.get(name)

    def set(self, name: str, val: "MonkeyObj"):
        self.store[name] = val
        return val


class ObjectType(Enum):
    INTEGER_OBJ = "INTEGER"
    BOOLEAN_OBJ = "BOOLEAN"
    NULL_OBJ = "NULL"
    RETURN_VALUE_OBJ = "RETURN_VALUE"
    ERROR_OBJ = "ERROR_OBJ"


class MonkeyObj(ABC):
    """Monkey 类型接口"""
    @abstractmethod
    def type(self) -> ObjectType:...

    @abstractmethod
    def inspect(self) -> str:...


class Integer(MonkeyObj):
    """整型"""
    def __init__(self, value: int = None):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.INTEGER_OBJ
    
    def inspect(self) -> str:
        return str(self.value)


class Boolean(MonkeyObj):
    """布尔值"""
    def __init__(self, value: bool = None):
        self.value = value
    
    def type(self):
        return ObjectType.BOOLEAN_OBJ
    
    def inspect(self):
        return str(self.value)
    

class Null(MonkeyObj):
    """空值"""
    def __init__(self):...

    def type(self):
        return ObjectType.NULL_OBJ
    
    def inspect(self):
        return "null"


class ReturnValue(MonkeyObj):
    """返回值"""
    def __init__(self, value: MonkeyObj = None):
        self.value = value
    
    def type(self):
        return ObjectType.RETURN_VALUE_OBJ
    
    def inspect(self):
        if not self.value:
            return "null"
        return self.value.inspect()


class Error(MonkeyObj):
    """错误基类"""
    def __init__(
            self,
            pos: Position = Position(0, 0),
            msg: str = '',
        ):
        self.pos = pos
        self.msg = msg
    
    def type(self):
        return ObjectType.ERROR_OBJ
    
    def inspect(self):
        return f"RUNTIME ERROR: line {self.pos.y}, column {self.pos.x}\n  {self.msg}"
