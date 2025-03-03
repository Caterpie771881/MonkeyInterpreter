from abc import ABC, abstractmethod
from lexer.token import Token
from lexer.token import Position


class Node(ABC):
    """语法树节点抽象类"""
    @abstractmethod
    def TokenLiteral(self) -> str:
        """返回与其关联的词法单元的字面量"""
    
    @abstractmethod
    def tostring(self) -> str:
        """返回 AST 节点的具体信息, 我不想覆写 __str__, 所以新建了一个 tostring 方法"""
    
    @abstractmethod
    def TokenPos(self) -> Position:
        """AST 节点对应词法单元的位置信息"""


class Statement(Node):
    """语句抽象类"""


class Expression(Node):
    """表达式抽象类"""


class Program(Node):
    """AST 根节点"""
    def __init__(self, statements: list[Statement] = None):
        if statements:
            self.statements = statements
        else:
            self.statements: list[Statement] = []
    
    def TokenLiteral(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].TokenLiteral()
        else:
            return ''
    
    def tostring(self) -> str:
        return ''.join([stmt.tostring() for stmt in self.statements])
    
    def TokenPos(self) -> Position:
        if len(self.statements) > 0:
            return self.statements[0].TokenPos()
        else:
            return Position(0, 0)


# ========== expression ==========

class Identifier(Expression):
    """标识符表达式节点"""
    def __init__(
            self,
            token: Token = None,
            value: str = ''
        ):
        self.token = token
        """IDENT 词法单元"""
        self.value = value
    
    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return self.value
    
    def TokenPos(self) -> Position:
        return self.token.position


class IntegerLiteral(Expression):
    """整型字面量节点"""
    def __init__(
            self,
            token: Token = None,
            value: int = -1
        ):
        self.token = token
        """INT 词法单元"""
        self.value = value

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return self.token.literal
    
    def TokenPos(self) -> Position:
        return self.token.position


class PrefixExpression(Expression):
    """前缀表达式节点"""
    def __init__(
            self,
            token: Token = None,
            operator: str = '',
            right: Expression = None
        ):
        self.token = token
        """前缀词法单元, 如 '!'"""
        self.operator = operator
        self.right = right

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return f"({self.operator}{self.right.tostring()})"
    
    def TokenPos(self) -> Position:
        return self.token.position


class InfixExpression(Expression):
    """中缀表达式节点"""
    def __init__(
            self,
            token: Token = None,
            left: Expression = None,
            operator: str = '',
            right: Expression = None
        ):
        self.token: Token = token
        """中缀词法单元, 如 '+'"""
        self.left: Expression = left
        self.operator: str = operator
        self.right: Expression = right

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return f"({self.left.tostring()} {self.operator} {self.right.tostring()})"
    
    def TokenPos(self) -> Position:
        return self.token.position


class Boolean(Expression):
    """布尔表达式节点"""
    def __init__(
            self,
            token: Token = None,
            value: bool = None
        ):
        self.token = token
        """布尔值词法单元 TRUE/FALSE"""
        self.value = value

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return self.token.literal
    
    def TokenPos(self) -> Position:
        return self.token.position


class IfExpression(Expression):
    """条件表达式节点"""
    def __init__(
            self,
            token: Token = None,
            condition: Expression = None,
            consequence: "BlockStatement" = None,
            alternative: "BlockStatement" = None
        ):
        self.token = token
        """IF 词法单元"""
        self.condition = condition
        self.consequence = consequence
        self.alternative = alternative

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self):
        condition = self.condition.tostring()
        consequence = self.consequence.tostring()
        if self.alternative:
            alternative = f" else {self.alternative.tostring()}"
        else:
            alternative = ""
        return f"if {condition} {consequence}{alternative}"
    
    def TokenPos(self) -> Position:
        return self.token.position


class FunctionLiteral(Expression):
    """函数字面量节点"""
    def __init__(
            self,
            token: Token = None,
            parameters: list[Identifier] = None,
            body: "BlockStatement" = None
        ):
        self.token = token
        """FN 词法单元"""
        if parameters:
            self.parameters = parameters
        else:
            self.parameters: list[Identifier] = []
        self.body = body
    
    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        params: list[str] = []
        for p in self.parameters:
            params.append(p.tostring())
        return f"fn({','.join(params)}) {self.body.tostring()}"
    
    def TokenPos(self) -> Position:
        return self.token.position


class CallExpression(Expression):
    """调用表达式 节点"""
    def __init__(
            self,
            token: Token = None,
            func: Expression = None,
            arguments: list[Expression] = None
        ):
        self.token = token
        """'(' 词法单元"""
        self.func = func
        if arguments:
            self.arguments = arguments
        else:
            self.arguments: list[Expression] = []
    
    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        args: list[str] = []
        for a in self.arguments:
            args.append(a.tostring())
        return f"{self.func.tostring()}({','.join(args)})"
    
    def TokenPos(self) -> Position:
        return self.token.position


# ========== statement ==========

class ExpressionStatement(Statement):
    """表达式语句节点, 用于处理仅包含表达式的语句"""
    def __init__(
            self,
            token: Token = None,
            expression: Expression = None
        ):
        self.token = token
        """表达式中的第一个词法单元"""
        self.expression = expression

    def TokenLiteral(self) -> str:
        return self.token.literal

    def tostring(self) -> str:
        if self.expression != None:
            return self.expression.tostring()
        return '[nil]'
    
    def TokenPos(self) -> Position:
        return self.token.position


class LetStatement(Statement):
    """let 语句节点"""
    def __init__(
            self,
            token: Token = None,
            name: Identifier = None,
            value: Expression = None
        ):
        self.token = token
        """LET 词法单元"""
        self.name = name
        self.value = value

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        v = '[nil]'
        if self.value != None:
            v = self.value.tostring()
        return f"{self.TokenLiteral()} {self.name.tostring()} = {v};"
    
    def TokenPos(self) -> Position:
        return self.token.position


class ReturnStatement(Statement):
    """return 语句节点"""
    def __init__(
            self,
            token: Token = None,
            return_value: Expression = None
        ):
        self.token = token
        """RETURN 词法单元"""
        self.return_value = return_value

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        v = '[nil]'
        if self.return_value != None:
            v = self.return_value.tostring()
        return f"{self.TokenLiteral()} {v};"
    
    def TokenPos(self) -> Position:
        return self.token.position


class BlockStatement(Statement):
    """块语句节点"""
    def __init__(
            self,
            token: Token = None,
            statements: list[Statement] = None
        ):
        self.token = token
        """LBRACE 词法单元"""
        if statements:
            self.statements = statements
        else:
            self.statements: list[Statement] = []

    def TokenLiteral(self) -> str:
        return self.token.literal

    def tostring(self) -> str:
        return ''.join([stmt.tostring() for stmt in self.statements])

    def TokenPos(self) -> Position:
        return self.token.position
