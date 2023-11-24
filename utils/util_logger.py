# -*- coding:utf-8 -*-
import os, sys
from loguru import logger

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_PATH)


def get_logger(name):
    logger.add(os.path.join(PROJECT_PATH, "logs", f"{name}.log"),
               level='DEBUG',
               # format='{time:YYYY-MM-DD HH:mm:ss} - {level} - {line} : {message}',
               format="{time:YYYY-MM-DD HH:mm:ss.ms} {level} | {module}.{function}:{line} : {message}",
               rotation="500 MB")
    return logger
