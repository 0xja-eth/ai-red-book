import configparser
import os

WORK_DIR = "../"

def file(path): return os.path.join(WORK_DIR, path)


# 读取配置文件
config = configparser.ConfigParser()
config.read(file('./config.ini'))


def get(section, key, type=None):
    if type == "int": return get_int(section, key)
    if type == "bool": return get_bool(section, key)
    if type == "enum": return get_enum(section, key)

    return config.get(section, key)


def get_enum(section, key): return config.get(section, key).lower()


def get_int(section, key): return int(config.get(section, key))


def get_bool(section, key): return config.get(section, key).lower() == "true"


if __name__ == '__main__':
    # Test
    print(os.path.exists(file('/config.ini')))
