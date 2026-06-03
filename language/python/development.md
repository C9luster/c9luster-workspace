# Python 工程开发

## typing（类型注解）

`typing` 是标准库，用于为函数参数、返回值、变量添加类型注解，供 IDE 和类型检查器（mypy、pyright）使用，**默认不参与运行时逻辑**。它的价值主要在于：接口更清晰、自动补全更准确、重构更安全、在 CI 中更早暴露类型错误。

类型注解的一个重要边界是：**Python 运行时不会因为注解不匹配就自动报错**（除非你使用了 Pydantic 这类“运行时校验”框架）。因此在工程实践里通常分两层：

- **静态层**：mypy/pyright 负责“提前发现问题”（例如可能为 `None` 的分支、参数类型不一致、容器元素类型错误等）。
- **运行时层**：需要强约束的输入（配置、API 请求体、外部数据）交给运行时校验（例如 Pydantic）。

另外，注解本身也会影响 import/依赖结构：如果你需要频繁写“前向引用”（引用尚未定义的类型）或避免“仅为类型而导入”导致的循环依赖，常见做法是使用 `from __future__ import annotations`（让注解延迟求值）与 `typing.TYPE_CHECKING`（仅在类型检查时导入）。

### 常用类型

常用注解以“容器/可选值/联合类型/回调”为主。Python 3.9+ 推荐优先使用内置泛型（`list[str]`、`dict[str, int]`），更直观；旧写法（`typing.List`、`typing.Dict`）主要用于兼容较老版本或特定工具链。

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

`Optional[T]` 表示“`T` 或 `None`”，它的意义在于提醒调用方/实现方：需要处理空值分支。`Union[A, B]` 表示多种可能类型；在 Python 3.10+，也可以写成 `A | B`，更简洁。`Literal[...]` 用于把“取值范围”收窄到有限集合，适合表达枚举式参数或协议常量。

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

当你希望描述“字典形状”而不是“任意 dict”时，可以用 `TypedDict` 指定 key 与 value 的类型，让静态检查在访问缺失字段、字段类型不一致时提前报警。它主要服务于类型系统，并不会自动在运行时校验 key 是否存在或类型是否正确（需要运行时校验请用 Pydantic）。

`Protocol` 用于表达“只要具备某些方法/属性就算满足接口”的结构化类型（鸭子类型），适合解耦依赖：调用方只关心能力，不关心具体继承体系。在工程中常用来给第三方对象、回调、适配器等定义最小接口面。

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

## contextvars（ContextVar 上下文变量）

`contextvars` 是标准库（Python 3.7+），用于定义**上下文变量** `ContextVar`：它看起来像“全局变量”，但值会随着**执行上下文**隔离与传播，适合在并发/异步场景中传递“隐式参数”。

### 适用场景

- **请求级/任务级上下文**：例如 `request_id`、`trace_id`、`user_id`、灰度/实验组标记等。
- **日志与链路追踪**：把 trace 信息放在 `ContextVar` 中，日志格式化器/埋点上报可以从当前上下文读取，而不需要层层传参。
- **库/框架内部状态**：在不污染函数签名的前提下，给底层组件提供“当前上下文”的只读输入。

### 关键行为与注意点

- **隔离性**：不同线程、不同异步任务通常拥有各自的上下文；在 `asyncio` 中，任务创建时会捕获并继承当时的上下文快照。
- **设置与回滚**：`ContextVar.set()` 会返回一个 token，可用 `reset(token)` 回滚到设置前的值，便于“进入/退出某个上下文”。
- **避免误用为全局可变状态**：不要把它当作共享可变对象的容器；更推荐存放不可变值（字符串、数字、元组、轻量对象等）。
- **与 ThreadLocal 的区别**：`threading.local()` 只按线程隔离，无法天然适配异步任务切换；`ContextVar` 面向“上下文”，更适合 async/await。

---

## Pydantic（运行时校验与数据模型）

