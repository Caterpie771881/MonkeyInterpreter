import evaluator
from lexer import Lexer
from parser import Parser
from parser.repl import REPL as RPPL
from evaluator.objsys import Environment


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
    def run(self) -> None:
        print(PROMPT)
        env = Environment()
        while True:
            code = input(">>> ")
            p = Parser(Lexer(code))
            program = p.parse_program()
            if len(p.errors):
                RPPL.raise_error(p.errors)
                continue
            evaluated = evaluator.Eval(program, env)
            if evaluated != None:
                print(evaluated.inspect())
