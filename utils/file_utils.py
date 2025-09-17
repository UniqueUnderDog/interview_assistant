# 文件处理工具类

import os
import json
import uuid
from datetime import datetime

class FileUtils:
    """文件处理工具类，提供文件读写、生成唯一文件名等功能"""
    
    @staticmethod
    def generate_unique_filename(original_filename=None):
        """生成唯一的文件名"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        
        if original_filename:
            # 保留原始文件扩展名
            _, ext = os.path.splitext(original_filename)
            return f"{timestamp}_{unique_id}{ext}"
        
        return f"{timestamp}_{unique_id}"
    
    @staticmethod
    def save_json(data, file_path):
        """保存JSON数据到文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    @staticmethod
    def load_json(file_path):
        """从文件加载JSON数据"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def save_file(content, file_path):
        """保存内容到文件"""
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(content)
    
    @staticmethod
    def read_file(file_path):
        """读取文件内容"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        with open(file_path, 'rb') as f:
            return f.read()
    
    @staticmethod
    def get_file_extension(filename):
        """获取文件扩展名"""
        _, ext = os.path.splitext(filename)
        return ext.lower()
    
    @staticmethod
    def list_files(directory, extensions=None):
        """列出目录下的所有文件，可以按扩展名过滤"""
        if not os.path.exists(directory):
            return []
        
        files = []
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path):
                if extensions is None or FileUtils.get_file_extension(filename) in extensions:
                    files.append(file_path)
        
        return files