# 个人面试助手使用示例

from main import InterviewAssistant

def main():
    """展示如何使用个人面试助手的各个功能"""
    # 创建面试助手实例
    assistant = InterviewAssistant()
    
    print("===== 个人面试助手使用示例 =====")
    
    # 1. 上传简历（注意：需要提供实际的简历文件路径）
    # 这里使用示例，实际使用时需要替换为真实的文件路径
    # resume_id = assistant.upload_resume("path/to/your/resume.pdf")
    # print(f"简历ID: {resume_id}")
    
    # 为了演示，我们使用一个示例简历ID
    resume_id = "example_resume_id"
    
    # 2. 创建面试记录
    interview_id = assistant.create_interview(
        title="技术面试-后端开发工程师",
        company="示例科技有限公司",
        position="后端开发工程师",
        interview_date="2023-10-15"
    )
    
    # 3. 添加面试问题和回答
    if interview_id:
        assistant.add_interview_qa(
            interview_id=interview_id,
            question="请介绍一下你最熟悉的技术栈？",
            answer="我最熟悉的技术栈包括Python、Django、Flask等Web框架，以及MySQL、PostgreSQL数据库。我还熟悉RESTful API设计和微服务架构。",
            notes="这是一个基础问题，考察候选人的技术背景。"
        )
        
        assistant.add_interview_qa(
            interview_id=interview_id,
            question="请描述一个你遇到过的技术挑战，以及你是如何解决的？",
            answer="在我之前的项目中，我们遇到了数据库性能问题。我通过分析查询日志，优化了SQL查询，添加了合适的索引，并实现了缓存机制，最终将系统响应时间从5秒优化到了500毫秒以内。",
            notes="行为问题，考察候选人解决问题的能力。"
        )
    
    # 4. 生成面试总结
    if interview_id:
        summary = assistant.summarize_interview(interview_id)
    
    # 5. 分析面试回答质量
    if interview_id:
        analysis = assistant.analyze_answer(interview_id, 0)  # 分析第一个回答
    
    # 6. 预测面试题目
    predictions = assistant.predict_questions(
        target_position="后端开发工程师",
        target_company="示例科技有限公司",
        resume_id=resume_id
    )
    
    # 7. 列出所有面试记录
    interviews = assistant.list_interviews()
    
    # 8. 与大模型聊天
    response = assistant.get_chat_response("请给我一些Python面试的建议")
    
    print("\n===== 示例演示完成 =====")
    print("\n提示：")
    print("1. 实际使用时，请提供真实的简历文件路径")
    print("2. 可以通过命令行方式使用各个功能，例如：")
    print("   python main.py upload_resume your_resume.pdf")
    print("   python main.py create_interview --title '技术面试' --company '示例公司' --position '工程师' --date '2023-10-15'")
    print("3. 更多命令可以通过 python main.py -h 查看")

if __name__ == '__main__':
    main()