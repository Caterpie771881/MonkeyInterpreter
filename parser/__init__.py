import parser.ast as ast
from lexer import Lexer
from lexer.token import Token
from lexer.token import TokenType
from lexer.token import Position
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
    INDEX_VISIT = 7 # array[idx] or X->Y


token_level: dict[TokenType, ExpLevel] = {
    TokenType.EQ:       ExpLevel.EQUALS,
    TokenType.NOT_EQ:   ExpLevel.EQUALS,
    TokenType.LT:       ExpLevel.LESSGREATER,
    TokenType.GT:       ExpLevel.LESSGREATER,
    TokenType.PLUS:     ExpLevel.SUM,
    TokenType.MINUS:    ExpLevel.SUM,
    TokenType.SLASH:    ExpLevel.PRODUCT,
    TokenType.ASTERISK: ExpLevel.PRODUCT,
    TokenType.LPAREN:   ExpLevel.CALL,
    TokenType.LBRACKET: ExpLevel.INDEX_VISIT,
    TokenType.VISIT:    ExpLevel.INDEX_VISIT,
}
"""符号的优先级表"""


nuds = Callable[[], ast.Expression]
"""前缀解析函数规范"""
leds = Callable[[ast.Expression], ast.Expression]
"""中缀解析函数规范"""


class ParserError():
    """parser 解析过程中发生的错误"""
    def __init__(
            self,
            pos: Position,
            msg: str = 'unknown error'
        ):
        self.pos = pos
        self.msg = msg
    
    def __str__(self) -> str:
        return self.msg


