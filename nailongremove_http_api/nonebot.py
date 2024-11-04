
import asyncio
from contextvars import copy_context
from typing_extensions import ParamSpec
from collections.abc import Coroutine
from functools import wraps, partial
from typing import TypeVar, Callable
P = ParamSpec("P")
R = TypeVar("R")
T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
class Utils:
    def run_sync(call: Callable[P, R]) -> Callable[P, Coroutine[None, None, R]]:
        """一个用于包装 sync function 为 async function 的装饰器

        参数:
            call: 被装饰的同步函数
        """

        @wraps(call)
        async def _wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            loop = asyncio.get_running_loop()
            pfunc = partial(call, *args, **kwargs)
            context = copy_context()
            result = await loop.run_in_executor(None, partial(context.run, pfunc))
            return result

        return _wrapper


class Logger:
    def error(self, msg):
        print(f"error: {msg}")

    def debug(self, msg):
        print(f"debug: {msg}")

    def info(self, msg):
        print(f"info: {msg}")

logger = Logger()
utils = Utils()