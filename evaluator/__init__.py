from lexer.token import Position
from parser import ast
from evaluator import objsys as obj


NULL = obj.Null()
TRUE = obj.Boolean(True)
FALSE = obj.Boolean(False)


def native_bool(v: bool):
    """根据输入条件返回 Monkey 原生布尔引用"""
    return TRUE if v else FALSE


def is_truthy(obj_: obj.MonkeyObj) -> bool:
    """Monkey 语言的真值判断, 非空非假均视为真"""
    if obj_ is NULL:
        return False
    if obj_ is FALSE:
        return False
    if obj_ is TRUE:
        return True
    return True


def is_error(obj_: obj.MonkeyObj) -> bool:
    """判断是否为 ERROR_OBJ"""
    if obj_ != None:
        return obj_.type() == obj.ObjectType.ERROR_OBJ
    return False


def unwrap(obj_: obj.MonkeyObj) -> obj.MonkeyObj:
    """解包 RETURN 对象"""
    if obj_.type() == obj.ObjectType.RETURN_VALUE_OBJ:
        return obj_.value
    return obj_


def Eval(node: ast.Node, env: obj.Environment) -> obj.MonkeyObj:
    """对所有类型的节点求值"""
    global NULL, TRUE, FALSE
    match node:
        case ast.Program():
            return eval_program(node.statements, env)
        
        case ast.BlockStatement():
            return eval_block_statement(node.statements, env)
        
        case ast.ExpressionStatement():
            return Eval(node.expression, env)
        
        case ast.IntegerLiteral():
            return obj.Integer(node.value)
        
        case ast.Boolean():
            return TRUE if node.value else FALSE
        
        case ast.PrefixExpression():
            right = Eval(node.right, env)
            if is_error(right):
                return right
            return eval_prefix_expression(
                node.operator, right, node.TokenPos())
        
        case ast.InfixExpression():
            left = Eval(node.left, env)
            if is_error(left):
                return left
            right = Eval(node.right, env)
            if is_error(right):
                return right
            return eval_infix_expression(
                left, node.operator, right, node.TokenPos())
        
        case ast.IfExpression():
            condition = Eval(node.condition, env)
            if is_error(condition):
                return condition
            if is_truthy(condition):
                return Eval(node.consequence, env)
            if node.alternative:
                return Eval(node.alternative, env)
            return NULL
        
        case ast.ReturnStatement():
            rv = Eval(node.return_value, env)
            if is_error(rv):
                return rv
            return obj.ReturnValue(rv)
        
        case ast.LetStatement():
            val = Eval(node.value, env)
            if is_error(val):
                return val
            env.set(node.name.value, val)
        
        case ast.Identifier():
            val = env.get(node.value)
            if val:
                return val
            return obj.Error(node.TokenPos(), f"identifier not found: {node.value}")
        
        case ast.FunctionLiteral():
            return obj.Function(node.parameters, node.body, env)
        
        case ast.CallExpression():
            func = Eval(node.func, env)
            if is_error(func):
                return func
            if not isinstance(func, obj.Function):
                return obj.Error(
                    node.TokenPos(),
                    f"not a function: {func.type().value} is not callable")
            args = eval_expressions(node.arguments, env)
            if len(args) == 1 and is_error(args[0]):
                return args[0]
            return apply_function(func, args)

        case _:
            return obj.Error(node.TokenPos(), f"unsupport ast node: {node.__class__}")


def eval_program(
        statements: list[ast.Statement],
        env: obj.Environment
    ) -> obj.MonkeyObj:
    """对语句求值"""
    result: obj.MonkeyObj = NULL
    for stmt in statements:
        result = Eval(stmt, env)
        match result:
            case obj.ReturnValue():
                return result.value
            case obj.Error():
                return result
    return result


def eval_block_statement(
        statements: list[ast.Statement],
        env: obj.Environment
    ) -> obj.MonkeyObj:
    """对块语句求值"""
    result: obj.MonkeyObj = NULL
    for stmt in statements:
        result = Eval(stmt, env)
        if result != None:
            rt = result.type()
            if (
                rt == obj.ObjectType.RETURN_VALUE_OBJ
                or rt == obj.ObjectType.ERROR_OBJ
                ):
                return result
    return result


