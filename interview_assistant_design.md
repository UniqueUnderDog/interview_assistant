# 个人面试助手后端模块设计

## 项目概述
设计一个个人面试助手的后端模块，用于帮助用户管理面试相关信息，并提供AI辅助功能。

## 功能需求
1. 上传简历，储存在本地并在需要的时候读取
2. 上传本地每一次面试的题目，储存每一次面试的题目以及回答
3. 支持利用模型对单个问题以及整场面试进行总结
4. 上传本地面试时间以及面试岗位，结合项目以及过往面试，预测面试题目并推荐准备的题目

## 项目结构
```
interview_assistant/
├── main.py                 # 主程序入口
├── config.py               # 配置文件
├── models/
│   ├── __init__.py
│   ├── resume.py           # 简历管理类
│   ├── interview.py        # 面试管理类
│   └── prediction.py       # 面试预测类
├── services/
│   ├── __init__.py
│   ├── storage.py          # 本地存储服务
│   ├── llm_service.py      # 大语言模型服务
│   ├── summary_service.py  # 总结服务
│   └── prediction_service.py # 预测服务
├── utils/
│   ├── __init__.py
│   ├── file_utils.py       # 文件处理工具
│   └── text_processing.py  # 文本处理工具
└── data/
    ├── resumes/            # 简历存储目录
    └── interviews/         # 面试数据存储目录
```

## 核心模块设计

### 1. 数据模型设计

#### Resume 模型
- 属性：resume_id, file_path, upload_time, user_info (姓名、联系方式等提取信息)
- 方法：save(), load(), extract_info()

#### Interview 模型
- 属性：interview_id, title, company, position, interview_date, questions_answers, summary
- 方法：save(), load(), add_question_answer(), generate_summary()

#### Prediction 模型
- 属性：prediction_id, target_position, target_company, resume_id, recommended_questions
- 方法：generate_predictions(), save(), load()

### 2. 服务设计

#### 存储服务 (StorageService)
- 功能：管理本地文件的存储和读取
- 方法：save_file(), read_file(), delete_file(), list_files()

#### 大语言模型服务 (LLMService)
- 功能：封装火山引擎API调用，提供统一的接口
- 方法：generate_response(), summarize_text(), extract_info_from_text()

#### 总结服务 (SummaryService)
- 功能：利用LLM服务对面试问题和整场面试进行总结
- 方法：summarize_question_answer(), summarize_interview()

#### 预测服务 (PredictionService)
- 功能：基于简历和岗位信息预测面试题目
- 方法：predict_questions(), recommend_study_topics()

### 3. 数据存储设计
- 简历以PDF/Word格式存储在本地文件系统
- 面试数据以JSON格式存储
- 可以考虑使用SQLite进行结构化数据管理

## 接口设计
- RESTful API 或命令行接口
- 支持文件上传/下载
- 提供数据查询和统计功能

## 技术栈
- Python 3.9+
- 火山引擎方舟大模型API
- 文件操作和JSON处理
- 可选：FastAPI (如果需要Web接口)