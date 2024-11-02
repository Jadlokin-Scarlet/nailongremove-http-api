import asyncio
import io
from asyncio import Semaphore
from typing import Any, Awaitable, Callable, Iterable, Iterator, TypeVar

import cv2
import numpy as np
from PIL import Image as PilImage

from config import config
from model import CheckResultTuple, check_image

T = TypeVar("T")


def transform_image(image_data: bytes) -> Iterator[np.ndarray]:
    image = PilImage.open(io.BytesIO(image_data))
    image = image.convert("RGB")

    def process_frame(index: int = 0) -> np.ndarray:
        image.seek(index)
        image_array = np.array(image)
        # 转换为BGR格式
        if len(image_array.shape) == 3 and image_array.shape[2] == 3:
            image_array = cv2.cvtColor(image_array, cv2.COLOR_RGB2BGR)
        return image_array

    frame_num: int = getattr(image, "n_frames", 1)
    yield from (process_frame(i) for i in range(frame_num))


async def check_frames(frames: Iterator[np.ndarray]) -> CheckResultTuple:
    async def worker() -> CheckResultTuple:
        while True:
            try:
                frame = next(frames)
            except StopIteration:
                return False, None
            res = await check_image(frame)
            if not isinstance(res, tuple):
                res = res, None
            if res[0]:
                return res

    tasks = [asyncio.create_task(worker()) for _ in range(config.nailong_concurrency)]
    while True:
        if not tasks:
            break
        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for t in done:
            if (res := t.result())[0]:
                for pt in pending:
                    pt.cancel()
                return res
        tasks = pending

    return False, None
