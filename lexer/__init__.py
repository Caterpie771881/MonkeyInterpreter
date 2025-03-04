from lexer.token import TokenType
from lexer.token import Token
from lexer.token import Position
from lexer.token import lookup_ident


def is_letter(ch: str) -> bool:
    """判断是否为字母的辅助方法"""
    return (
        ('a' <= ch and ch <= 'z')
        or ('A' <= ch and ch <= 'Z')
        or ch == '_'
    )


def is_space(ch: str) -> bool:
    """判断是否为空白符的辅助方法"""
    return (
        ch == ' '
        or ch == '\t'
        or ch == '\n'
        or ch == '\r'
    )


def is_digit(ch: str) -> bool:
    """判断是否为数字的辅助方法"""
    return ch >= '0' and ch <= '9'


class Lexer():
    """词法分析器"""
    def __init__(self, input_: str):
        self.__input: str = input_
        self.__front_idx: int = 0
        self.__back_idx: int = 0
        self.__current: str = ''
        self.__pos: Position = Position(0, 1)
        self.read_char()
    

    def read_char(self) -> None:
        """向前读取单个字符"""
        if self.__back_idx >= len(self.__input):
            self.__current = ''
        else:
            self.__current = self.__input[self.__back_idx]
            if self.__current == '\n':
                self.__pos.x = 0
                self.__pos.y += 1
            else:
                self.__pos.x += 1
        self.__front_idx = self.__back_idx
        self.__back_idx += 1
    

    def read_identifier(self) -> str:
        """读取标识符"""
        position = self.__front_idx
        while is_letter(self.__current):
            self.read_char()
        return self.__input[position:self.__front_idx]
    

    def read_number(self) -> str:
        """读取数字"""
        position = self.__front_idx
        while is_digit(self.__current):
            self.read_char()
        return self.__input[position:self.__front_idx]


    def read_string(self) -> str:
        """读取字符串"""
        position = self.__front_idx
        while True:
            self.read_char()
            if self.__current == '"' or self.__current == '':
                break
        return self.__input[position + 1: self.__front_idx]


    def skipspace(self) -> None:
        """跳过空白符"""
        while is_space(self.__current):
            self.read_char()
    

    def peek_char(self) -> str:
        """“窥探”下一个字符"""
        if self.__back_idx >= len(self.__input):
            return ''
        else:
            return self.__input[self.__back_idx]


    def next_token(self) -> Token:
        """lexer核心功能: 获取下一个标记"""
        tok: Token

        self.skipspace()

        ch = self.__current
        pos = Position(self.__pos.x, self.__pos.y)
        match ch:
            case '=':
                if self.peek_char() == '=':
                    self.read_char()
                    tok = Token(TokenType.EQ, str(ch) + str(self.__current), pos)
                else:
                    tok = Token(TokenType.ASSIGN, ch, pos)
            
            case '+':
                tok = Token(TokenType.PLUS, ch, pos)
            
            case '-':
                tok = Token(TokenType.MINUS, ch, pos)
            
            case '!':
                if self.peek_char() == '=':
                    self.read_char()
                    tok = Token(TokenType.NOT_EQ, str(ch) + str(self.__current), pos)
                else:
                    tok = Token(TokenType.BANG, ch, pos)
            
            case '*':
                tok = Token(TokenType.ASTERISK, ch, pos)
            
            case '/':
                tok = Token(TokenType.SLASH, ch, pos)
            
            case '<':
                tok = Token(TokenType.LT, ch, pos)
            
            case '>':
                tok = Token(TokenType.GT, ch, pos)
            
            case ',':
                tok = Token(TokenType.COMMA, ch, pos)
            
            case ';':
                tok = Token(TokenType.SEMICOLON, ch, pos)
            
            case '(':
                tok = Token(TokenType.LPAREN, ch, pos)
            
            case ')':
                tok = Token(TokenType.RPAREN, ch, pos)
            
            case '{':
                tok = Token(TokenType.LBRACE, ch, pos)
            
            case '}':
                tok = Token(TokenType.RBRACE, ch, pos)
            
            case '"':
                tok = Token(TokenType.STRING, self.read_string(), pos)
            
            case '':
                tok = Token(TokenType.EOF, '', pos)
            
            case _:
                if is_letter(ch):
                    literal = self.read_identifier()
                    toktype = lookup_ident(literal)
                    tok = Token(toktype, literal, pos)
                    return tok
                elif is_digit(ch):
                    tok = Token(TokenType.INT, self.read_number(), pos)
                    return tok
                else:
                    tok = Token(TokenType.ILLEGAL, ch, pos)
            
        self.read_char()
        return tok

