from langgraph.func import entrypoint, task

@task
def add(x: int, y: int) -> int:
    """Add two numbers."""
    return x + y

@task
def multiply(x: int, y: int) -> int:
    """Multiply two numbers."""
    return x * y

@entrypoint()
def calculate(l) -> dict:
    """Calculate the sum and product of two numbers."""
    x, y = l
    if not isinstance(x, int) or not isinstance(y, int):
        raise ValueError("Both inputs must be integers.")
    sum_result = add(x, y).result()
    product_result = multiply(x, y).result()
    
    return {
        "sum": sum_result,
        "product": product_result
    }

result = calculate.invoke([3, 5])
print(f"Sum: {result['sum']}, Product: {result['product']}")