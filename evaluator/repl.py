import evaluator
from lexer import Lexer
from parser import Parser
from parser.repl import REPL as RPPL
from evaluator.objsys import Environment
from evaluator.builtins import NULL


PROMPT = """\
.------..------..------..------..------..------.
|M.--. ||O.--. ||N.--. ||K.--. ||E.--. ||Y.--. |
| (\/) || :/\: || :(): || :/\: || (\/) || (\/) |
| :\/: || :\/: || ()() || :\/: || :\/: || :\/: |
| '--'M|| '--'O|| '--'N|| '--'K|| '--'E|| '--'Y|
`------'`------'`------'`------'`------'`------'
Monkey v1.0 | Interpreter made by python3.10+\
"""


class REPL():
    """real read-eval-print loop, nice ^u^"""
    def __init__(self):
        self.env = Environment()    
    
    def run(self) -> None:
        print(PROMPT)
        while True:
            code = input(">>> ")
            self.eval_print(code)
    
    def eval_print(self, code: str) -> None:
        p = Parser(Lexer(code))
        program = p.parse_program()
        if len(p.errors):
            RPPL.raise_error(p.errors)
            return
        evaluated = evaluator.Eval(program, self.env)
        if evaluated != None and evaluated != NULL:
            print(evaluated.inspect())