# ========== prefix expression ==========

def eval_prefix_expression(
        operator: str,
        right: obj.MonkeyObj,
        pos: Position
    ) -> obj.MonkeyObj:
    """对前缀表达式求值"""
    match operator:
        case '!':
            return eval_bang(right, pos)
        case '-':
            return eval_minus_prefix(right, pos)
        case _:
            return obj.Error(pos, f"unknown operator: {operator}{right.type().value}")


def eval_bang(right: obj.MonkeyObj, pos: Position) -> obj.MonkeyObj:
    """对取反操作求值"""
    global NULL, TRUE, FALSE
    if right is TRUE:
        return FALSE
    if right is FALSE:
        return TRUE
    if right is NULL:
        return TRUE
    return FALSE


def eval_minus_prefix(right: obj.MonkeyObj, pos: Position) -> obj.MonkeyObj:
    """对 minus 前缀操作求值"""
    if right.type() != obj.ObjectType.INTEGER_OBJ:
        return obj.Error(pos, f"unknown operator: -{right.type().value}")
    if not isinstance(right, obj.Integer):
        return obj.Error(pos, f"unknown operator: -{right.type().value}")
    value = right.value
    return obj.Integer(-value)


# ========== infix expression ==========

def eval_infix_expression(
        left: obj.MonkeyObj,
        operator: str,
        right: obj.MonkeyObj,
        pos: Position
    ) -> obj.MonkeyObj:
    """对中缀表达式求值"""
    if (
        left.type() == obj.ObjectType.INTEGER_OBJ
        and right.type() == obj.ObjectType.INTEGER_OBJ
        ):
        return eval_infix_expression_for_integer(left, operator, right, pos)
    if (
        left.type() == obj.ObjectType.BOOLEAN_OBJ
        and right.type() == obj.ObjectType.BOOLEAN_OBJ
        ):
        return eval_infix_expression_for_boolean(left, operator, right, pos)
    return obj.Error(pos, f"type mismatch: {left.type().value} {operator} {right.type().value}")


def eval_infix_expression_for_integer(
        left: obj.Integer,
        operator: str,
        right: obj.Integer,
        pos: Position
    ) -> obj.MonkeyObj:
    """对整型支持的中缀表达式求值"""
    left_v = left.value
    right_v = right.value
    match operator:
        case '+':
            return obj.Integer(left_v + right_v)
        case '-':
            return obj.Integer(left_v - right_v)
        case '*':
            return obj.Integer(left_v * right_v)
        case '/':
            return obj.Integer(left_v // right_v)
        case '>':
            return native_bool(left_v > right_v)
        case '<':
            return native_bool(left_v < right_v)
        case '==':
            return native_bool(left_v == right_v)
        case '!=':
            return native_bool(left_v != right_v)
        case _:
            return obj.Error(pos, f"unknown operator: INTEGER unsupport operator '{operator}'")


def eval_infix_expression_for_boolean(
        left: obj.Boolean,
        operator: str,
        right: obj.Boolean,
        pos: Position
    ) -> obj.MonkeyObj:
    """对布尔值支持的中缀表达式求值"""
    match operator:
        case '==':
            return native_bool(left is right)
        case '!=':
            return native_bool(left is not right)
        case _:
            return obj.Error(pos, f"unknown operator: BOOLEAN unsupport operator '{operator}'")


def eval_expressions(
        exps: list[ast.Expression],
        env: obj.Environment
    ) -> list[obj.MonkeyObj]:
    """批量求值表达式, 返回一个由表达式对应结果组成的 list,
    一旦出现错误, 将返回一个仅由错误对象组成的 list"""
    result: list[obj.MonkeyObj] = []
    for e in exps:
        evaluated = Eval(e, env)
        if is_error(evaluated):
            return [evaluated]
        result.append(evaluated)
    return result


def apply_function(
        func: obj.Function,
        args: list[obj.MonkeyObj]
    ) -> obj.MonkeyObj:
    """执行函数"""
    extend_env = obj.Environment(func.env)
    for i in range(len(func.parameters)):
        param = func.parameters[i].value
        extend_env.set(param, args[i])
    evaluated = Eval(func.body, extend_env)
    return unwrap(evaluated)
