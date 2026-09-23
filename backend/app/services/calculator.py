import ast
import operator as op
from typing import Dict, Any, Union

OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Mod: op.mod,
    ast.Pow: op.pow,
    ast.USub: op.neg,
    ast.UAdd: op.pos,
}

def eval_node(node: ast.AST) -> Union[int, float]:
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError(f"Unsupported constant type: {type(node.value)}")

    elif isinstance(node, ast.BinOp):
        left = eval_node(node.left)
        right = eval_node(node.right)
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported operator: {op_type.__name__}")
        
        if op_type == ast.Div and right == 0:
            raise ZeroDivisionError("Division by zero is undefined.")
        if op_type == ast.Mod and right == 0:
            raise ZeroDivisionError("Modulo by zero is undefined.")

        return OPERATORS[op_type](left, right)

    elif isinstance(node, ast.UnaryOp):
        operand = eval_node(node.operand)
        op_type = type(node.op)
        if op_type not in OPERATORS:
            raise ValueError(f"Unsupported unary operator: {op_type.__name__}")
        return OPERATORS[op_type](operand)

    elif isinstance(node, ast.Expr):
        return eval_node(node.value)

    else:
        raise ValueError(f"Unsupported expression component: {type(node).__name__}")


import re

def extract_and_clean_math(expression: str) -> str:
    cleaned = expression.strip()
    cleaned = cleaned.replace("$", "")

    pattern_pct_of = re.compile(r'(\d+(?:\.\d+)?)\s*%\s*(?:of|\*|\s)\s*(\d+(?:\.\d+)?)', re.IGNORECASE)
    match_pct = pattern_pct_of.search(cleaned)
    if match_pct:
        pct_val, base_val = match_pct.groups()
        return f"({pct_val} / 100) * {base_val}"

    for prefix in ["calculate", "what is", "compute", "eval", "evaluate"]:
        if cleaned.lower().startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()
            break

    for stop_kw in [" and ", ". ", ", ", ";", " explain", " showing", " then "]:
        if stop_kw in cleaned.lower():
            idx = cleaned.lower().index(stop_kw)
            cand = cleaned[:idx].strip()
            if any(char.isdigit() for char in cand):
                cleaned = cand
                break

    cleaned = cleaned.rstrip("?=").strip()
    return cleaned

def evaluate_expression(expression: str) -> Dict[str, Any]:
    cleaned = extract_and_clean_math(expression)

    if not cleaned:
        return {"success": False, "error": "Empty arithmetic expression."}

    try:
        parsed = ast.parse(cleaned, mode='eval')
        result = eval_node(parsed.body)
        
        if isinstance(result, float) and result.is_integer():
            result = int(result)
        elif isinstance(result, float):
            result = round(result, 6)

        return {
            "success": True,
            "expression": cleaned,
            "result": result,
            "formatted_result": f"{cleaned} = {result}"
        }
    except ZeroDivisionError as e:
        return {"success": False, "expression": cleaned, "error": str(e)}
    except SyntaxError:
        return {"success": False, "expression": cleaned, "error": "Invalid mathematical syntax."}
    except ValueError as e:
        return {"success": False, "expression": cleaned, "error": str(e)}
    except Exception as e:
        return {"success": False, "expression": cleaned, "error": f"Evaluation error: {str(e)}"}
