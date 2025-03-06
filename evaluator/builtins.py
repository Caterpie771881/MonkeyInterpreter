from typing import Callable
from lexer.token import Position
from parser import ast
from evaluator import objsys as obj


pyfunc_args = list[obj.MonkeyObj]
pyfunc = Callable[[Position, pyfunc_args], obj.MonkeyObj]

NULL = obj.Null()
TRUE = obj.Boolean(True)
FALSE = obj.Boolean(False)


def len_(pos: Position, args: pyfunc_args) -> obj.MonkeyObj:
    if len(args) != 1:
        return obj.Error(
            pos,
            f"wrong number of arguments. got={len(args)}, want=1"
        )
    match arg := args[0]:
        case obj.String():
            return obj.Integer(len(arg.value))
        case obj.Array():
            return obj.Integer(len(arg.elements))
        case _:
            return obj.Error(
                pos,
                f"argument to `len` not support. got {arg.type().value}"
            )


def exit_(pos: Position, args: pyfunc_args) -> obj.MonkeyObj:
    exit()
    return obj.String("bye")


def puts(pos: Position, args: pyfunc_args) -> obj.MonkeyObj:
    print(*[arg.inspect() for arg in args])
    return NULL


def first(pos: Position, args: pyfunc_args) -> obj.MonkeyObj:
    if len(args) != 1:
        return obj.Error(pos, f"wrong number of arguments. got={len(args)}, want=1")
    
    if args[0].type() != obj.ObjectType.ARRAY_OBJ:
        return obj.Error(pos, f"argument to `first` must be ARRAY. got {args[0].type().value}")
    
    array: obj.Array = args[0]
    if len(array.elements) > 0:
        return array.elements[0]
    return NULL


def last(pos: Position, args: pyfunc_args) -> obj.MonkeyObj:
    if len(args) != 1:
        return obj.Error(pos, f"wrong number of arguments. got={len(args)}, want=1")
    
    if args[0].type() != obj.ObjectType.ARRAY_OBJ:
        return obj.Error(pos, f"argument to `last` must be ARRAY. got {args[0].type().value}")
    
    array: obj.Array = args[0]
    length = len(array.elements)
    if length > 0:
        return array.elements[length-1]
    return NULL


def rest(pos: Position, args: pyfunc_args) -> obj.MonkeyObj:
    if len(args) != 1:
        return obj.Error(pos, f"wrong number of arguments. got={len(args)}, want=1")
    
    if args[0].type() != obj.ObjectType.ARRAY_OBJ:
        return obj.Error(pos, f"argument to `rest` must be ARRAY. got {args[0].type().value}")
    
    array: obj.Array = args[0]
    length = len(array.elements)
    if length > 0:
        new_elements = array.elements[1:]
        return obj.Array(new_elements)
    return NULL


def push(pos: Position, args: pyfunc_args) -> obj.MonkeyObj:
    if len(args) != 2:
        return obj.Error(pos, f"wrong number of arguments. got={len(args)}, want=2")
    
    if args[0].type() != obj.ObjectType.ARRAY_OBJ:
        return obj.Error(pos, f"argument to `push` must be ARRAY. got {args[0].type().value}")
    
    array: obj.Array = args[0]
    element = args[1]
    return obj.Array(array.elements + [element])


class Builtins():
    """内置对象空间"""
    def __init__(self):
        self.__store: dict[str, obj.MonkeyObj] = {}
        self.set("copyright", obj.String(
            "Copyright 2025 Caterpie771881.\nAll Rights Reserved."))
        self.bind_py("len", len_)
        self.bind_py("exit", exit_)
        self.bind_py("puts", puts)
        self.bind_py("first", first)
        self.bind_py("last", last)
        self.bind_py("rest", rest)
        self.bind_py("push", push)

    def set(self, key: str, value: obj.MonkeyObj) -> None:
        if not isinstance(value, obj.MonkeyObj):
            raise ValueError(f"Builtins only store MonkeyObj. not {value.__class__}")
        self.__store[key] = value

    def get(self, key):
        return self.__store.get(key)

    def bind_py(
            self,
            name: str,
            func: pyfunc = None
        ) -> None:
        """将一个 python 函数绑定到内置对象空间"""
        self.set(name, obj.Python(name, func))
