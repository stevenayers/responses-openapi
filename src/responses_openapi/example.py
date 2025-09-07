from typing import Optional


def say_hello(name: Optional[str]) -> str:
    """
    Says hello
    :param name: Name to greet
    :type name: str | None
    :return: greeting
    :rtype: str
    """
    return f"Hello, {name}!"
