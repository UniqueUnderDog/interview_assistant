# 个人面试助手主程序

import os
import argparse
from models.resume import Resume
from models.interview import Interview
from models.prediction import Prediction
from services.llm_service import LLMService
from config import BASE_DIR

class InterviewAssistant:
    """个人面试助手主类，整合所有功能模块"""
    
    def __init__(self):
        """初始化面试助手"""
        self.llm_service = LLMService()
    
    def upload_resume(self, file_path):
        """上传简历
        
        Args:
            file_path (str): 简历文件路径
            
        Returns:
            str: 简历ID
        """
        try:
            # 读取文件内容
            with open(file_path, 'rb') as f:
                resume_content = f.read()
            
            # 创建并保存简历对象
            resume = Resume()
            resume.save(resume_content, os.path.basename(file_path))
            
            print(f"简历上传成功！简历ID: {resume.resume_id}")
            print(f"提取的简历信息: {resume.user_info}")
            
            return resume.resume_id
        except Exception as e:
            print(f"简历上传失败: {e}")
            return None
    
    def create_interview(self, title, company, position, interview_date):
        """创建新的面试记录
        
        Args:
            title (str): 面试标题
            company (str): 公司名称
            position (str): 面试岗位
            interview_date (str): 面试日期
            
        Returns:
            str: 面试ID
        """
        try:
            interview = Interview(
                title=title,
                company=company,
                position=position,
                interview_date=interview_date
            )
            interview.save()
            
            print(f"面试记录创建成功！面试ID: {interview.interview_id}")
            
            return interview.interview_id
        except Exception as e:
            print(f"创建面试记录失败: {e}")
            return None
    
    def add_interview_qa(self, interview_id, question, answer, notes=None):
        """添加面试问题和回答
        
        Args:
            interview_id (str): 面试ID
            question (str): 面试问题
            answer (str): 面试回答
            notes (str, optional): 备注信息
            
        Returns:
            bool: 是否添加成功
        """
        try:
            interview = Interview().load(interview_id)
            interview.add_question_answer(question, answer, notes)
            
            print(f"面试问答添加成功！")
            
            return True
        except Exception as e:
            print(f"添加面试问答失败: {e}")
            return False
    
    def summarize_interview(self, interview_id):
        """生成面试总结
        
        Args:
            interview_id (str): 面试ID
            
        Returns:
            str: 面试总结
        """
        try:
            interview = Interview().load(interview_id)
            summary = interview.generate_summary()
            
            print(f"面试总结生成成功！")
            print(f"总结内容: {summary}")
            
            return summary
        except Exception as e:
            print(f"生成面试总结失败: {e}")
            return None
    
    def analyze_answer(self, interview_id, qa_index):
        """分析面试回答质量
        
        Args:
            interview_id (str): 面试ID
            qa_index (int): 问题回答的索引
            
        Returns:
            str: 分析结果
        """
        try:
            interview = Interview().load(interview_id)
            analysis = interview.analyze_answer(qa_index)
            
            print(f"回答分析成功！")
            print(f"分析结果: {analysis}")
            
            return analysis
        except Exception as e:
            print(f"分析回答失败: {e}")
            return None
    
    def predict_questions(self, target_position, target_company=None, resume_id=None):
        """预测面试题目
        
        Args:
            target_position (str): 目标岗位
            target_company (str, optional): 目标公司
            resume_id (str, optional): 简历ID
            
        Returns:
            dict: 预测结果
        """
        try:
            prediction = Prediction(
                target_position=target_position,
                target_company=target_company,
                resume_id=resume_id
            )
            
            # 如果提供了简历ID，尝试加载简历内容
            resume_content = None
            if resume_id:
                try:
                    resume = Resume().load(resume_id)
                    # 简化处理，实际应该根据文件格式提取文本内容
                    resume_content = f"简历信息：{resume.to_dict()}"
                except Exception as e:
                    print(f"加载简历失败，但仍会继续预测: {e}")
            
            prediction.generate_predictions(resume_content)
            
            print(f"面试题目预测成功！预测ID: {prediction.prediction_id}")
            print(f"推荐的面试问题: {prediction.recommended_questions}")
            print(f"推荐的学习主题: {prediction.recommended_topics}")
            
            return prediction.get_recommendations()
        except Exception as e:
            print(f"预测面试题目失败: {e}")
            return None
    
    def list_interviews(self):
        """列出所有面试记录
        
        Returns:
            list: 面试记录列表
        """
        interviews = Interview.list_interviews()
        
        print(f"找到 {len(interviews)} 条面试记录:")
        for i, interview in enumerate(interviews):
            print(f"{i+1}. {interview.title} - {interview.company} - {interview.position} - {interview.interview_date}")
        
        return interviews
    
    def get_chat_response(self, prompt):
        """获取大模型的聊天响应
        
        Args:
            prompt (str): 用户输入的提示
            
        Returns:
            str: 模型生成的响应
        """
        try:
            response = self.llm_service.generate_response(prompt)
            print(f"模型响应: {response}")
            return response
        except Exception as e:
            print(f"获取模型响应失败: {e}")
            return None