class Parser():
    """语法分析器"""
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.cur_tok: Token = Token(TokenType.EOF, '')
        self.peek_tok: Token = Token(TokenType.EOF, '')
        self.errors: list[ParserError] = []
        self.prefix_parse_funcs: dict[TokenType, nuds] = {}
        self.infix_parse_funcs: dict[TokenType, leds] = {}
        # 初始化 cur_tok 和 peek_tok
        self.next_token()
        self.next_token()
        # 注册表达式解析函数
        # nuds
        self.register_nuds(TokenType.IDENT,     self.parse_identifier)
        self.register_nuds(TokenType.INT,       self.parse_integer)
        self.register_nuds(TokenType.MINUS,     self.parse_prefix_expression)
        self.register_nuds(TokenType.BANG,      self.parse_prefix_expression)
        self.register_nuds(TokenType.TRUE,      self.parse_boolean)
        self.register_nuds(TokenType.FALSE,     self.parse_boolean)
        self.register_nuds(TokenType.IF,        self.parse_if_expression)
        self.register_nuds(TokenType.LPAREN,    self.parse_grouped_expression)
        self.register_nuds(TokenType.FUNCTION,  self.parse_func_literal)
        self.register_nuds(TokenType.STRING,    self.parse_string)
        self.register_nuds(TokenType.LBRACKET,  self.parse_array)
        self.register_nuds(TokenType.LBRACE,    self.parse_hash_expression)
        self.register_nuds(TokenType.NULL,      self.parse_null)
        # leds
        self.register_leds(TokenType.PLUS,      self.parse_infix_expression)
        self.register_leds(TokenType.MINUS,     self.parse_infix_expression)
        self.register_leds(TokenType.SLASH,     self.parse_infix_expression)
        self.register_leds(TokenType.ASTERISK,  self.parse_infix_expression)
        self.register_leds(TokenType.EQ,        self.parse_infix_expression)
        self.register_leds(TokenType.NOT_EQ,    self.parse_infix_expression)
        self.register_leds(TokenType.LT,        self.parse_infix_expression)
        self.register_leds(TokenType.GT,        self.parse_infix_expression)
        self.register_leds(TokenType.LPAREN,    self.parse_call_expression)
        self.register_leds(TokenType.LBRACKET,  self.parse_index_expression)
        self.register_leds(TokenType.VISIT,     self.parse_visit_expression)


    def register_nuds(self, tt: TokenType, fn: nuds) -> None:
        """为指定 token 注册对应的前缀解析方法"""
        self.prefix_parse_funcs[tt] = fn
    

    def register_leds(self, tt: TokenType, fn: leds) -> None:
        """为指定 token 注册对应的中缀解析方法"""
        self.infix_parse_funcs[tt] = fn


    def recordError(self, msg: str) -> None:
        pos = self.cur_tok.position
        self.errors.append(ParserError(pos, msg))


    def peekError(self, expected_token_type: TokenType) -> None:
        msg = f"expected next token to be {expected_token_type}, got {self.peek_tok.type} instead"
        self.recordError(msg)
    

    def noNudsFnError(self, tt: TokenType) -> None:
        msg = f"no nuds function for {tt.value} found"
        self.recordError(msg)


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
        program = ast.Program()
        
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
            case TokenType.IMPORT:
                return self.parse_import_statement()
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
            self.noNudsFnError(self.cur_tok.type)
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

        self.next_token()

        stmt_value = self.parse_expression(ExpLevel.LOWEST)

        if self.peek_tok.type == TokenType.SEMICOLON:
            self.next_token()

        return ast.LetStatement(stmt_token, stmt_name, stmt_value)
    

    def parse_return_statement(self) -> ast.ReturnStatement:
        """解析 RETURN 语句节点"""
        stmt_token = self.cur_tok

        self.next_token()

        stmt_return_value = self.parse_expression(ExpLevel.LOWEST)

        if self.peek_tok.type == TokenType.SEMICOLON:
            self.next_token()

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
        """解析前缀运算符节点"""
        exp_token = self.cur_tok
        exp_operator = self.cur_tok.literal

        self.next_token()

        exp_right = self.parse_expression(ExpLevel.PREFIX)

        return ast.PrefixExpression(exp_token, exp_operator, exp_right)


    def parse_infix_expression(self, left: ast.Expression) -> ast.Expression:
        """解析中缀运算符节点"""
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


    def parse_boolean(self) -> ast.Expression:
        """解析布尔运算符节点"""
        exp_token = self.cur_tok

        token_type = exp_token.type
        if (
            token_type != TokenType.TRUE
            and token_type != TokenType.FALSE
        ):
            msg = f"expected current token to be TRUE or FALSE, got {token_type.name} instead"
            self.errors.append(msg)
            return None

        exp_value = token_type == TokenType.TRUE
        
        return ast.Boolean(exp_token, exp_value)
    

    def parse_grouped_expression(self) -> ast.Expression:
        """解析分组表达式"""
        self.next_token()

        exp = self.parse_expression(ExpLevel.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None
        
        return exp
    

    def parse_block_statement(self) -> ast.Statement:
        """解析块语句"""
        block = ast.BlockStatement(self.cur_tok)
        
        self.next_token()

        while (
            self.cur_tok.type != TokenType.RBRACE
            and self.cur_tok.type != TokenType.EOF
        ):
            stmt = self.parse_statement()
            if stmt:
                block.statements.append(stmt)
            self.next_token()
        
        return block


    def parse_if_expression(self) -> ast.Expression:
        """解析 IF 表达式"""
        exp = ast.IfExpression(self.cur_tok)

        if not self.expect_peek(TokenType.LPAREN):
            return None
        
        self.next_token()
        exp.condition = self.parse_expression(ExpLevel.LOWEST)

        if not self.expect_peek(TokenType.RPAREN):
            return None
        if not self.expect_peek(TokenType.LBRACE):
            return None
        
        exp.consequence = self.parse_block_statement()

        if self.peek_tok.type == TokenType.ELSE:
            self.next_token()
            if not self.expect_peek(TokenType.LBRACE):
                return None
            exp.alternative = self.parse_block_statement()

        return exp


    def parse_func_literal(self) -> ast.Expression:
        """解析函数字面量"""
        exp = ast.FunctionLiteral(self.cur_tok)

        if not self.expect_peek(TokenType.LPAREN):
            return None
        
        exp.parameters = self.parse_func_parameters()

        if not self.expect_peek(TokenType.LBRACE):
            return None
        
        exp.body = self.parse_block_statement()

        return exp
    

    def parse_expression_list(
            self,
            separator: TokenType = TokenType.COMMA,
            end: TokenType = TokenType.RPAREN
        ) -> list[ast.Expression]:
        """通用参数列表解析方法,
        separator 用于指定参数之间的分隔符,
        end 用于指定标识列表结尾的词法单元"""
        self.next_token()

        exp_list: list[ast.Expression] = []

        # 零参数
        if self.cur_tok.type == end:
            return exp_list
        # 一参数
        element = self.parse_expression(ExpLevel.LOWEST)
        exp_list.append(element)
        # 多参数
        while self.peek_tok.type == separator:
            self.next_token()
            self.next_token()
            element = self.parse_expression(ExpLevel.LOWEST)
            exp_list.append(element)

        if not self.expect_peek(end):
            return []

        return exp_list


    def parse_func_parameters(self) -> list[ast.Identifier]:
        """解析函数字面量参数"""
        parameters: list[ast.Identifier] = self.parse_expression_list()
        if not all([isinstance(p, ast.Identifier) for p in parameters]):
            self.recordError("function parameters only accept Identifier")
        return parameters


    def parse_call_expression(self, function: ast.Expression) -> ast.Expression:
        """解析调用表达式"""
        exp = ast.CallExpression(self.cur_tok, function)
        exp.arguments = self.parse_call_arguments()
        return exp
    

    def parse_call_arguments(self) -> list[ast.Expression]:
        """解析调用表达式的参数列表"""
        arguments: list[ast.Expression] = self.parse_expression_list()
        return arguments


    def parse_string(self) -> ast.Expression:
        """解析字符串字面量节点"""
        return ast.StringLiteral(self.cur_tok, self.cur_tok.literal)


    def parse_array(self) -> ast.Expression:
        """解析数组字面量"""
        exp = ast.ArrayLiteral(self.cur_tok)
        exp.elements = self.parse_expression_list(end=TokenType.RBRACKET)
        return exp


    def parse_index_expression(self, left: ast.Expression) -> ast.Expression:
        """解析取下标表达式"""
        exp = ast.IndexExpression(self.cur_tok, left)

        self.next_token()
        exp.index = self.parse_expression(ExpLevel.LOWEST)

        if not self.expect_peek(TokenType.RBRACKET):
            return None
        
        return exp


    def parse_hash_expression(self) -> ast.Expression:
        """解析哈希表表达式"""
        exp = ast.HashLiteral(self.cur_tok)
        
        while self.peek_tok.type != TokenType.RBRACE:
            self.next_token()
            key = self.parse_expression(ExpLevel.LOWEST)
            if not self.expect_peek(TokenType.COLON):
                self.recordError(f"SyntaxError: ':' expected after dictionary key")
                break
            exp.pairs.append(self.parse_pairs_expression(key))
            if (
                self.peek_tok.type != TokenType.RBRACE
                and not self.expect_peek(TokenType.COMMA)
                ):
                break
        
        if not self.expect_peek(TokenType.RBRACE):
            return None
        
        return exp


    def parse_pairs_expression(self, key: ast.Expression) -> ast.Expression:
        """解析键值对表达式"""
        exp = ast.PairsExpression(self.cur_tok, key)
        self.next_token()
        exp.value = self.parse_expression(ExpLevel.LOWEST)
        return exp


    def parse_null(self) -> ast.Expression:
        """解析空值字面量"""
        return ast.NullLiteral(self.cur_tok)


    def parse_import_statement(self) -> ast.ImportStatement:
        """解析导入语句节点"""
        stmt = ast.ImportStatement(self.cur_tok)

        if not self.expect_peek(TokenType.IDENT):
            return None
        
        stmt.module = self.cur_tok.literal

        if self.peek_tok.type == TokenType.SEMICOLON:
            self.next_token()

        return stmt


    def parse_visit_expression(self, left: ast.Expression) -> ast.Expression:
        """解析属性访问表达式"""
        exp = ast.VisitExpression(self.cur_tok)
        exp.left = left
        exp.operator = self.cur_tok.literal

        level = self.get_current_precedence()
        self.next_token()
        right = self.parse_expression(level)

        if not isinstance(right, ast.Identifier):
            self.recordError(f"expect Identifier, but {right.__class__}")
            return None
        exp.right = right

        return exp
