from lexer import Lexer
from lexer.token import Token, TokenType, Position
from parser import Parser, ParserError
from parser.ast import Node, Program
from enum import Enum
import json
from typing import Callable


class Mode(Enum):
    tostring = 'tostring'
    json = 'json'


def get_dict(node: Node | Token) -> dict:
    result = {}
    for attr in node.__dict__:
        v = node.__dict__.get(attr)
        match v:
            case list():
                result[attr] = []
                for n in v:
                    result[attr].append(get_dict(n))
            case Node() | Token():
                result[attr] = get_dict(v)
            case TokenType():
                result[attr] = v.name
            case Position():
                pass
            case _:
                result[attr] = v
    return result


class REPL():
    """read-eval-print loop for parser"""
    def __init__(self, mode: Mode = Mode.tostring):
        self.mode = mode
        self.print: Callable[[Program], None] = None
        match self.mode:
            case Mode.tostring:
                self.print = self.tostring
            case Mode.json:
                self.print = self.json
            case _:
                print(f"Unknown REPL Mode: {self.mode}, run as tostring Mode")
                self.mode = Mode.tostring
                self.print = self.tostring

    def run(self) -> None:
        """运行 REPL"""
        print("Parser REPL")
        print(f"Mode: {self.mode.value}")
        while True:
            code = input(">>> ")
            self.eval_print(code)
    
    @staticmethod
    def raise_error(errors: list[ParserError]) -> None:
        """打印 Parser 的错误信息"""
        print(f"parser has {len(errors)} errors:")
        for msg in errors:
            print(f"  line {msg.pos.y} column {msg.pos.x}, {msg}")

    @staticmethod
    def tostring(program: Program) -> None:
        print(program.tostring())
    
    @staticmethod
    def json(program: Program) -> None:
        output = get_dict(program).get("statements")
        pretty_output = json.dumps(output, indent=4)
        print(pretty_output)

    def eval_print(self, code: str) -> None:
        p = Parser(Lexer(code))
        program = p.parse_program()
        errors = p.errors
        if len(errors) > 0:
            self.raise_error(errors)
        else:
            self.print(program)

