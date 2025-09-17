# 面试预测服务类

from services.llm_service import LLMService
from services.storage import StorageService

class PredictionService:
    """面试预测服务类，负责基于简历和岗位信息预测面试题目"""
    
    def __init__(self):
        """初始化预测服务"""
        self.llm_service = LLMService()
        self.storage_service = StorageService()
    
    def predict_interview_questions(self, resume_content, target_position, target_company=None, num_questions=10):
        """预测面试题目
        
        Args:
            resume_content (str): 简历内容文本
            target_position (str): 目标岗位
            target_company (str, optional): 目标公司
            num_questions (int, optional): 预测的问题数量
            
        Returns:
            list: 预测的面试问题列表
        """
        # 获取历史面试数据，用于参考
        historical_interviews = self.storage_service.list_interviews()
        
        # 构建历史面试问题参考文本
        historical_questions = []
        for interview in historical_interviews:
            # 如果有相同或相似岗位的面试，优先参考
            if target_position.lower() in interview.get('position', '').lower():
                for qa in interview.get('questions_answers', []):
                    historical_questions.append(qa.get('question', ''))
        
        # 构建预测提示
        system_prompt = "你是一个经验丰富的面试官。请根据候选人的简历、目标岗位和历史面试问题，预测可能的面试问题。"
        
        prompt = f"简历内容：{resume_content[:1000]}...\n\n"
        prompt += f"目标岗位：{target_position}\n\n"
        
        if target_company:
            prompt += f"目标公司：{target_company}\n\n"
        
        if historical_questions:
            prompt += "历史类似岗位的面试问题参考：\n"
            prompt += "\n".join(historical_questions[:10]) + "\n\n"
        
        prompt += f"请预测{num_questions}个最可能的面试问题，你的问题应当聚焦，项目的出发点，项目的难点，项目的解决方法。，按重要性排序。"
        
        # 获取预测结果
        prediction_result = self.llm_service.generate_response(prompt, system_prompt)
        
        # 解析预测结果为问题列表
        questions = self._parse_prediction_result(prediction_result)
        
        return questions[:num_questions]  # 确保不超过请求的数量
    
    def recommend_study_topics(self, target_position, resume_content=None):
        """推荐面试准备的学习主题
        
        Args:
            target_position (str): 目标岗位
            resume_content (str, optional): 简历内容文本
            
        Returns:
            list: 推荐的学习主题列表
        """
        system_prompt = "你是一个专业的职业顾问。请根据目标岗位和候选人简历，推荐需要学习和准备的主题。"
        
        prompt = f"目标岗位：{target_position}\n\n"
        
        if resume_content:
            prompt += f"候选人简历摘要：{resume_content[:500]}...\n\n"
        
        prompt += "请列出10个最重要的学习和准备主题，包括技术技能、知识点和面试技巧。"
        
        # 获取推荐结果
        recommendation_result = self.llm_service.generate_response(prompt, system_prompt)
        
        # 解析推荐结果为主题列表
        topics = self._parse_prediction_result(recommendation_result)
        
        return topics[:10]  # 限制为10个主题
    
    def prepare_interview(self, resume_content, target_position, target_company=None, interview_date=None):
        """综合准备面试，包括预测问题和推荐学习主题
        
        Args:
            resume_content (str): 简历内容文本
            target_position (str): 目标岗位
            target_company (str, optional): 目标公司
            interview_date (str, optional): 面试日期
            
        Returns:
            dict: 包含预测问题、学习主题和准备建议的综合结果
        """
        # 预测面试问题
        predicted_questions = self.predict_interview_questions(
            resume_content, target_position, target_company
        )
        
        # 推荐学习主题
        recommended_topics = self.recommend_study_topics(target_position, resume_content)
        
        # 生成综合准备建议
        system_prompt = "你是一个专业的面试教练。请根据目标岗位、预测的面试问题和推荐的学习主题，提供综合的面试准备建议。"
        
        prompt = f"目标岗位：{target_position}\n\n"
        if target_company:
            prompt += f"目标公司：{target_company}\n\n"
        if interview_date:
            prompt += f"面试日期：{interview_date}\n\n"
        
        prompt += "预测的面试问题：\n"
        prompt += "\n".join([f"{i+1}. {q}" for i, q in enumerate(predicted_questions[:5])]) + "\n\n"
        
        prompt += "推荐的学习主题：\n"
        prompt += "\n".join([f"{i+1}. {t}" for i, t in enumerate(recommended_topics[:5])]) + "\n\n"
        
        prompt += "请提供一份详细的面试准备计划和建议，包括时间安排、重点内容和准备方法。"
        
        preparation_plan = self.llm_service.generate_response(prompt, system_prompt)
        
        return {
            'predicted_questions': predicted_questions,
            'recommended_topics': recommended_topics,
            'preparation_plan': preparation_plan
        }
    
    def _parse_prediction_result(self, text):
        """解析预测结果文本为列表
        
        Args:
            text (str): 预测结果文本
            
        Returns:
            list: 解析后的列表
        """
        result = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            # 匹配常见的列表格式，如 "1. 问题"、"- 问题"、"• 问题" 等
            if line and (line[0].isdigit() or line[0] in ['-', '•', '•', '*']):
                # 提取实际内容，去掉序号或符号
                content = ''
                if line[0].isdigit():
                    # 处理数字序号格式，如 "1. 问题" 或 "1) 问题"
                    content = line.split(' ', 1)[1] if ' ' in line else line
                    if content.startswith(')'):
                        content = content[1:].strip()
                else:
                    # 处理符号格式，如 "- 问题" 或 "• 问题"
                    content = line[1:].strip()
                
                if content:
                    result.append(content)
            elif line and len(line) > 10 and result:
                # 如果行不是列表项但有内容，可能是上一项的延续
                result[-1] += ' ' + line
        
        return result