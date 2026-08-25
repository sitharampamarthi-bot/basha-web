from __future__ import annotations

import ast
import math
import operator
import re
from typing import Any


BINARY_OPERATORS = {
    ast.Add:
        operator.add,

    ast.Sub:
        operator.sub,

    ast.Mult:
        operator.mul,

    ast.Div:
        operator.truediv,

    ast.FloorDiv:
        operator.floordiv,

    ast.Mod:
        operator.mod,

    ast.Pow:
        operator.pow,
}


UNARY_OPERATORS = {
    ast.UAdd:
        operator.pos,

    ast.USub:
        operator.neg,
}


def clean_expression(
    question: str,
) -> str:

    text = str(
        question or ""
    ).strip()


    text = (
        text
        .replace(
            "×",
            "*",
        )
        .replace(
            "÷",
            "/",
        )
        .replace(
            "^",
            "**",
        )
    )


    text = re.sub(
        r"\b(?:calculate|calculator|compute|what is)\b",
        " ",
        text,
        flags=re.IGNORECASE,
    )


    text = (
        text
        .replace(
            "క్యాలిక్యులేట్",
            " ",
        )
        .replace(
            "లెక్క",
            " ",
        )
    )


    text = re.sub(
        r"[^0-9+\-*/().%\s]",
        " ",
        text,
    )


    return re.sub(
        r"\s+",
        "",
        text,
    )


def evaluate_node(
    node,
):

    if isinstance(
        node,
        ast.Expression,
    ):
        return evaluate_node(
            node.body
        )


    if (
        isinstance(
            node,
            ast.Constant,
        )
        and
        isinstance(
            node.value,
            (int, float),
        )
    ):
        return node.value


    if (
        isinstance(
            node,
            ast.BinOp,
        )
        and
        type(node.op)
        in BINARY_OPERATORS
    ):

        left = evaluate_node(
            node.left
        )

        right = evaluate_node(
            node.right
        )


        if (
            isinstance(
                node.op,
                ast.Pow,
            )
            and
            abs(right) > 12
        ):
            raise ValueError(
                "Exponent is too large."
            )


        return BINARY_OPERATORS[
            type(node.op)
        ](
            left,
            right,
        )


    if (
        isinstance(
            node,
            ast.UnaryOp,
        )
        and
        type(node.op)
        in UNARY_OPERATORS
    ):

        return UNARY_OPERATORS[
            type(node.op)
        ](
            evaluate_node(
                node.operand
            )
        )


    raise ValueError(
        "Unsupported calculation."
    )


def calculate(
    question: str,
) -> dict[str, Any]:

    expression = clean_expression(
        question
    )


    if not expression:

        return {
            "success": False,
            "error": (
                "Please provide "
                "a calculation."
            ),
        }


    if len(expression) > 200:

        return {
            "success": False,
            "error": (
                "Calculation is too long."
            ),
        }


    try:

        tree = ast.parse(
            expression,
            mode="eval",
        )


        result = evaluate_node(
            tree
        )


        if isinstance(
            result,
            float,
        ):

            if not math.isfinite(
                result
            ):
                raise ValueError(
                    "Result is not finite."
                )


            result = round(
                result,
                10,
            )


        return {
            "success": True,

            "expression":
                expression,

            "result":
                result,

            "source":
                "Local calculator",
        }


    except (
        SyntaxError,
        ValueError,
        ZeroDivisionError,
        OverflowError,
    ) as error:

        return {
            "success": False,
            "error": (
                "Calculation failed: "
                f"{error}"
            ),
        }