# 命令行接口
def main():
    parser = argparse.ArgumentParser(description='个人面试助手')
    subparsers = parser.add_subparsers(dest='command', help='支持的命令')
    
    # 上传简历命令
    upload_parser = subparsers.add_parser('upload_resume', help='上传简历')
    upload_parser.add_argument('file_path', help='简历文件路径')
    
    # 创建面试命令
    create_parser = subparsers.add_parser('create_interview', help='创建面试记录')
    create_parser.add_argument('--title', required=True, help='面试标题')
    create_parser.add_argument('--company', required=True, help='公司名称')
    create_parser.add_argument('--position', required=True, help='面试岗位')
    create_parser.add_argument('--date', required=True, help='面试日期 (YYYY-MM-DD)')
    
    # 添加面试问答命令
    add_qa_parser = subparsers.add_parser('add_qa', help='添加面试问题和回答')
    add_qa_parser.add_argument('--interview_id', required=True, help='面试ID')
    add_qa_parser.add_argument('--question', required=True, help='面试问题')
    add_qa_parser.add_argument('--answer', required=True, help='面试回答')
    add_qa_parser.add_argument('--notes', help='备注信息')
    
    # 生成面试总结命令
    summary_parser = subparsers.add_parser('summarize', help='生成面试总结')
    summary_parser.add_argument('--interview_id', required=True, help='面试ID')
    
    # 分析回答命令
    analyze_parser = subparsers.add_parser('analyze_answer', help='分析面试回答质量')
    analyze_parser.add_argument('--interview_id', required=True, help='面试ID')
    analyze_parser.add_argument('--index', type=int, required=True, help='问题回答的索引')
    
    # 预测面试题目命令
    predict_parser = subparsers.add_parser('predict', help='预测面试题目')
    predict_parser.add_argument('--position', required=True, help='目标岗位')
    predict_parser.add_argument('--company', help='目标公司')
    predict_parser.add_argument('--resume_id', help='简历ID')
    
    # 列出面试记录命令
    list_parser = subparsers.add_parser('list_interviews', help='列出所有面试记录')
    
    # 聊天命令
    chat_parser = subparsers.add_parser('chat', help='与大模型聊天')
    chat_parser.add_argument('prompt', help='聊天提示')
    
    args = parser.parse_args()
    
    assistant = InterviewAssistant()
    
    if args.command == 'upload_resume':
        assistant.upload_resume(args.file_path)
    elif args.command == 'create_interview':
        assistant.create_interview(args.title, args.company, args.position, args.date)
    elif args.command == 'add_qa':
        assistant.add_interview_qa(args.interview_id, args.question, args.answer, args.notes)
    elif args.command == 'summarize':
        assistant.summarize_interview(args.interview_id)
    elif args.command == 'analyze_answer':
        assistant.analyze_answer(args.interview_id, args.index)
    elif args.command == 'predict':
        assistant.predict_questions(args.position, args.company, args.resume_id)
    elif args.command == 'list_interviews':
        assistant.list_interviews()
    elif args.command == 'chat':
        assistant.get_chat_response(args.prompt)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()