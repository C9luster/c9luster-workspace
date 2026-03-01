# SQLAlchemy + ORM 学习使用文档

## 一、简介

**SQLAlchemy** 是 Python 中最流行的 SQL 工具包和 ORM（Object-Relational Mapping，对象关系映射）库。ORM 让你用 Python 类和对象来操作数据库，而不必手写 SQL。

- **Core**：底层 SQL 抽象层，可写原生 SQL 或使用表达式 API
- **ORM**：在 Core 之上的高级抽象，用类/对象表示表和关系

本文档主要介绍 **SQLAlchemy 2.0 风格** 的 ORM 用法。

---

## 二、安装

```bash
pip install sqlalchemy
```

如需连接具体数据库，还需安装对应驱动，例如：

```bash
# SQLite（Python 内置，无需额外安装）
# 无需额外包

# PostgreSQL
pip install psycopg2-binary

# MySQL
pip install pymysql
```

---

## 三、核心概念

| 概念 | 说明 |
|------|------|
| **Engine** | 数据库连接引擎，管理连接池 |
| **Session** | 会话，用于事务和所有 ORM 的增删改查 |
| **Model / Mapped** | 用类定义的数据库表（ORM 模型） |
| **Base** | 声明式基类，所有模型继承它 |

---

## 四、连接数据库与创建引擎

```python
from sqlalchemy import create_engine

# SQLite（文件数据库，适合学习）
engine = create_engine("sqlite:///./app.db", echo=True)  # echo=True 打印 SQL

# PostgreSQL
# engine = create_engine("postgresql://user:pass@localhost:5432/mydb")

# MySQL
# engine = create_engine("mysql+pymysql://user:pass@localhost:3306/mydb")
```

---

## 五、声明式模型（ORM 表定义）

使用 **Declarative Base** 定义表结构，每个类对应一张表，类属性对应列。列通过 **`mapped_column()`** 定义：它把 Python 类型（配合 `Mapped[]`）和数据库列类型、约束绑定在一起，是 SQLAlchemy 2.0 推荐的列声明方式。



```python
from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    # 关系：一个用户有多篇文章
    posts: Mapped[list["Post"]] = relationship(back_populates="author")

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")
```

### mapped_column 说明

- **作用**：在声明式模型中声明一列，等价于旧版的 `Column()`，同时支持类型注解（`Mapped[类型]`）。
- **常见用法**：`mapped_column(类型, 约束...)`，例如 `mapped_column(String(50), nullable=False)`。
- **类型与约束**：第一个位置参数通常是列类型（`String`, `Integer`, `ForeignKey` 等），后面可跟 `primary_key`、`nullable`、`unique`、`default` 等关键字参数。
- **与 Mapped 搭配**：推荐写成 `name: Mapped[str] = mapped_column(String(50))`，既满足类型检查，又让 ORM 知道列类型。

### relationship 说明

- **作用**：在 ORM 中声明**表与表之间的关联**，不对应数据库列，用于在 Python 里通过属性访问关联对象（如 `user.posts`、`post.author`）。
- **`back_populates`**：成对使用，表示**双向关系**。`User.posts` 的 `back_populates="author"` 指向 `Post.author`，`Post.author` 的 `back_populates="posts"` 指向 `User.posts`，两边同步，避免重复配置。
- **常见用法**：
  - 一对多：在“一”侧用 `relationship(back_populates="多侧属性名")`，类型为 `Mapped[list["Model"]]`；在“多”侧要有外键 `ForeignKey`，并用 `relationship(back_populates="一侧属性名")`，类型为 `Mapped["Model"]`。
  - 多对多：需中间表，两侧都用 `relationship(secondary=表名, back_populates="对方属性名")`。
- **其他常用参数**：`lazy="select"`（默认懒加载）、`lazy="joined"`（预加载）、`cascade="all, delete-orphan"`（级联删除）等。

### 常用列类型

| 类型 | 说明 |
|------|------|
| `String(n)` | 定长/变长字符串 |
| `Text` | 长文本 |
| `Integer` | 整数 |
| `Float` | 浮点数 |
| `Boolean` | 布尔 |
| `DateTime` | 日期时间 |
| `Date` | 日期 |

### 常用列参数

- `primary_key=True`：主键  
- `autoincrement=True`：自增  
- `nullable=False`：非空  
- `unique=True`：唯一  
- `default=...`：默认值  

---

## 六、创建表

在应用启动时根据模型创建所有表（若不存在）：

