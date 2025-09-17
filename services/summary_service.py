# 面试总结服务类

from services.llm_service import LLMService
from services.storage import StorageService

class SummaryService:
    """面试总结服务类，负责对面试问题和整场面试进行总结"""
    
    def __init__(self):
        """初始化总结服务"""
        self.llm_service = LLMService()
        self.storage_service = StorageService()
    
    def summarize_question_answer(self, question, answer):
        """总结单个面试问题和回答
        
        Args:
            question (str): 面试问题
            answer (str): 面试回答
            
        Returns:
            str: 总结内容
        """
        system_prompt = "你是一个专业的面试分析师。请总结下面的面试问题和回答，突出关键点和核心信息。"
        prompt = f"面试问题：{question}\n\n面试回答：{answer}\n\n请用简洁的语言总结这个问答的核心内容。"
        
        return self.llm_service.generate_response(prompt, system_prompt)
    
    def summarize_interview(self, interview_id):
        """总结整场面试
        
        Args:
            interview_id (str): 面试ID
            
        Returns:
            dict: 包含面试总结和分析的字典
        """
        # 获取面试数据
        interview_data = self.storage_service.get_interview(interview_id)
        
        # 构建面试内容文本
        interview_content = []
        interview_content.append(f"面试岗位: {interview_data.get('position', '未提供')}")
        interview_content.append(f"面试公司: {interview_data.get('company', '未提供')}")
        interview_content.append(f"面试日期: {interview_data.get('interview_date', '未提供')}")
        interview_content.append(f"面试问答内容: {interview_data.get('interview_content', '未提供')}")
        
        for qa in interview_data.get('questions_answers', []):
            interview_content.append(f"问题: {qa.get('question', '')}")
            interview_content.append(f"回答: {qa.get('answer', '')}\n")
        
        full_content = '\n'.join(interview_content)
        
        # 生成面试总结
        system_prompt = "你是一个经验丰富的面试教练。请对整场面试进行全面总结和分析。"
        prompt = f"{full_content}\n\n请从以下几个方面对整场面试进行总结：\n1. 面试的整体内容和重点领域\n2. 候选人在哪些方面表现较好\n3. 候选人在哪些方面需要改进\n4. 总体评价和建议\n5. 可能的面试结果预测"
        
        summary = self.llm_service.generate_response(prompt, system_prompt)
        
        # 更新面试数据中的总结
        interview_data['summary'] = summary
        self.storage_service.save_interview(interview_data)
        
        # 提取关键信息
        key_points = self._extract_key_points(summary)
        
        return {
            'interview_id': interview_id,
            'summary': summary,
            'key_points': key_points
        }
    
    def analyze_answer_quality(self, question, answer):
        """分析面试回答质量，提供反馈和改进建议
        
        Args:
            question (str): 面试问题
            answer (str): 面试回答
            
        Returns:
            str: 分析结果和改进建议
        """
        return self.llm_service.analyze_interview_answer(question, answer)
    
    def _extract_key_points(self, summary):
        """从总结中提取关键点
        
        Args:
            summary (str): 面试总结
            
        Returns:
            list: 关键点列表
        """
        # 这里可以根据实际需求实现更复杂的关键点提取逻辑
        # 简单实现：按段落分割，取每段的第一句话作为关键点
        key_points = []
        paragraphs = summary.split('\n')
        
        for para in paragraphs:
            para = para.strip()
            if para and len(para) > 10:
                # 取段落的前50个字符作为关键点摘要
                key_points.append(para[:50] + ('...' if len(para) > 50 else ''))
        
        return key_points
    
    def batch_summarize_interviews(self, interview_ids):
        """批量总结多个面试
        
        Args:
            interview_ids (list): 面试ID列表
            
        Returns:
            list: 每个面试的总结结果
        """
        results = []
        
        for interview_id in interview_ids:
            try:
                summary_result = self.summarize_interview(interview_id)
                results.append({
                    'interview_id': interview_id,
                    'summary': summary_result['summary']
                })
            except Exception as e:
                results.append({
                    'interview_id': interview_id,
                    'error': str(e)
                })
        
        return results