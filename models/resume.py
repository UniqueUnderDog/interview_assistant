# 简历管理模型

import os
from datetime import datetime
from utils.file_utils import FileUtils
from utils.file_parser import FileParser
from services.storage import StorageService
from services.llm_service import LLMService
from config import RESUMES_DIR

class Resume:
    """简历模型类，用于管理简历数据和操作"""
    
    def __init__(self, resume_id=None, file_path=None, upload_time=None, user_info=None):
        """初始化简历对象
        
        Args:
            resume_id (str, optional): 简历ID
            file_path (str, optional): 简历文件路径
            upload_time (str, optional): 上传时间
            user_info (dict, optional): 用户信息字典
        """
        self.resume_id = resume_id or FileUtils.generate_unique_filename()
        self.file_path = file_path
        self.upload_time = upload_time or datetime.now().isoformat()
        self.user_info = user_info or {}
        self._storage_service = StorageService()
        self._llm_service = LLMService()
    
    def save(self, resume_content, original_filename=None):
        """保存简历文件
        
        Args:
            resume_content (bytes): 简历文件内容
            original_filename (str, optional): 原始文件名
            
        Returns:
            Resume: 当前简历对象
        """
        self.file_path = self._storage_service.save_resume(resume_content, original_filename)
        self.resume_id = os.path.basename(self.file_path).split('.')[0]
        self.upload_time = datetime.now().isoformat()
        
        # 尝试从简历中提取信息
        self.extract_info()
        
        return self
    
    def load(self, resume_id):
        """加载简历文件
        
        Args:
            resume_id (str): 简历ID
            
        Returns:
            Resume: 当前简历对象
        """
        # 查找对应ID的简历文件
        resume_files = self._storage_service.list_resumes()
        target_file = None
        
        for file_path in resume_files:
            if os.path.basename(file_path).startswith(resume_id):
                target_file = file_path
                break
        
        if not target_file:
            raise FileNotFoundError(f"未找到ID为 {resume_id} 的简历")
        
        self.file_path = target_file
        self.resume_id = os.path.basename(target_file).split('.')[0]
        
        # 尝试从文件名或文件内容中获取上传时间
        # 这里简单处理，实际可以根据需要实现更复杂的逻辑
        self.upload_time = datetime.fromtimestamp(os.path.getctime(target_file)).isoformat()
        
        # 如果是JSON格式的简历文件，直接加载其中的信息
        file_ext = os.path.splitext(target_file)[1].lower()
        if file_ext == '.json':
            try:
                with open(target_file, 'r', encoding='utf-8') as f:
                    resume_data = json.load(f)
                    if 'user_info' in resume_data:
                        self.user_info = resume_data['user_info']
                        # 如果JSON中有上传时间，使用它
                        if 'upload_time' in resume_data:
                            self.upload_time = resume_data['upload_time']
                        return self
            except Exception as e:
                print(f"加载JSON格式简历失败: {e}")
        
        # 对于非JSON格式的简历，尝试从中提取信息
        self.extract_info()
        
        return self
    
    def extract_info(self):
        """从简历文件中提取信息
        
        Returns:
            dict: 提取的用户信息
        """
        try:
            # 如果是JSON格式的简历，已经在load方法中加载了信息，这里不再处理
            file_ext = os.path.splitext(self.file_path)[1].lower()
            if file_ext == '.json':
                # 检查是否已经加载了user_info
                if self.user_info:
                    return self.user_info
                
            # 使用FileParser解析不同格式的简历文件
            try:
                file_content = self._storage_service.get_resume(self.file_path)
                content = FileParser.parse_file(self.file_path, file_content)
                # 清理解析后的文本
                content = FileParser.clean_text(content)
            except Exception as e:
                print(f"解析简历文件失败: {e}")
                content = f"解析简历文件失败: {str(e)}"
            
            # 使用LLM提取信息
            info_types = [
                "姓名", "联系方式", "邮箱", "学历背景", "工作经历", 
                "项目经验",  "专业证书" , "学术著作"
            ]
            
            extracted_info = {}
            for info_type in info_types:
                try:
                    info = self._llm_service.extract_info_from_text(content, info_type)
                    extracted_info[info_type] = info
                except Exception as e:
                    print(f"提取{info_type}失败: {e}")
                    extracted_info[info_type] = "未提取到"
            
            self.user_info = extracted_info
            return extracted_info
        except Exception as e:
            print(f"提取简历信息失败: {e}")
            self.user_info = {"error": str(e)}
            return self.user_info
    
    def get_content(self):
        """获取简历文件内容
        
        Returns:
            bytes: 简历文件内容
        """
        if not self.file_path:
            raise ValueError("简历文件路径未设置")
        
        return self._storage_service.get_resume(self.file_path)
    
    def delete(self):
        """删除简历文件
        
        Returns:
            bool: 是否删除成功
        """
        if not self.file_path:
            raise ValueError("简历文件路径未设置")
        
        try:
            self._storage_service.delete_resume(self.file_path)
            self.file_path = None
            return True
        except Exception as e:
            print(f"删除简历失败: {e}")
            return False
    
    def to_dict(self):
        """将简历对象转换为字典
        
        Returns:
            dict: 简历信息字典
        """
        return {
            'resume_id': self.resume_id,
            'file_path': self.file_path,
            'upload_time': self.upload_time,
            'user_info': self.user_info
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建简历对象
        
        Args:
            data (dict): 简历信息字典
            
        Returns:
            Resume: 简历对象
        """
        return cls(
            resume_id=data.get('resume_id'),
            file_path=data.get('file_path'),
            upload_time=data.get('upload_time'),
            user_info=data.get('user_info')
        )