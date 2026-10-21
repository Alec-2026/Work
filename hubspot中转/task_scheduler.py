"""Run the HubSpot email-generation workflow every five minutes."""

from __future__ import annotations

import logging
import queue
import threading
from time import monotonic

from app import run_email_generation


logger = logging.getLogger(__name__)


def _execute_scheduled_run(scheduled_number: int) -> None:
    """Execute one scheduled run without letting failures kill a worker."""

    logger.info("定时任务开始：run_number=%d", scheduled_number)
    try:
        result = run_email_generation()
        logger.info(
            "定时任务执行成功：run_number=%d, contacts=%d, generated=%d, updated=%d",
            scheduled_number,
            result["contact_count"],
            result["generated_count"],
            result["updated_count"],
        )
    except Exception:
        logger.exception("定时任务执行失败：run_number=%d", scheduled_number)


def _worker(
    task_queue: queue.Queue[int],
    stop_event: threading.Event,
) -> None:
    while not stop_event.is_set():
        try:
            scheduled_number = task_queue.get(timeout=0.1)
        except queue.Empty:
            continue
        try:
            _execute_scheduled_run(scheduled_number)
        finally:
            task_queue.task_done()


def _run_scheduler(
    interval_seconds: float,
    worker_count: int,
    stop_event: threading.Event,
) -> None:
    task_queue: queue.Queue[int] = queue.Queue()
    workers = [
        threading.Thread(
            target=_worker,
            args=(task_queue, stop_event),
            name=f"email-scheduler-worker-{index + 1}",
            daemon=True,
        )
        for index in range(worker_count)
    ]
    for worker in workers:
        worker.start()

    next_run_at = monotonic() + interval_seconds
    scheduled_number = 0
    logger.info(
        "定时调度器已启动：interval_seconds=%s, worker_count=%d, first_run_in_seconds=%s",
        interval_seconds,
        worker_count,
        interval_seconds,
    )

    while not stop_event.is_set():
        wait_seconds = max(0.0, next_run_at - monotonic())
        if stop_event.wait(wait_seconds):
            break

        now = monotonic()
        while next_run_at <= now and not stop_event.is_set():
            scheduled_number += 1
            task_queue.put(scheduled_number)
            logger.info(
                "定时任务已提交：run_number=%d, queued_tasks=%d",
                scheduled_number,
                task_queue.qsize(),
            )
            next_run_at += interval_seconds

    logger.info(
        "定时调度器已停止：scheduled_runs=%d, queued_tasks=%d",
        scheduled_number,
        task_queue.qsize(),
    )


def run_scheduler(
    interval_seconds: float = 300,
    worker_count: int = 1,
) -> None:
    """Run email generation at fixed intervals until interrupted.

    The first run is scheduled after one complete interval. Runs may execute
    concurrently up to ``worker_count``; additional runs wait in an unbounded
    queue. Press Ctrl+C to stop scheduling without waiting for active runs.
    """

    if (
        not isinstance(interval_seconds, (int, float))
        or isinstance(interval_seconds, bool)
        or interval_seconds <= 0
    ):
        raise ValueError("interval_seconds must be a positive number")
    if (
        not isinstance(worker_count, int)
        or isinstance(worker_count, bool)
        or worker_count <= 0
    ):
        raise ValueError("worker_count must be a positive integer")

    stop_event = threading.Event()
    try:
        _run_scheduler(float(interval_seconds), worker_count, stop_event)
    except KeyboardInterrupt:
        stop_event.set()
        logger.info("收到停止信号，定时调度器正在退出")
    except Exception:
        stop_event.set()
        logger.exception("定时调度器异常退出")
        raise


def main() -> None:
    run_scheduler(
        interval_seconds=600,  # 每十分钟扫描一次hubspot的数据
        worker_count=1,  # 只有一个worker
    )


if __name__ == "__main__":
    main()


__all__ = ["run_scheduler"]
