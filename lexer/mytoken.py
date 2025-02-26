from enum import Enum


class TokenType(Enum):
    ILLEGAL = 'ILLEGAL'
    EOF = 'EOF'
    # 标识符 + 字面量
    IDENT = 'IDENT'
    INT = 'INT'
    # 运算符
    ASSIGN = '='
    PLUS = '+'
    MINUS = '-'
    BANG = '!'
    ASTERISK = '*'
    SLASH = '/'
    LT = '<'
    GT = '>'
    EQ = '=='
    NOT_EQ = '!='
    # 分隔符
    COMMA = ','
    SEMICOLON = ';'
    LPAREN = '('
    RPAREN = ')'
    LBRACE = '{'
    RBRACE = '}'
    # 关键字
    FUNCTION = 'FUNCTION'
    LET = 'LET'
    IF = 'IF'
    TRUE = 'TRUE'
    FALSE = 'FALSE'
    ELSE = 'ELSE'
    RETURN = 'RETURN'


class Token():
    def __init__(self, type: TokenType, literal: str):
        self.type = type
        self.literal = literal


keywords: dict[str, TokenType] = {
    'fn': TokenType.FUNCTION,
    'let': TokenType.LET,
    'if': TokenType.IF,
    'true': TokenType.TRUE,
    'false': TokenType.FALSE,
    'else': TokenType.ELSE,
    'return': TokenType.RETURN
}


def lookup_ident(literal: str) -> TokenType:
    """匹配标识符类型, 识别关键字与用户定义标识"""
    return keywords.get(literal, TokenType.IDENT)
