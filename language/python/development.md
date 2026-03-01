# Python 工程开发

## typing（类型注解）

`typing` 是标准库，用于为函数参数、返回值、变量添加类型注解，供 IDE 和类型检查器（mypy、pyright）使用，**不参与运行时逻辑**。能提升可读性、重构安全性和补全体验。

### 常用类型

```python
from typing import Optional, Union, List, Dict, Callable, Any

def find_user(id: int) -> Optional[str]:
    ...

# 容器：list[str]、dict[str, int]（Python 3.9+ 可直接用内置泛型）
def merge(items: list[str], mapping: dict[str, int]) -> None:
    ...

# 多类型之一
def parse(value: Union[int, str]) -> int:
    ...

# 回调类型
def on_done(callback: Callable[[str], None]) -> None:
    ...
```

### Optional、Union、Literal

```python
from typing import Optional, Union, Literal

# 可 None，等价于 Union[T, None] 或 T | None
def get_name() -> Optional[str]:
    return None

# 字面量联合，常用于枚举式参数
def set_status(s: Literal["ok", "fail"]) -> None:
    ...
```

### TypedDict、Protocol

```python
from typing import TypedDict, Protocol

class Point(TypedDict):
    x: int
    y: int

# 结构化子类型（鸭子类型），不依赖继承
class Reader(Protocol):
    def read(self) -> str: ...
```

### 建议

- 优先给公共 API、入参出参写类型；内部实现可逐步补全。
- 配合 mypy 或 pyright 在 CI 中跑类型检查。
- 少用 `Any`，会削弱检查效果。

---

## Pydantic（运行时校验与数据模型）

Pydantic 基于类型注解，在**运行时**做数据校验、类型转换和序列化，常用于 API 请求/响应体、配置、环境变量。

### BaseModel 基本用法

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1)
    tags: list[str] = []

# 自动校验 + 类型转换（如 "123" -> 123）
user = User(id="123", name="alice")
user.model_dump()        # 转 dict
user.model_dump_json()   # 转 JSON 字符串
```

### Field 常用参数

```python
from pydantic import BaseModel, Field

class Item(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    count: int = Field(default=0, ge=0)
    desc: str | None = Field(default=None, description="说明")
```

### 校验器：field_validator / model_validator

```python
from pydantic import BaseModel, field_validator

class Config(BaseModel):
    port: int

    @field_validator("port")
    @classmethod
    def port_range(cls, v: int) -> int:
        if not 1 <= v <= 65535:
            raise ValueError("port must be 1-65535")
        return v
```

### BaseSettings（配置 / 环境变量）

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

    model_config = {"env_prefix": "APP_"}  # 从 APP_HOST、APP_PORT 等读取

settings = Settings()
```
