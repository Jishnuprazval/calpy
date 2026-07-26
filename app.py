from flask import Flask, render_template, request, jsonify
import math
import re

app = Flask(__name__)


def safe_evaluate(expression: str) -> str:
    """Evaluate a restricted mathematical expression."""

    # Replace calculator symbols with Python operators
    expression = (
        expression
        .replace("×", "*")
        .replace("÷", "/")
        .replace("^", "**")
    )

    # Support implicit multiplication:
    # 77(7) -> 77*(7)
    # (2+3)(4) -> (2+3)*(4)
    expression = re.sub(r'(\d|\))\(', r'\1*(', expression)

    # Allow only calculator-related characters
    allowed_chars = set("0123456789+-*/.() ")

    if not all(c in allowed_chars for c in expression):
        raise ValueError("Invalid characters in expression")

    if not expression.strip():
        raise ValueError("Empty expression")

    result = eval(expression, {"__builtins__": {}}, {})

    # Format floating-point results
    if isinstance(result, float):
        if not math.isfinite(result):
            raise ValueError("Invalid result")

        if result.is_integer():
            return str(int(result))

        return f"{result:.10g}"

    return str(result)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():

    data = request.get_json(silent=True) or {}
    expression = data.get("expression", "")

    if not isinstance(expression, str):
        return jsonify({
            "result": None,
            "error": "Invalid expression"
        }), 400

    try:
        result = safe_evaluate(expression)

        return jsonify({
            "result": result,
            "error": None
        })

    except ZeroDivisionError:
        return jsonify({
            "result": None,
            "error": "Cannot divide by zero"
        })

    except (SyntaxError, ValueError, TypeError, OverflowError):
        return jsonify({
            "result": None,
            "error": "Syntax Error"
        })


if __name__ == "__main__":
    print("Calculator running at: http://127.0.0.1:5000")
    app.run()
