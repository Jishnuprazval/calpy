from flask import Flask, render_template, request, jsonify
import math
import re

app = Flask(__name__)


def safe_evaluate(expression: str) -> str:
    """Safely evaluate a mathematical expression."""
    # Replace display symbols with Python operators
    expression = expression.replace("×", "*").replace("÷", "/").replace("^", "**")

    # Implicit multiplication: insert * between digit/) and (
    # e.g. 77(7) → 77*(7),  (2+3)(4) → (2+3)*(4)
    expression = re.sub(r'(\d|\))\(', r'\1*(', expression)

    # Whitelist: only allow digits, operators, parentheses, dots, spaces
    allowed_chars = set("0123456789+-*/.() ")
    if not all(c in allowed_chars for c in expression):
        raise ValueError("Invalid characters in expression")

    # Guard against empty expression
    if not expression.strip():
        raise ValueError("Empty expression")

    result = eval(expression, {"__builtins__": {}}, {})  # noqa: S307

    # Format: drop unnecessary trailing zeros on floats
    if isinstance(result, float):
        if result == int(result) and not math.isinf(result):
            return str(int(result))
        return f"{result:.10g}"
    return str(result)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/calculate", methods=["POST"])
def calculate():
    data = request.get_json()
    expression = data.get("expression", "")
    try:
        result = safe_evaluate(expression)
        return jsonify({"result": result, "error": None})
    except ZeroDivisionError:
        return jsonify({"result": None, "error": "Cannot divide by zero"})
    except Exception:
        return jsonify({"result": None, "error": "Syntax Error"})


if __name__ == "__main__":
    print("  Calculator running at: http://127.0.0.1:5000")
    app.run(debug=True)
