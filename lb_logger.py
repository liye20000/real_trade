from loguru import logger
import os
import sys

log_formats = {
    "DEBUG": "{time} - {level} - {message}",
    "INFO": "{message}",
    "WARNING": "{time} - {level} - {message}",
    "ERROR": "{time} - {level} - {message} - {file} - {function} - {line}",
    "CRITICAL": "{time} - {level} - {message} - {file} - {function} - {line}"
}

def setup_logger(log_dir="logs"):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    logger.remove()

    # logger.add(os.path.join(log_dir, "debug.log"), level="DEBUG", format=log_formats["DEBUG"])
    # logger.add(os.path.join(log_dir, "info.log"), level="INFO", format=log_formats["INFO"])
    # logger.add(os.path.join(log_dir, "warning.log"), level="WARNING", format=log_formats["WARNING"])
    # logger.add(os.path.join(log_dir, "error.log"), level="ERROR", format=log_formats["ERROR"])

    # 配置控制台输出，根据日志级别设置不同的格式
    logger.add(sys.stdout, level="DEBUG", format=log_formats["DEBUG"], filter=lambda record: record["level"].name == "DEBUG")
    logger.add(sys.stdout, level="INFO", format=log_formats["INFO"], filter=lambda record: record["level"].name == "INFO")
    logger.add(sys.stdout, level="WARNING", format=log_formats["WARNING"], filter=lambda record: record["level"].name == "WARNING")
    logger.add(sys.stdout, level="ERROR", format=log_formats["ERROR"], filter=lambda record: record["level"].name == "ERROR")
    logger.add(sys.stdout, level="CRITICAL", format=log_formats["CRITICAL"], filter=lambda record: record["level"].name == "CRITICAL")

setup_logger()

log = logger

if __name__ == '__main__':
    log.debug("Debug Test")
    log.info("Info Test")
    log.warning("Warning Test")
    log.error("Error Test")
    log.critical("Critical Test")
