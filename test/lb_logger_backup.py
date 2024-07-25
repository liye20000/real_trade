import logging
# 配置日志记录器
# 现有的
logging.basicConfig(level=logging.DEBUG,
                    format='%(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

log_formats = {
    logging.DEBUG: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    logging.INFO: '%(message)s',
    logging.WARNING: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    logging.ERROR: '%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s - %(funcName)s - %(lineno)d',
    logging.CRITICAL: '%(asctime)s - %(name)s - %(levellevel)s - %(message)s - %(filename)s - %(funcName)s - %(lineno)d'
}

class CustomFormatter(logging.Formatter):
    """自定义日志格式类，支持不同的日志级别使用不同的格式"""

    def __init__(self, formats):
        super().__init__()
        self.formats = formats

    def format(self, record):
        log_fmt = self.formats.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

# level = logging.DEBUG
# formats = CustomFormatter(log_formats)
# logfile = None

logger1 = logging.getLogger(__name__)
# logger.setLevel(level)
# logger.handlers.clear()
# # 创建自定义的日志处理器和格式化器
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(level)
# stream_handler.setFormatter(formats)
# logger.addHandler(stream_handler)

# if logfile:
#     file_handler = logging.FileHandler(filename=logfile, mode='a')
#     file_handler.setLevel(level)
#     file_handler.setFormatter(formats)
#     logger.addHandler(file_handler)

# 定义一个函数来获取日志记录器，以便在其他模块中使用
# def get_logger(name, level=logging.DEBUG, logfile=None, logformat=log_formats):
#     logger = logging.getLogger(name)
#     # logger.setLevel(level)
#     # logger.handlers.clear() 
#     # # 检查是否已有处理器，避免重复添加
#     # if not logger.hasHandlers():
#     #     formats = CustomFormatter(logformat)
        
#     #     # 创建自定义的日志处理器和格式化器
#     #     stream_handler = logging.StreamHandler()
#     #     stream_handler.setLevel(level)
#     #     stream_handler.setFormatter(formats)
#     #     logger.addHandler(stream_handler)

#     #     if logfile:
#     #         file_handler = logging.FileHandler(filename=logfile, mode='a')
#     #         file_handler.setLevel(level)
#     #         file_handler.setFormatter(formats)
#     #         logger.addHandler(file_handler)
#     #     print(f'Logger {name} handlers: {logger.handlers}')
#     return logger

# logger = get_logger(__name__) 

if __name__ == '__main__':
    
    test1 = logger1.getEffectiveLevel()
    logger1.debug(f'Just a debug test {test1}')
    logger1.info(f'Just a info test {test1}')
    logger1.error(f'Just a error test {test1}')
    logger1.warning(f'Just a warning test {test1}')