```python
Base.metadata.create_all(engine)
```

**表已存在时**：`create_all` 只会创建**尚未存在**的表，不会删除、不会覆盖、也不会修改已有表的结构；对已存在的表相当于什么都不做，可以安全重复执行。

删除所有表（慎用）：

```python
Base.metadata.drop_all(engine)
```

---

## 七、Session 与 CRUD

所有 ORM 的增删改查都通过 **Session** 完成，用完后要 **commit** 或 **rollback**，并 **close**。

### 7.1 创建 Session

```python
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

def get_session():
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

简单用法示例：

```python
with SessionLocal() as session:
    # 在这里做 CRUD
    session.commit()
```

### 7.2 增加（Create）

```python
with SessionLocal() as session:
    user = User(name="张三", email="zhangsan@example.com")
    session.add(user)
    session.commit()
    print(user.id)  # 提交后会有 id

    # 批量添加
    session.add_all([
        User(name="李四", email="lisi@example.com"),
        User(name="王五", email="wangwu@example.com"),
    ])
    session.commit()
```

### 7.3 查询（Read）

```python
with SessionLocal() as session:
    # 按主键查
    user = session.get(User, 1)

    # 查全部
    users = session.query(User).all()

    # 条件过滤
    user = session.query(User).filter(User.email == "zhangsan@example.com").first()
    users = session.query(User).filter(User.name.like("%张%")).all()

    # 2.0 风格：select
    from sqlalchemy import select
    stmt = select(User).where(User.id > 1).limit(2)
    users = session.scalars(stmt).all()
```

### 7.4 更新（Update）

```python
with SessionLocal() as session:
    user = session.get(User, 1)
    if user:
        user.name = "张三丰"
        user.email = "zhangsanfeng@example.com"
        session.commit()
```

### 7.5 删除（Delete）

```python
with SessionLocal() as session:
    user = session.get(User, 1)
    if user:
        session.delete(user)
        session.commit()
```

---

## 八、常用查询 API

```python
# filter / where
session.query(User).filter(User.id == 1).first()
session.query(User).where(User.id == 1).first()

# 多条件
session.query(User).filter(User.id > 1, User.name.like("%张%")).all()

# order_by
session.query(User).order_by(User.created_at.desc()).all()
session.query(User).order_by(User.created_at.asc()).all()

# limit / offset
session.query(User).limit(10).offset(0).all()

# count
session.query(User).count()

# 2.0 风格 select
from sqlalchemy import select
stmt = select(User).where(User.id > 0).order_by(User.id).limit(10)
session.scalars(stmt).all()
```

---

## 九、关系（Relationship）

### 9.1 一对多（One-to-Many）

上面 `User` 与 `Post` 即为一对多：一个用户多篇文章。

```python
# User 侧
posts: Mapped[list["Post"]] = relationship(back_populates="author")

# Post 侧
author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
author: Mapped["User"] = relationship(back_populates="posts")
```

使用：

```python
user = session.get(User, 1)
for post in user.posts:
    print(post.title)

post = session.get(Post, 1)
print(post.author.name)
```

### 9.2 多对多（Many-to-Many）

需要一张**关联表**（只存两个外键）：

```python
from sqlalchemy import Table, Column

# 关联表（不建 ORM 类也可以）
tag_post = Table(
    "tag_post",
    Base.metadata,
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))

    posts: Mapped[list["Post"]] = relationship(
        secondary=tag_post,
        back_populates="tags"
    )

# 在 Post 中
tags: Mapped[list["Tag"]] = relationship(
    secondary=tag_post,
    back_populates="posts"
)
```

---

## 十、完整示例（SQLite + 增删改查）

```python
from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))

engine = create_engine("sqlite:///./demo.db", echo=True)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

with Session() as s:
    s.add(User(name="Alice", email="alice@example.com"))
    s.commit()

with Session() as s:
    for u in s.query(User).all():
        print(u.id, u.name, u.email)
```

---

## 十一、最佳实践小结

1. **Session 作用域**：一个请求/一个业务单元用一个 Session，用完后 commit/rollback 并 close。  
2. **不要长期持有 Session**：避免跨请求或跨线程复用。  
3. **关系用 `relationship`**：方便懒加载/预加载，代码更清晰。  
4. **2.0 风格**：优先用 `select(Model).where(...)` + `session.scalars(stmt).all()`。  
5. **生产环境**：关闭 `echo`，用连接池；根据数据库选合适驱动（如 PostgreSQL 用 `asyncpg` 做异步）。  