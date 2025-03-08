from abc import ABC, abstractmethod
from enum import Enum
from typing import Callable
from lexer.token import Position
from parser import ast


class Environment():
    """解释器运行环境"""
    def __init__(self, outer: "Environment" = None):
        self.store: dict[str, MonkeyObj] = {}
        self.outer = outer
    
    def get(self, name: str):
        obj = self.store.get(name)
        if obj == None and self.outer != None:
            return self.outer.get(name)
        return obj

    def set(self, name: str, val: "MonkeyObj"):
        self.store[name] = val
        return val


class ObjectType(Enum):
    INTEGER_OBJ         = "INTEGER"
    BOOLEAN_OBJ         = "BOOLEAN"
    NULL_OBJ            = "NULL"
    RETURN_VALUE_OBJ    = "RETURN_VALUE"
    ERROR_OBJ           = "ERROR"
    FUNCTION_OBJ        = "FUNCTION"
    STRING_OBJ          = "STRING"
    PYTHON_OBJ          = "PYTHON"
    ARRAY_OBJ           = "ARRAY"
    HASH_OBJ            = "HASH"
    HASHPAIR_OBJ        = "HASHPAIR"


class MonkeyObj(ABC):
    """Monkey 类型接口"""
    @abstractmethod
    def type(self) -> ObjectType:...

    @abstractmethod
    def inspect(self) -> str:...

HashKey = tuple[ObjectType, int]

class Hashable(ABC):
    """可哈希抽象类"""
    @abstractmethod
    def hashkey(self) -> HashKey:...


class Integer(MonkeyObj, Hashable):
    """整型"""
    def __init__(self, value: int = None):
        self.value = value

    def type(self) -> ObjectType:
        return ObjectType.INTEGER_OBJ
    
    def inspect(self) -> str:
        return str(self.value)
    
    def hashkey(self) -> HashKey:
        return self.type(), self.value


class Boolean(MonkeyObj, Hashable):
    """布尔值"""
    def __init__(self, value: bool = None):
        self.value = value
    
    def type(self):
        return ObjectType.BOOLEAN_OBJ
    
    def inspect(self):
        return str(self.value)
    
    def hashkey(self) -> HashKey:
        if self.value:
            return self.type(), 1
        return self.type(), 0


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


class Function(MonkeyObj):
    """函数对象"""
    def __init__(
            self,
            parameters: list[ast.Identifier] = None,
            body: ast.BlockStatement = None,
            env: Environment = None
        ):
        if parameters:
            self.parameters = parameters
        else:
            self.parameters: list[ast.Identifier] = []
        self.body = body
        if env:
            self.env = env
        else:
            self.env: Environment = Environment()
    
    def type(self):
        return ObjectType.FUNCTION_OBJ
    
    def inspect(self):
        params = [p.tostring() for p in self.parameters]
        return f"fn({','.join(params)}) {{\n{self.body.tostring()}\n}}"


class String(MonkeyObj, Hashable):
    def __init__(self, value: str = ''):
        self.value = value
    
    def type(self):
        return ObjectType.STRING_OBJ

    def inspect(self):
        return f'"{self.value}"'
    
    def hashkey(self) -> HashKey:
        return self.type(), hash(self.value)


class Python(MonkeyObj):
    """python 对象,
    该对象持有一个 python 函数, 能直接使用宿主语言生成 MonkeyObj"""
    def __init__(
            self,
            name: str = '',
            func: Callable[[Position, list[MonkeyObj]], MonkeyObj] = None
        ):
        self.name = name
        self.func = func

    def type(self):
        return ObjectType.PYTHON_OBJ
    
    def inspect(self):
        return f"{self.name}<py>(...){{...}}"


class Array(MonkeyObj):
    """数组对象"""
    def __init__(self, elements: list[MonkeyObj] = None):
        if elements:
            self.elements = elements
        else:
            self.elements: list[MonkeyObj] = []
    
    def type(self) -> ObjectType:
        return ObjectType.ARRAY_OBJ

    def inspect(self) -> str:
        return f"[{', '.join([e.inspect() for e in self.elements])}]"


class HashPair(MonkeyObj):
    """哈希键值对对象"""
    def __init__(
            self,
            key: MonkeyObj | Hashable = None,
            value: MonkeyObj = None
        ):
        self.key = key
        self.value = value
    
    def type(self) -> ObjectType:
        return ObjectType.HASHPAIR_OBJ
    
    def inspect(self) -> str:
        return f"{self.key.inspect()}:{self.value.inspect()}"


class Hash(MonkeyObj):
    """哈希表对象"""
    def __init__(
            self,
            pairs: dict[HashKey, HashPair] = None
        ):
        if pairs:
            self.pairs = pairs
        else:
            self.pairs: dict[HashKey, HashPair] = {}            
    
    def type(self) -> ObjectType:
        return ObjectType.HASH_OBJ

    def inspect(self) -> str:
        pairs = []
        for p in self.pairs.values():
            pairs.append(p.inspect())
        return f"{{{', '.join(pairs)}}}"
