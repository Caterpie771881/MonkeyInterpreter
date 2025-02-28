from abc import ABC, abstractmethod
from lexer.token import Token


class Node(ABC):
    """语法树节点抽象类"""
    @abstractmethod
    def TokenLiteral(self) -> str:
        """返回与其关联的词法单元的字面量"""
    
    @abstractmethod
    def tostring(self) -> str:
        """返回 AST 节点的具体信息"""


class Statement(Node):
    """语句抽象类"""
    @abstractmethod
    def statementNode(self):
        """语句节点必须实现该方法"""


class Expression(Node):
    """表达式抽象类"""
    @abstractmethod
    def expressionNode(self):
        """表达式节点必须实现该方法"""


class Program(Node):
    """AST 根节点"""
    def __init__(self, statements: list[Statement]):
        self.statements = statements
    
    def TokenLiteral(self) -> str:
        if len(self.statements) > 0:
            return self.statements[0].TokenLiteral()
        else:
            return ''
    
    def tostring(self) -> str:
        return ''.join([stmt.tostring() for stmt in self.statements])


# ========== expression ==========

class Identifier(Expression):
    """标识符表达式节点"""
    def __init__(self, token: Token, value: str):
        self.token = token # IDENT 词法单元
        self.value = value

    def expressionNode(self):...
    
    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return self.value


class IntegerLiteral(Expression):
    """整型字面量节点"""
    def __init__(self, token: Token, value: int):
        self.token = token # INT 词法单元
        self.value = value
    
    def expressionNode(self):...

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return self.token.literal


class PrefixExpression(Expression):
    """前缀表达式节点"""
    def __init__(self, token: Token, operator: str, right: Expression):
        self.token = token # 前缀词法单元, 如 '!'
        self.operator = operator
        self.right = right
    
    def expressionNode(self):...

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return f"({self.operator}{self.right.tostring()})"


class InfixExpression(Expression):
    """中缀表达式节点"""
    def __init__(
            self,
            token: Token,
            left: Expression,
            operator: str,
            right: Expression
        ):
        self.token = token # 中缀词法单元, 如 '+'
        self.left = left
        self.operator = operator
        self.right = right

    def expressionNode(self):...

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        return f"({self.left.tostring()} {self.operator} {self.right.tostring()})"


# ========== statement ==========

class ExpressionStatement(Statement):
    """表达式语句节点"""
    def __init__(self, token: Token, expression: Expression):
        self.token = token # 该表达式中的第一个词法单元
        self.expression = expression

    def statementNode(self):...

    def TokenLiteral(self) -> str:
        return self.token.literal

    def tostring(self) -> str:
        if self.expression != None:
            return self.expression.tostring()
        return '[nil]'


class LetStatement(Statement):
    """let 语句节点"""
    def __init__(self, token: Token, name: Identifier, value: Expression):
        self.token = token # LET 词法单元
        self.name = name
        self.value = value
    
    def statementNode(self):...

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        v = '[nil]'
        if self.value != None:
            v = self.value.tostring()
        return f"{self.TokenLiteral()} {self.name.tostring()} = {v};"


class ReturnStatement(Statement):
    """return 语句节点"""
    def __init__(self, token: Token, return_value: Expression):
        self.token = token # RETURN 词法单元
        self.return_value = return_value
    
    def statementNode(self):...

    def TokenLiteral(self) -> str:
        return self.token.literal
    
    def tostring(self) -> str:
        v = '[nil]'
        if self.return_value != None:
            v = self.return_value.tostring()
        return f"{self.TokenLiteral()} {v};"

