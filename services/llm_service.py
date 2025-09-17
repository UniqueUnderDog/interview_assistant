# 大语言模型服务类

import os
from volcenginesdkarkruntime import Ark
from config import LLM_CONFIG

class LLMService:
    """大语言模型服务类，封装火山引擎方舟大模型API调用"""
    
    def __init__(self):
        """初始化LLM服务"""
        self.api_key = LLM_CONFIG['api_key']
        self.model = LLM_CONFIG['model']
        self.timeout = LLM_CONFIG['timeout']
        self.client = self._init_client()
    
    def _init_client(self):
        """初始化方舟客户端"""
        return Ark(
            api_key=os.environ.get("ARK_API_KEY", self.api_key),
            timeout=self.timeout,
        )
    
    def generate_response(self, prompt, system_prompt=None):
        """生成模型响应
        
        Args:
            prompt (str): 用户输入的提示
            system_prompt (str, optional): 系统提示
            
        Returns:
            str: 模型生成的响应内容
        """
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
            
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"LLM API调用失败: {e}")
            return f"错误: 无法获取模型响应 - {str(e)}"
    
    def summarize_text(self, text, max_length=300):
        """总结文本内容
        
        Args:
            text (str): 要总结的文本
            max_length (int, optional): 总结的最大长度
            
        Returns:
            str: 总结后的文本
        """
        system_prompt = f"你是一个专业的文本总结助手。请将下面的文本总结为{max_length}字以内的内容，保持关键信息完整。"
        prompt = text
        
        return self.generate_response(prompt, system_prompt)
    
    def extract_info_from_text(self, text, info_type):
        """从文本中提取特定类型的信息
        
        Args:
            text (str): 源文本
            info_type (str): 要提取的信息类型描述
            
        Returns:
            str: 提取的信息
        """
        system_prompt = "你是一个信息提取助手。请根据用户要求从文本中提取相关信息。"
        prompt = f"请从下面的文本中提取{info_type}：\n\n{text}"
        
        return self.generate_response(prompt, system_prompt)
    
    def analyze_interview_answer(self, question, answer):
        """分析面试回答质量
        
        Args:
            question (str): 面试问题
            answer (str): 面试回答
            
        Returns:
            str: 分析结果和改进建议
        """
        system_prompt = "你是一个行业专家。请分析下面的面试回答，提供反馈和改进建议。"
        prompt = f"个人简历：{resume_info}\n\n面试问题：{question}\n\n面试回答：{answer}\n\n请分析这个回答的优点和不足，并给出具体的改进建议。"
        
        return self.generate_response(prompt, system_prompt)
    
    def predict_questions(self, resume_info, job_description, num_questions=10):
        """根据简历和岗位描述预测可能的面试问题
        
        Args:
            resume_info (str): 简历信息摘要
            job_description (str): 岗位描述
            num_questions (int, optional): 预测的问题数量
            
        Returns:
            str: 预测的面试问题列表
        """
        system_prompt = "你是一个经验丰富的面试官。请根据候选人的简历和岗位描述，预测可能的面试问题。"
        prompt = f"简历摘要：{resume_info}\n\n岗位描述：{job_description}\n\n请预测{num_questions}个最可能的面试问题，包括技术问题和行为问题，主要针对候选人的过往经历以及延伸的技术问题，你的问题应当聚焦，项目的出发点，项目的难点，项目的解决方法。"
        
        return self.generate_response(prompt, system_prompt)