from dotenv import load_dotenv
import os

# 加载 .env 文件
load_dotenv()

def get_plugin_config(Config):
    config = Config()
    config.proxy = os.getenv('PROXY')
    return config