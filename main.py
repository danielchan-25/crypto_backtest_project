# -*- coding: utf-8 -*-
from time import sleep
from utils.logger import get_logger
from data.spider_data import get_klines

logger = get_logger(__name__)

if __name__ == '__main__':
    while True:
        if not get_klines():    # 获取行情数据
            logger.error("无法获取 BTC 数据，请检查网络是否正常，程序已退出")
            break
        logger.info("数据获取成功，开始策略计算...")
        sleep(10)