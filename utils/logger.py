# -*- coding: utf-8 -*-
import os
import logging
from datetime import datetime


def get_logger(name: str = "crypto_logger", log_dir: str = "logs", log_to_file: bool = False) -> logging.Logger:
    """
    获取一个可复用的 logger 实例。

    :param name: logger 名称（一般使用 __name__）
    :param log_dir: 日志目录
    :param log_to_file: 是否输出日志到文件
    :return: logger 实例
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # 可根据需要设置成 INFO、WARNING 等

    if not logger.handlers:
        # 设置输出格式
        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - [%(levelname)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # 控制台输出
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 文件输出（可选）
        if log_to_file:
            os.makedirs(log_dir, exist_ok=True)
            log_filename = datetime.now().strftime("%Y%m%d_%H%M%S.log")
            file_path = os.path.join(log_dir, log_filename)

            file_handler = logging.FileHandler(file_path, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
