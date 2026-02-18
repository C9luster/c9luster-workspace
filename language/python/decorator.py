from dataclasses import dataclass 
from typing import overload
from abc import ABC, abstractmethod
import functools

@dataclass
class TestDataclass:
    name: str
    age: int


class TestClassmethod:
    @classmethod
    def create(cls):
        return cls()
    
    @classmethod
    def messsage(cls, message: str):
        return message


class TestProperty:
    def __init__(self):
        self._name = None  # 使用私有属性存储实际值
    
    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value: str):
        self._name = value

    @name.deleter
    def name(self):
        del self._name


class TestOverload:
    @overload
    def add(self, a: int, b: int) -> int:
        ...

    @overload
    def add(self, a: str, b: str) -> str:
        ...

    def add(self, a, b) -> int:
        if isinstance(a, int) and isinstance(b, int):
            return a + b
        elif isinstance(a, str) and isinstance(b, str):
            return f"{a}{b}"


class TestABC(ABC):
    # 子类必须重新实现add方法
    @abstractmethod
    def add(self, a, b) -> int:
        ...


def trace(func):
    """使用 functools.wraps 的装饰器，保持原函数的元数据"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"args: {args}, arg_len: {len(args)}")
        print(f"kwargs: {kwargs}, kwargs_len: {len(kwargs)}")
        print(f"调用函数: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@trace
def test_with_wraps(arg, kwargs):
    """使用 wraps 的测试函数"""
    return "Hello"


def test_decorator():
    # dataclass属性测试
    test_dataclass_1 = TestDataclass("John", 20)
    test_dataclass_2 = TestDataclass("John", 20)
    print(test_dataclass_1)
    print(test_dataclass_1 == test_dataclass_2)

    # classmethod 测试
    print(TestClassmethod.create)
    print(TestClassmethod.messsage("message"))
    print(TestClassmethod.messsage.__qualname__)

    # property 测试
    test_property = TestProperty()
    test_property.name = "John"
    print(f"设置后的 name: {test_property.name}")
    del test_property.name
    try:
        test_property.name
    except AttributeError as e:
        print(f"删除后访问属性会报错: {e}")

    # overload 测试
    test_overload = TestOverload()
    print(test_overload.add(1, 2))
    print(test_overload.add("1", "2"))

    # trace 测试 - 展示 functools.wraps 的作用
    print(f"\n使用 wraps 的装饰器:")
    print(f"函数名称: {test_with_wraps.__name__}")      # 显示 'test_with_wraps'
    print(f"函数文档: {test_with_wraps.__doc__}")        # 显示原函数的文档
    test_with_wraps("test", kwargs="test") 


if __name__ == "__main__":
    test_decorator()