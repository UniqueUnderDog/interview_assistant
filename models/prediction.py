# 面试预测模型

import os
from datetime import datetime
from services.prediction_service import PredictionService
from models.resume import Resume
from utils.file_utils import FileUtils

class Prediction:
    """面试预测模型类，用于管理面试预测数据和操作"""
    
    def __init__(self, prediction_id=None, target_position=None, target_company=None, 
                 resume_id=None, recommended_questions=None, preparation_plan=None):
        """初始化预测对象
        
        Args:
            prediction_id (str, optional): 预测ID
            target_position (str, optional): 目标岗位
            target_company (str, optional): 目标公司
            resume_id (str, optional): 关联的简历ID
            recommended_questions (list, optional): 推荐的面试问题列表
            preparation_plan (str, optional): 准备计划
        """
        self.prediction_id = prediction_id or FileUtils.generate_unique_filename()
        self.target_position = target_position
        self.target_company = target_company
        self.resume_id = resume_id
        self.recommended_questions = recommended_questions or []
        self.recommended_topics = []
        self.preparation_plan = preparation_plan
        self.generated_time = datetime.now().isoformat()
        
        self._prediction_service = PredictionService()
    
    def generate_predictions(self, resume_content=None):
        """生成面试预测
        
        Args:
            resume_content (str, optional): 简历内容文本
            
        Returns:
            Prediction: 当前预测对象
        """
        if not self.target_position:
            raise ValueError("目标岗位未设置")
        
        # 如果未提供简历内容，但提供了简历ID，则尝试加载简历
        if not resume_content and self.resume_id:
            try:
                resume = Resume().load(self.resume_id)
                # 这里简化处理，实际应该根据文件格式提取文本内容
                resume_content = f"简历信息：{resume.to_dict()}"
            except Exception as e:
                print(f"加载简历失败: {e}")
                resume_content = ""
        
        # 预测面试问题
        self.recommended_questions = self._prediction_service.predict_interview_questions(
            resume_content or "", 
            self.target_position, 
            self.target_company
        )
        
        # 推荐学习主题
        self.recommended_topics = self._prediction_service.recommend_study_topics(
            self.target_position, 
            resume_content
        )
        
        # 生成准备计划
        self.preparation_plan = self._prediction_service.prepare_interview(
            resume_content or "", 
            self.target_position, 
            self.target_company
        )
        
        # 更新生成时间
        self.generated_time = datetime.now().isoformat()
        
        # 保存预测结果
        self.save()
        
        return self
    
    def save(self):
        """保存预测结果
        
        Returns:
            Prediction: 当前预测对象
        """
        # 这里简化处理，实际应该将预测结果保存到文件或数据库
        # 为了演示，我们将预测结果打印出来
        print(f"保存预测结果: {self.prediction_id}")
        
        # 实际应用中，应该将预测结果保存到文件或数据库
        # prediction_data = self.to_dict()
        # FileUtils.save_json(prediction_data, f"predictions/{self.prediction_id}.json")
        
        return self
    
    def load(self, prediction_id):
        """加载预测结果
        
        Args:
            prediction_id (str): 预测ID
            
        Returns:
            Prediction: 当前预测对象
        """
        # 这里简化处理，实际应该从文件或数据库加载预测结果
        # 为了演示，我们直接返回一个空的预测对象
        print(f"加载预测结果: {prediction_id}")
        
        # 实际应用中，应该从文件或数据库加载预测结果
        # prediction_data = FileUtils.load_json(f"predictions/{prediction_id}.json")
        # self.from_dict(prediction_data)
        
        return self
    
    def get_recommendations(self):
        """获取推荐信息
        
        Returns:
            dict: 推荐信息字典
        """
        return {
            'prediction_id': self.prediction_id,
            'target_position': self.target_position,
            'target_company': self.target_company,
            'recommended_questions': self.recommended_questions,
            'recommended_topics': self.recommended_topics,
            'preparation_plan': self.preparation_plan,
            'generated_time': self.generated_time
        }
    
    def to_dict(self):
        """将预测对象转换为字典
        
        Returns:
            dict: 预测信息字典
        """
        return {
            'prediction_id': self.prediction_id,
            'target_position': self.target_position,
            'target_company': self.target_company,
            'resume_id': self.resume_id,
            'recommended_questions': self.recommended_questions,
            'recommended_topics': self.recommended_topics,
            'preparation_plan': self.preparation_plan,
            'generated_time': self.generated_time
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建预测对象
        
        Args:
            data (dict): 预测信息字典
            
        Returns:
            Prediction: 预测对象
        """
        return cls(
            prediction_id=data.get('prediction_id'),
            target_position=data.get('target_position'),
            target_company=data.get('target_company'),
            resume_id=data.get('resume_id'),
            recommended_questions=data.get('recommended_questions'),
            preparation_plan=data.get('preparation_plan')
        )