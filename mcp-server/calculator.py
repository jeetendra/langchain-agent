from mcp.server.fastmcp import FastMCP

mcp = FastMCP()

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b
@mcp.tool()
def subtract_numbers(a: int, b: int) -> int:
    """Subtract two numbers."""
    return a - b
@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers."""
    return a * b
@mcp.tool()
def divide_numbers(a: int, b: int) -> float:
    """Divide two numbers."""
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b

if __name__ == "__main__":
    # Start the MCP server
    mcp.run(transport="stdio")
    print("MCP server is running...")