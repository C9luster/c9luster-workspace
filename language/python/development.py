from __future__ import annotations

import os
import asyncio
from contextvars import ContextVar
from pydantic_settings import BaseSettings
from pydantic import Field


request_id_var: ContextVar[str] = ContextVar("request_id", default="-")



def log(msg: str) -> None:
    print(f"[request_id={request_id_var.get()}] {msg}")


def demo_sync_token_reset() -> None:
    log("sync: before set")
    token = request_id_var.set("req-1001")
    try:
        log("sync: inside context")
        token2 = request_id_var.set("req-1001/nested")
        try:
            log("sync: nested context")
        finally:
            request_id_var.reset(token2)
        log("sync: after nested reset")
    finally:
        request_id_var.reset(token)
    log("sync: after reset")


async def worker(name: str, delay_s: float) -> None:
    log(f"async worker {name}: start")
    await asyncio.sleep(delay_s)
    log(f"async worker {name}: after sleep")


async def demo_async_task_inheritance() -> None:
    token = request_id_var.set("req-2001") # worker A 记录req-2001的快照
    try:
        t1 = asyncio.create_task(worker("A", 0.05))
        token2 = request_id_var.set("req-2001/override") # worker B 记录req-2001/override的快照
        try:
            t2 = asyncio.create_task(worker("B", 0.01))
        finally:
            request_id_var.reset(token2)
        await asyncio.gather(t1, t2)
    finally:
        request_id_var.reset(token)

os.environ["APP_HOST"] = "127.0.0.1"
os.environ["APP_PORT"] = "8000"
os.environ["APP_DEBUG"] = "False"

class Settings(BaseSettings):
    host: str = Field(default="")
    port: int = Field(default=0)
    debug: bool = Field(default=True)

    model_config = {"env_prefix": "APP_"}  # 从 APP_HOST、APP_PORT 等读取

settings = Settings()


def main() -> None:

    demo_sync_token_reset()
    asyncio.run(demo_async_task_inheritance())
    print(settings.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
