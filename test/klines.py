#!/usr/bin/env python
import logging
from binance.um_futures import UMFutures
from binance.lib.utils import config_logging


def setup_logging():
    # 创建logger
    logger = logging.getLogger('BTLOG')
    logger.setLevel(logging.DEBUG)  # 设置最低日志级别

    # 创建控制台handler并设置级别为DEBUG
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # 创建文件handler并设置级别为WARNING
    file_handler = logging.FileHandler('BNLOG.log',mode='w') # mode='w' 'a'
    file_handler.setLevel(logging.WARNING)
 
    # 创建formatter并添加到handlers
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # 将handlers添加到logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


config_logging(logging, logging.DEBUG)


um_futures_client = UMFutures()

logging.info(um_futures_client.klines("BTCUSDT", "1d"))
