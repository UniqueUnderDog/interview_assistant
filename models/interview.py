# 面试管理模型

import os
from datetime import datetime
from services.storage import StorageService
from services.summary_service import SummaryService
from utils.file_utils import FileUtils
from config import INTERVIEWS_DIR

class Interview:
    """面试模型类，用于管理面试数据和操作"""
    
    def __init__(self, interview_id=None, title=None, company=None, position=None, interview_date=None, 
                 questions_answers=None, summary=None):
        """初始化面试对象
        
        Args:
            interview_id (str, optional): 面试ID
            title (str, optional): 面试标题
            company (str, optional): 公司名称
            position (str, optional): 面试岗位
            interview_date (str, optional): 面试日期
            questions_answers (list, optional): 问题和回答列表
            summary (str, optional): 面试总结
        """
        self.interview_id = interview_id or FileUtils.generate_unique_filename()
        self.title = title or f"未命名面试_{datetime.now().strftime('%Y%m%d')}"
        self.company = company or "未知公司"
        self.position = position or "未知岗位"
        self.interview_date = interview_date or datetime.now().strftime('%Y-%m-%d')
        self.questions_answers = questions_answers or []
        self.summary = summary
        self.save_time = datetime.now().isoformat()
        
        self._storage_service = StorageService()
        self._summary_service = SummaryService()
    
    def save(self):
        """保存面试数据
        
        Returns:
            Interview: 当前面试对象
        """
        interview_data = self.to_dict()
        file_path = self._storage_service.save_interview(interview_data)
        
        # 更新保存时间
        self.save_time = datetime.now().isoformat()
        
        return self
    
    def load(self, interview_id):
        """加载面试数据
        
        Args:
            interview_id (str): 面试ID
            
        Returns:
            Interview: 当前面试对象
        """
        try:
            interview_data = self._storage_service.get_interview(interview_id)
            
            # 更新对象属性
            self.interview_id = interview_data.get('interview_id', self.interview_id)
            self.title = interview_data.get('title', self.title)
            self.company = interview_data.get('company', self.company)
            self.position = interview_data.get('position', self.position)
            self.interview_date = interview_data.get('interview_date', self.interview_date)
            self.questions_answers = interview_data.get('questions_answers', self.questions_answers)
            self.summary = interview_data.get('summary', self.summary)
            self.save_time = interview_data.get('save_time', datetime.now().isoformat())
            
            return self
        except Exception as e:
            print(f"加载面试数据失败: {e}")
            raise
    
    def add_question_answer(self, question, answer, notes=None):
        """添加面试问题和回答
        
        Args:
            question (str): 面试问题
            answer (str): 面试回答
            notes (str, optional): 备注信息
            
        Returns:
            Interview: 当前面试对象
        """
        qa_item = {
            'question': question,
            'answer': answer,
            'notes': notes,
            'timestamp': datetime.now().isoformat()
        }
        
        self.questions_answers.append(qa_item)
        
        # 自动保存更新
        self.save()
        
        return self
    
    def update_question_answer(self, index, question=None, answer=None, notes=None):
        """更新面试问题和回答
        
        Args:
            index (int): 问题和回答的索引
            question (str, optional): 新的面试问题
            answer (str, optional): 新的面试回答
            notes (str, optional): 新的备注信息
            
        Returns:
            Interview: 当前面试对象
        """
        if 0 <= index < len(self.questions_answers):
            if question is not None:
                self.questions_answers[index]['question'] = question
            if answer is not None:
                self.questions_answers[index]['answer'] = answer
            if notes is not None:
                self.questions_answers[index]['notes'] = notes
            
            # 更新时间戳
            self.questions_answers[index]['timestamp'] = datetime.now().isoformat()
            
            # 自动保存更新
            self.save()
        else:
            raise IndexError(f"索引 {index} 超出范围")
        
        return self
    
    def delete_question_answer(self, index):
        """删除面试问题和回答
        
        Args:
            index (int): 问题和回答的索引
            
        Returns:
            Interview: 当前面试对象
        """
        if 0 <= index < len(self.questions_answers):
            del self.questions_answers[index]
            
            # 自动保存更新
            self.save()
        else:
            raise IndexError(f"索引 {index} 超出范围")
        
        return self
    
    def generate_summary(self):
        """生成面试总结
        
        Returns:
            str: 面试总结
        """
        try:
            # 使用总结服务生成面试总结
            summary_result = self._summary_service.summarize_interview(self.interview_id)
            self.summary = summary_result['summary']
            
            # 保存更新
            self.save()
            
            return self.summary
        except Exception as e:
            print(f"生成面试总结失败: {e}")
            return f"错误: 无法生成面试总结 - {str(e)}"
    
    def analyze_answer(self, index):
        """分析特定问题的回答质量
        
        Args:
            index (int): 问题和回答的索引
            
        Returns:
            str: 分析结果和改进建议
        """
        if 0 <= index < len(self.questions_answers):
            qa = self.questions_answers[index]
            analysis = self._summary_service.analyze_answer_quality(qa['question'], qa['answer'])
            
            # 将分析结果添加到备注中
            if 'analysis' not in qa:
                qa['analysis'] = []
            qa['analysis'].append({
                'content': analysis,
                'timestamp': datetime.now().isoformat()
            })
            
            # 保存更新
            self.save()
            
            return analysis
        else:
            raise IndexError(f"索引 {index} 超出范围")
    
    def delete(self):
        """删除面试数据
        
        Returns:
            bool: 是否删除成功
        """
        try:
            self._storage_service.delete_interview(self.interview_id)
            return True
        except Exception as e:
            print(f"删除面试数据失败: {e}")
            return False
    
    def to_dict(self):
        """将面试对象转换为字典
        
        Returns:
            dict: 面试信息字典
        """
        return {
            'interview_id': self.interview_id,
            'title': self.title,
            'company': self.company,
            'position': self.position,
            'interview_date': self.interview_date,
            'questions_answers': self.questions_answers,
            'summary': self.summary,
            'save_time': self.save_time
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建面试对象
        
        Args:
            data (dict): 面试信息字典
            
        Returns:
            Interview: 面试对象
        """
        return cls(
            interview_id=data.get('interview_id'),
            title=data.get('title'),
            company=data.get('company'),
            position=data.get('position'),
            interview_date=data.get('interview_date'),
            questions_answers=data.get('questions_answers'),
            summary=data.get('summary')
        )
    
    @classmethod
    def list_interviews(cls):
        """列出所有面试
        
        Returns:
            list: 面试对象列表
        """
        storage_service = StorageService()
        interviews_data = storage_service.list_interviews()
        
        interviews = []
        for data in interviews_data:
            try:
                interview = cls.from_dict(data)
                interviews.append(interview)
            except Exception as e:
                print(f"创建面试对象失败: {e}")
                continue
        
        return interviews