Pydantic 基于类型注解，在**运行时**做数据校验、类型转换和序列化，常用于 API 请求/响应体、配置、环境变量等“边界输入”。它通常和 `typing` 配合使用：`typing` 负责让接口在静态层更清晰（IDE/类型检查器），Pydantic 则把这些约束落到运行时，避免“外部数据不可信”导致的隐蔽错误。

### 什么时候该用 Pydantic

- **外部输入/不可信数据**：HTTP 请求体、消息队列、配置文件、环境变量、第三方 API 返回值等。
- **需要可维护的数据模型**：把一堆零散的 dict 解析/转换/校验逻辑集中到模型里，减少重复代码。
- **需要稳定的序列化协议**：对外输出 JSON / dict（字段别名、默认值处理、排除空值等）。

### 常见行为与注意点

- **会做类型转换**：例如字符串数字转 int、字符串转 bool 等（取决于字段类型与配置）。工程上要区分“强校验”还是“宽松转换”，避免把数据问题悄悄吞掉。
- **校验失败要可观测**：把 `ValidationError` 当作“输入不合法”的一类错误处理，记录关键上下文（例如来源、字段路径），而不是直接抛到最外层。
- **字段默认值陷阱**：尽量避免用可变对象（如 `[]`、`{}`）当默认值，除非你明确理解其语义；更推荐使用默认工厂或在模型层集中初始化（不同版本/配置下行为可能不同）。
- **v1 / v2 差异**：新项目优先以 v2 心智模型理解（例如 `model_dump()`、`field_validator`/`model_validator`）；如果项目混用或迁移，建议统一版本并在 CI 中锁定依赖，减少行为差异带来的线上风险。

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

校验器用于补充“仅靠字段类型/Field 约束表达不了的规则”，例如范围校验、跨字段一致性、归一化（trim、大小写处理）、兼容多种输入格式等。

- **field_validator**：聚焦单个字段（或多个指定字段）的校验/转换，适合做范围判断、格式规范化等。通常约定“输入是什么就输出什么类型”，避免在校验器里做过度的业务逻辑。
- **model_validator**：聚焦整个模型，适合做**跨字段**校验（例如 `start_time < end_time`、二选一字段、字段组合约束）。当规则依赖多个字段时优先用它，避免把逻辑拆散到多个字段校验器里导致顺序/可读性问题。

工程实践建议：

- **错误信息要面向使用者**：抛出的 `ValueError`/`TypeError` 信息尽量可读，方便定位字段与原因；上层捕获 `ValidationError` 时再统一打日志/返回 4xx。
- **保持幂等与可预测**：校验器适合做“纯函数式”的校验/归一化，避免读写外部状态，否则调试会变困难。
- **注意版本差异**：Pydantic v2 推荐 `field_validator`/`model_validator`；旧项目 v1 常见的是 `@validator`/`@root_validator`，迁移时要统一写法与依赖版本。

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

`BaseSettings` 用来把“配置来源”标准化：将**环境变量/配置文件**等输入解析为强类型对象，并把默认值、缺省策略、校验规则集中管理。它非常适合 12-Factor 应用的配置方式（配置与代码分离）。

常见约定与注意点：

- **来源与优先级**：通常以“显式传参 / 环境变量 / 默认值”为主（具体优先级可通过配置或自定义 sources 调整）。建议在项目里固定一套策略，并在 README/部署脚本里说明。
- **命名与前缀**：通过 `env_prefix` 把同一服务的变量聚合在一起（如 `APP_`），避免与系统变量/其它服务冲突。
- **类型转换**：会把字符串环境变量转换成目标类型（如 `int`、`bool`）。布尔值等容易产生歧义，建议在团队内约定允许的取值（如 `true/false/1/0`）并在校验失败时快速暴露。
- **不要把密钥写进代码**：密钥/令牌/数据库密码等应来自环境变量或密钥管理系统；如需本地开发，可配合 `.env` 文件与部署侧注入，但要确保不提交到仓库。

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False

    model_config = {"env_prefix": "APP_"}  # 从 APP_HOST、APP_PORT 等读取

settings = Settings()
```
