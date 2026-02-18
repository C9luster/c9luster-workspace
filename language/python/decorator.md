# Python 装饰器详解

## @dataclass

`@dataclass` 是 Python 3.7+ 提供的装饰器，用于简化数据类的定义。它会自动生成 `__init__`、`__repr__`、`__eq__` 等方法，减少样板代码。使用方式：在类定义前添加 `@dataclass`，类属性会自动成为实例属性，支持类型注解和默认值。适用于创建数据容器类，让代码更简洁、可读性更好。

```python
@dataclass
class Point:
    x: int
    y: int = 0
```

## @classmethod

`@classmethod` 用于定义类方法，第一个参数是类本身（通常命名为 `cls`），而不是实例。可以通过类直接调用，无需创建实例。常用于工具方法、工厂方法或需要访问类属性的场景。与普通实例方法（`self`）不同，类方法主要操作类级别的数据。

```python
class MyClass:
    @classmethod
    def create(cls):
        return cls()
```

## @property

`@property` 将方法转换为属性，实现类似属性的访问方式。可以定义 getter、setter、deleter 来控制属性的读取、设置和删除行为。支持数据验证、计算属性等功能。使用 `@property` 可以保持 API 简洁，同时提供对数据的控制，实现封装和数据验证。

```python
class Circle:
    @property
    def area(self):
        return 3.14 * self.radius ** 2
```

## @overload

`@overload` 来自 `typing` 模块，用于声明函数重载的类型签名，仅用于类型检查，不影响运行时。必须配合实际实现使用，所有重载签名的函数体必须是 `...`。让类型检查器根据不同的参数类型推断不同的返回类型，提供更精确的类型提示和更好的 IDE 支持。

```python
@overload
def process(value: int) -> str: ...
@overload
def process(value: str) -> int: ...
def process(value):  # 实际实现
    ...
```

## @abstractmethod

`@abstractmethod` 来自 `abc` 模块，用于定义抽象方法。必须配合继承 `ABC` 的抽象基类使用。子类必须实现所有抽象方法才能实例化，否则会抛出 `TypeError`。用于强制子类实现特定接口，确保多态性和接口一致性。适用于定义框架接口、插件系统等需要强制实现的场景。

```python
from abc import ABC, abstractmethod

class Shape(ABC):
    @abstractmethod
    def area(self):
        pass
```

## @functools.wraps

`@functools.wraps` 用于在装饰器中保持原函数的元数据（如 `__name__`、`__doc__` 等）。不使用 `wraps` 时，装饰后的函数会丢失原函数的名称和文档字符串，显示为包装函数的名称。使用 `wraps` 可以确保装饰后的函数保持原函数的元数据，这对于调试、文档生成和工具链非常重要。

```python
import functools

def trace(func):
    @functools.wraps(func)  # 保持原函数的元数据
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
```

