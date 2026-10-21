import logging
import os
from logging.handlers import TimedRotatingFileHandler


def configure_logging():
    # 确保logs目录存在，如果不存在则创建
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 设置日志文件路径
    log_file_path = os.path.join(log_dir, 'app.log')

    # 创建文件日志处理器，按天滚动日志
    file_handler = TimedRotatingFileHandler(log_file_path, when='midnight', interval=1, backupCount=7)
    file_handler.setLevel(logging.INFO)  # 设置日志级别为INFO

    # 创建日志格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 创建控制台日志处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)  # 设置控制台日志级别为INFO
    console_handler.setFormatter(formatter)

    # 获取根日志器并添加处理器
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # 设置根日志器的日志级别
    logger.addHandler(file_handler)  # 添加文件处理器
    logger.addHandler(console_handler)  # 添加控制台处理器