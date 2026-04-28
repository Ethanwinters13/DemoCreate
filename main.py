"""
DemoCreate - Simple Python Application
"""

def hello_world():
    """Print hello world message"""
    print("🚀 Welcome to DemoCreate!")
    print("This is a demo project for GitHub integration.")

def greet(name):
    """Greet a person by name"""
    return f"Hello, {name}! 👋"

def add(a, b):
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    hello_world()
    print()
    print(greet("Developer"))
    print(f"2 + 3 = {add(2, 3)}")
