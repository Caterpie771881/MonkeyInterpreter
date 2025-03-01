from lexer import Lexer
from lexer.token import Token, TokenType
from parser import Parser
from parser.ast import Node
from enum import Enum


class Mode(Enum):
    tostring = 'tostring'
    json = 'json'


class REPL():
    """read-eval-print loop for parser"""
    def __init__(self, mode: Mode = Mode.tostring):
        self.mode = mode

    def run(self) -> None:
        """运行 REPL"""
        print("Parser REPL")
        match self.mode:
            case Mode.tostring:
                self.tostring()
            case Mode.json:
                self.json()
            case _:
                print(f"Unknown REPL Mode: {self.mode}, run as tostring Mode")
                self.tostring()
    
    def raise_error(self, errors: list) -> None:
        """打印 Parser 的错误信息"""
        print(f"parser has {len(errors)} errors:")
        for msg in errors:
            print(f"parser error: {msg}")
    
    def tostring(self) -> None:
        """以 tostring 形式输出 AST"""
        print("Mode: tostring")
        while True:
            code = input(">>> ")
            p = Parser(Lexer(code))
            program = p.parse_program()
            errors = p.errors
            if len(errors) > 0:
                self.raise_error(errors)
            else:
                print(program.tostring())
    
    def json(self) -> None:
        """以 json 形式输出 AST"""
        import json
        def get_json(node: Node) -> dict:
            result = {}
            for attr in node.__dict__:
                v = node.__dict__.get(attr)
                match v:
                    case list():
                        result[attr] = []
                        for n in v:
                            result[attr].append(get_json(n))
                    case Node() | Token():
                        result[attr] = get_json(v)
                    case TokenType():
                        result[attr] = v.name
                    case _:
                        result[attr] = v
            return result
        
        print("Mode: json")
        while True:
            code = input(">>> ")
            p = Parser(Lexer(code))
            program = p.parse_program()
            errors = p.errors
            if len(errors) > 0:
                self.raise_error(errors)
            else:
                output = get_json(program).get("statements")
                pretty_output = json.dumps(output, indent=4)
                print(pretty_output)
