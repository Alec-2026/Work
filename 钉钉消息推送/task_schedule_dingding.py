"""每天北京时间 08:50 调用 app.send_message；需保持本进程运行。

启动：python task_schedule_dingding.py
错过的任务不补发，启动时已过 08:50 则从次日开始。
"""

import logging
import time
from datetime import datetime, timedelta, timezone

from app import send_message


BEIJING_TIME = timezone(timedelta(hours=8))
logger = logging.getLogger(__name__)


def get_next_run_time(now):
    """根据当前时间计算下一次北京时间 08:50 的执行时间。"""
    now = now.astimezone(BEIJING_TIME)
    next_run = now.replace(hour=8, minute=50, second=0, microsecond=0)
    if next_run <= now:
        next_run += timedelta(days=1)
    return next_run


def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
    )
    try:
        while True:
            next_run = get_next_run_time(datetime.now(BEIJING_TIME))
            logger.info('下次执行时间（北京时间）：%s', next_run.isoformat())
            while True:
                now = datetime.now(BEIJING_TIME)
                remaining = (next_run - now).total_seconds()
                if remaining <= 0:
                    break
                time.sleep(min(remaining, 30))

            # 跨日休眠恢复后不补发已错过日期的消息。
            if now.date() != next_run.date():
                continue
            try:
                logger.info('开始调用 app.send_message')
                send_message()
                logger.info('app.send_message 调用结束，发送结果以推送接口日志为准')
            except Exception:
                logger.exception('定时任务执行异常，将继续等待下一次调度')
    except KeyboardInterrupt:
        logger.info('定时任务已停止')


if __name__ == '__main__':
    main()
