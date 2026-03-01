from re import S
from sqlalchemy import create_engine  # echo=True 打印 SQL

from sqlalchemy import String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

from datetime import datetime, timezone, timedelta

# 东八区 = UTC+8
TZ_UTC_PLUS_8 = timezone(timedelta(hours=8))

class Base(DeclarativeBase):
    """
    数据库的基础表接口
    """
    def to_dict(self):
        """
        将模型内容转为字典
        """
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now(TZ_UTC_PLUS_8))

    # 关系：一个用户有多篇文章
    posts: Mapped[list["Post"]] = relationship(back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(200))
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    author: Mapped["User"] = relationship(back_populates="posts")


# 创建 Session

def get_session(engine):
    SQLSession = sessionmaker(
        bind=engine,
        autocommit=False,
        autoflush=False,
    )
    return SQLSession

def main():
    # SQLite（文件数据库，适合学习）
    engine = create_engine("sqlite:///./app.db", echo=True)
    Base.metadata.create_all(engine)

    sql_session = get_session(engine)
    with sql_session() as session:
        # 增加
        for i in range(3):
            user = User(name=f"test-{i}", email=f"test-{i}@example.com")
            session.add(user)
            session.commit()
            print(f"add user {user.id}")
        
        # 批量增加
        session.add_all([
            User(name="test-3", email="test-3@example.com"),
            User(name="test-4", email="test-4@example.com"),
        ])
        session.commit()
        # INSERT 风格
        from sqlalchemy import insert
        stmt = insert(User).values(
            name="test-5",
            email="test-5@example.com"
        )
        session.execute(stmt)
        session.commit()
        print(f"add user {user.id}")

        # 查询
        # 按主键查
        user = session.get(User, 1)
        print(f"user: {user.name}")
        # 查全部
        users = session.query(User).all()
        # 条件过滤
        user = session.query(User).filter(User.email == "test-1@example.com").first()
        users = session.query(User).filter(User.name.like("%test%")).all()
        for user in users:
            print(f"query - user: {user.name}")
        # 2.0 风格：select
        from sqlalchemy import select
        stmt = select(User).where(User.id > 1).limit(2)
        users = session.scalars(stmt).all()
        for i in range(len(users)):
            print(f"selsct - user: {users[i].name}")

        # 更新
        # UPDATE 风格
        from sqlalchemy import update
        stmt = update(User).where(User.id == 1).values(
            name="test-6",
            email="test-6@example.com"
        )
        session.execute(stmt)
        session.commit()
        user = session.get(User, 1)
        print(f"UPDATE user: {user.name}")
        # 直接更新风格
        user = session.get(User, 1)
        if user:
            user.name = "张三丰"
            user.email = "zhangsanfeng@example.com"
            session.commit()
        user = session.get(User, 1)
        print(f"Direct UPDATE user: {user.name}")
        
        # 计数
        print(f"COUNT users: {session.query(User).count()}")

        # 删除 
        for i in range(1, 10):
            user = session.get(User, i)
            if user:
                session.delete(user)
                session.commit()
            
        users = session.query(User).all()
        assert len(users) == 0
        print(f"DELETE users length: {len(users)}")

        Base.metadata.drop_all(engine)

if __name__ == "__main__":
    main()