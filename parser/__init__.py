import parser.ast as ast
from lexer import Lexer
from lexer.token import Token
from lexer.token import TokenType
from typing import Callable
from enum import IntEnum


class ExpLevel(IntEnum):
    """表达式优先级"""
    LOWEST      = 0
    EQUALS      = 1 # ==
    LESSGREATER = 2 # > or <
    SUM         = 3 # +
    PRODUCT     = 4 # *
    PREFIX      = 5 # -X or !X
    CALL        = 6 # func(X)


token_level: dict[TokenType, ExpLevel] = {
    TokenType.EQ:       ExpLevel.EQUALS,
    TokenType.NOT_EQ:   ExpLevel.EQUALS,
    TokenType.LT:       ExpLevel.LESSGREATER,
    TokenType.GT:       ExpLevel.LESSGREATER,
    TokenType.PLUS:     ExpLevel.SUM,
    TokenType.MINUS:    ExpLevel.SUM,
    TokenType.SLASH:    ExpLevel.PRODUCT,
    TokenType.ASTERISK: ExpLevel.PRODUCT,
}
"""符号的优先级表"""


nuds = Callable[[], ast.Expression]
"""前缀解析函数规范"""
leds = Callable[[ast.Expression], ast.Expression]
"""中缀解析函数规范"""


