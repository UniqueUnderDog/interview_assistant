# 个人面试助手配置文件

import os

# 项目根目录
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 数据存储目录
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESUMES_DIR = os.path.join(DATA_DIR, 'resumes')
INTERVIEWS_DIR = os.path.join(DATA_DIR, 'interviews')

# 确保数据目录存在
os.makedirs(RESUMES_DIR, exist_ok=True)
os.makedirs(INTERVIEWS_DIR, exist_ok=True)

# LLM模型配置
LLM_CONFIG = {
    'api_key': os.environ.get('ARK_API_KEY', 'bbbb2dd9-de42-416b-9fb4-59ad0f45dc94'),
    'model': 'doubao-seed-1-6-thinking-250715',
    'timeout': 1800,  # 30分钟超时时间
}

# 文件格式配置
SUPPORTED_RESUME_FORMATS = ['.pdf', '.docx', '.doc', '.txt']

# 日志配置
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'