from lexer import Lexer
from lexer.token import TokenType


class REPL():
    """read-eval-print loop for lexer"""
    def __init__(self):
        self.current_line = 1


    def run(self) -> None:
        """运行 REPL"""
        print("Lexer REPL")
        while True:
            code = input(">>> ")
            self.eval_print(code)
    
    
    def eval_print(self, code: str) -> None:
        l = Lexer(code)
        empty = True
        while True:
            token = l.next_token()
            if token.type == TokenType.EOF:
                break
            empty = False
            if token.position.y > self.current_line:
                self.current_line = token.position.y
                print('')
            print(f"[{token.type.name} '{token.literal}']", end="")
        if not empty: print('')
