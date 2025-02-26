from lexer import Lexer
from mytoken import TokenType

print("Lexer REPL")

while True:
    code = input(">>> ")
    l = Lexer(code)
    while True:
        token = l.next_token()
        if token.type == TokenType.EOF:
            break
        else:
            print(f"Token:{token.type.value}  Literal:{token.literal}")