class Parser():
    """语法分析器"""
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.cur_tok: Token = None
        self.peek_tok: Token = None
        self.errors: list[str] = []
        self.prefix_parse_funcs: dict[TokenType, nuds] = {}
        self.infix_parse_funcs: dict[TokenType, leds] = {}
        # 初始化 cur_tok 和 peek_tok
        self.next_token()
        self.next_token()
        # 注册表达式解析函数
        self.register_prefix(TokenType.IDENT, self.parse_identifier)
        self.register_prefix(TokenType.INT, self.parse_integer)
        self.register_prefix(TokenType.MINUS, self.parse_prefix_expression)
        self.register_prefix(TokenType.BANG, self.parse_prefix_expression)
        self.register_infix(TokenType.PLUS, self.parse_infix_expression)
        self.register_infix(TokenType.MINUS, self.parse_infix_expression)
        self.register_infix(TokenType.SLASH, self.parse_infix_expression)
        self.register_infix(TokenType.ASTERISK, self.parse_infix_expression)
        self.register_infix(TokenType.EQ, self.parse_infix_expression)
        self.register_infix(TokenType.NOT_EQ, self.parse_infix_expression)
        self.register_infix(TokenType.LT, self.parse_infix_expression)
        self.register_infix(TokenType.GT, self.parse_infix_expression)


    def register_prefix(
            self,
            tt: TokenType,
            fn: nuds
        ) -> None:
        """为指定 token 注册对应的前缀解析方法"""
        self.prefix_parse_funcs[tt] = fn
    

    def register_infix(
            self,
            tt: TokenType,
            fn: leds
        ) -> None:
        """为指定 token 注册对应的中缀解析方法"""
        self.infix_parse_funcs[tt] = fn


    def peekError(self, expected_token_type: TokenType) -> None:
        msg = f"expected next token to be {expected_token_type}, got {self.peek_tok.type} instead"
        self.errors.append(msg)
    

    def noPrefixParseFnError(self, tt: TokenType) -> None:
        msg = f"no prefix parse function for {tt.value} found"
        self.errors.append(msg)


    def next_token(self) -> None:
        """向前读取一个 token"""
        self.cur_tok = self.peek_tok
        self.peek_tok = self.lexer.next_token()
    

    def expect_peek(self, tt: TokenType) -> bool:
        """断言后一个 token 的类型, 断言成功会自动调用 next_token"""
        if self.peek_tok.type != tt:
            self.peekError(tt)
            return False
        self.next_token()
        return True


    def get_current_precedence(self) -> ExpLevel:
        """获取当前符号的优先级"""
        return token_level.get(self.cur_tok.type, ExpLevel.LOWEST)


    def get_peek_precedence(self) -> ExpLevel:
        """窥视下一个符号的优先级"""
        return token_level.get(self.peek_tok.type, ExpLevel.LOWEST)


    def parse_program(self) -> ast.Program:
        """parser 的核心, 使用递归下降生成一棵以 Program 为根节点的 AST"""
        program = ast.Program([])
        
        while self.cur_tok.type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                program.statements.append(stmt)
            self.next_token()
        
        return program
    
    
    def parse_statement(self) -> ast.Statement:
        """解析语句节点"""
        match self.cur_tok.type:
            case TokenType.LET:
                return self.parse_let_statement()
            case TokenType.RETURN:
                return self.parse_return_statement()
            case _:
                return self.parse_expression_statement()
    

    def parse_expression_statement(self) -> ast.ExpressionStatement:
        """解析 表达式语句 节点"""
        stmt_token = self.cur_tok
        stmt_expression = self.parse_expression(ExpLevel.LOWEST)

        if self.peek_tok.type == TokenType.SEMICOLON:
            self.next_token()

        return ast.ExpressionStatement(stmt_token, stmt_expression)


    def parse_expression(self, level: ExpLevel) -> ast.Expression:
        """解析 表达式 节点"""
        prefix = self.prefix_parse_funcs.get(self.cur_tok.type)
        if not prefix:
            self.noPrefixParseFnError(self.cur_tok.type)
            return None
        leftExp = prefix()

        while (
            self.peek_tok.type != TokenType.SEMICOLON
            and level < self.get_peek_precedence()
            ):
            infix = self.infix_parse_funcs.get(self.peek_tok.type)
            if not infix:
                return leftExp
            self.next_token()
            leftExp = infix(leftExp)

        return leftExp


    def parse_let_statement(self) -> ast.LetStatement:
        """解析 LET 语句节点"""
        stmt_token = self.cur_tok

        if not self.expect_peek(TokenType.IDENT):
            return None
        
        stmt_name = ast.Identifier(
            token=self.cur_tok,
            value=self.cur_tok.literal
        )

        if not self.expect_peek(TokenType.ASSIGN):
            return None

        # TODO: 跳过对表达式的处理, 直到遇见分号
        while self.cur_tok.type != TokenType.SEMICOLON:
            self.next_token()

        stmt_value = None
        return ast.LetStatement(stmt_token, stmt_name, stmt_value)
    

    def parse_return_statement(self) -> ast.ReturnStatement:
        """解析 RETURN 语句节点"""
        stmt_token = self.cur_tok

        self.next_token()

        # TODO: 跳过对表达式的处理, 直到遇见分号
        while self.cur_tok.type != TokenType.SEMICOLON:
            self.next_token()

        stmt_return_value = None
        return ast.ReturnStatement(stmt_token, stmt_return_value)


    def parse_identifier(self) -> ast.Expression:
        """解析标识符节点"""
        return ast.Identifier(self.cur_tok, self.cur_tok.literal)
    

    def parse_integer(self) -> ast.Expression:
        """解析整型字面量节点"""
        exp_token = self.cur_tok
        try:
            exp_value = int(self.cur_tok.literal)
        except Exception as e:
            msg = f"could not parse {self.cur_tok.literal} as integer"
            self.errors.append(msg)
            return None
        
        return ast.IntegerLiteral(exp_token, exp_value)


    def parse_prefix_expression(self) -> ast.Expression:
        """解析前缀表达式节点"""
        exp_token = self.cur_tok
        exp_operator = self.cur_tok.literal

        self.next_token()

        exp_right = self.parse_expression(ExpLevel.PREFIX)

        return ast.PrefixExpression(exp_token, exp_operator, exp_right)


    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression:
        """解析中缀表达式节点"""
        exp_token = self.cur_tok
        exp_operator = self.cur_tok.literal
        exp_left = left

        level = self.get_current_precedence()
        self.next_token()
        exp_right = self.parse_expression(level)

        return ast.InfixExpression(
            token=exp_token,
            operator=exp_operator,
            left=exp_left,
            right=exp_right
        )
