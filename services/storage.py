# 存储服务类

import os
import json
from datetime import datetime
from utils.file_utils import FileUtils
from config import RESUMES_DIR, INTERVIEWS_DIR, SUPPORTED_RESUME_FORMATS

class StorageService:
    """存储服务类，负责管理本地文件的存储和读取"""
    
    def __init__(self):
        """初始化存储服务"""
        # 确保数据目录存在
        os.makedirs(RESUMES_DIR, exist_ok=True)
        os.makedirs(INTERVIEWS_DIR, exist_ok=True)
    
    def save_resume(self, resume_content, original_filename=None):
        """保存简历文件
        
        Args:
            resume_content (bytes): 简历文件内容
            original_filename (str, optional): 原始文件名
            
        Returns:
            str: 保存后的文件路径
        """
        # 验证文件格式
        if original_filename:
            ext = FileUtils.get_file_extension(original_filename)
            if ext not in SUPPORTED_RESUME_FORMATS:
                raise ValueError(f"不支持的简历文件格式: {ext}，支持的格式: {SUPPORTED_RESUME_FORMATS}")
        
        # 生成唯一文件名
        filename = FileUtils.generate_unique_filename(original_filename)
        file_path = os.path.join(RESUMES_DIR, filename)
        
        # 保存文件
        FileUtils.save_file(resume_content, file_path)
        
        return file_path
    
    def get_resume(self, file_path):
        """获取简历文件内容
        
        Args:
            file_path (str): 简历文件路径
            
        Returns:
            bytes: 简历文件内容
        """
        # 确保文件在RESUMES_DIR目录下（安全检查）
        if not file_path.startswith(RESUMES_DIR):
            raise ValueError("无效的简历文件路径")
        
        return FileUtils.read_file(file_path)
    
    def list_resumes(self):
        """列出所有简历文件
        
        Returns:
            list: 简历文件路径列表
        """
        return FileUtils.list_files(RESUMES_DIR, SUPPORTED_RESUME_FORMATS)
    
    def save_interview(self, interview_data):
        """保存面试数据
        
        Args:
            interview_data (dict): 面试数据
            
        Returns:
            str: 保存后的文件路径
        """
        # 确保必要字段存在
        required_fields = ['title', 'company', 'position', 'interview_date', 'questions_answers']
        for field in required_fields:
            if field not in interview_data:
                raise ValueError(f"缺少必要的面试数据字段: {field}")
        
        # 如果没有interview_id，生成一个
        if 'interview_id' not in interview_data:
            interview_data['interview_id'] = FileUtils.generate_unique_filename()
            
        # 添加保存时间
        interview_data['save_time'] = datetime.now().isoformat()
        
        # 保存为JSON文件
        filename = f"{interview_data['interview_id']}.json"
        file_path = os.path.join(INTERVIEWS_DIR, filename)
        
        FileUtils.save_json(interview_data, file_path)
        
        return file_path
    
    def get_interview(self, interview_id):
        """获取面试数据
        
        Args:
            interview_id (str): 面试ID
            
        Returns:
            dict: 面试数据
        """
        filename = f"{interview_id}.json"
        file_path = os.path.join(INTERVIEWS_DIR, filename)
        
        return FileUtils.load_json(file_path)
    
    def list_interviews(self):
        """列出所有面试数据
        
        Returns:
            list: 面试数据列表
        """
        interviews = []
        json_files = FileUtils.list_files(INTERVIEWS_DIR, ['.json'])
        
        for file_path in json_files:
            try:
                interview_data = FileUtils.load_json(file_path)
                interviews.append(interview_data)
            except Exception as e:
                print(f"加载面试数据失败 ({file_path}): {e}")
                continue
        
        # 按面试日期排序（最新的在前）
        interviews.sort(key=lambda x: x.get('interview_date', ''), reverse=True)
        
        return interviews
    
    def delete_resume(self, file_path):
        """删除简历文件
        
        Args:
            file_path (str): 简历文件路径
        """
        # 确保文件在RESUMES_DIR目录下（安全检查）
        if not file_path.startswith(RESUMES_DIR):
            raise ValueError("无效的简历文件路径")
        
        if os.path.exists(file_path):
            os.remove(file_path)
    
    def delete_interview(self, interview_id):
        """删除面试数据
        
        Args:
            interview_id (str): 面试ID
        """
        filename = f"{interview_id}.json"
        file_path = os.path.join(INTERVIEWS_DIR, filename)
        
        if os.path.exists(file_path):
            os.remove(file_path)