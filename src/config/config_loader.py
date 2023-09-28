
import configparser

# 读取配置文件
config = configparser.ConfigParser()
config.read('../config.ini')

def get(section, key): return config.get(section, key)

def get_enum(section, key): return config.get(section, key).lower()

def get_int(section, key): return int(config.get(section, key))

def get_bool(section, key): return config.get(section, key).lower() == "true"