from tool_tuesday.handler import handler


def start():
    print("Local Dev")
    result = handler("test", "test")
    print(result)
