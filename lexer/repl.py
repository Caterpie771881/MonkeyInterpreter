from lexer import Lexer
from lexer.token import TokenType


class REPL():
    """read-eval-print loop for lexer"""
    def __init__(self):...

    def run(self) -> None:
        """运行 REPL"""
        print("Lexer REPL")

        while True:
            code = input(">>> ")
            l = Lexer(code)
            while True:
                token = l.next_token()
                if token.type == TokenType.EOF:
                    break
                print(f"Token:{token.type.value}  Literal:{token.literal}")
