import json
import configparser

class ParameterHandler:
    def __init__(self, default_params=None):
        self.params = default_params if default_params else {}

    def load_from_dict(self, param_dict):
        self.params.update(param_dict)

    def load_from_json(self, json_file):
        with open(json_file, 'r') as f:
            self.params.update(json.load(f))

    def load_from_ini(self, ini_file):
        config = configparser.ConfigParser()
        config.read(ini_file)
        for section in config.sections():
            for key, value in config.items(section):
                self.params[key] = self._convert_type(value)

    def get_param(self, key, default=None):
        return self.params.get(key, default)

    def _convert_type(self, value):
        # 尝试将字符串转换为适当的类型（int, float, bool, None）
        if value.isdigit():
            return int(value)
        try:
            return float(value)
        except ValueError:
            pass
        if value.lower() in ['true', 'false']:
            return value.lower() == 'true'
        if value.lower() == 'none':
            return None
        return value


if __name__ == '__main__':
    # 示例用法
    default_params = {
        'fast_period': 5,
        'slow_period': 15,
        'volume_threshold': 1.5,
        'volume_window': 5,
        'use_lever': 8,
        'test_flag': False,
        'lost_perc': 0.05,
    }

    update_params = {
        'fast_period': 100,
        'slow_period': 200
    }
    # 创建参数处理器实例
    param_handler = ParameterHandler(default_params)

    # 从字典加载参数
    # param_handler.load_from_dict({'fast_period': 10, 'slow_period': 20})
    param_handler.load_from_dict(update_params)

    # 从 JSON 文件加载参数
    # param_handler.load_from_json('test/params.json')

    # 从 INI 文件加载参数
    # param_handler.load_from_ini('test/params.ini')

    # 获取参数
    # fast_period = param_handler.get_param('fast_period')
    # slow_period = param_handler.get_param('slow_period')
    # test_flag  = param_handler.get_param('test_flag')
    # lost_perc = param_handler.get_param('lost_perc')
    # test_add = param_handler.get_param('test_add', 20)
    # print(f'fast_period: {fast_period}, slow_period: {slow_period}, test_flag: {test_flag},lost_perc:{lost_perc}')
    # print(f'test_add:{test_add}')

    param_handler.load_from_json('configure/user_cfg.json')
    key = param_handler.get_param('key')
    secret = param_handler.get_param('secret')

    print(f'key:{key}')
    print(f'secret:{secret}')


