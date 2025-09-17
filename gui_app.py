# 个人面试助手GUI界面

import os
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from datetime import datetime
from main import InterviewAssistant
from config import LLM_CONFIG, SUPPORTED_RESUME_FORMATS
from services.llm_service import LLMService

class InterviewAssistantGUI:
    """个人面试助手GUI界面"""
    
    def __init__(self, root):
        """初始化GUI界面"""
        self.root = root
        self.root.title("个人面试助手")
        self.root.geometry("1000x600")
        
        # 初始化面试助手
        self.assistant = InterviewAssistant()
        self.llm_service = LLMService()
        
        # 创建标签页
        self.tab_control = ttk.Notebook(root)
        
        # 创建各个标签页
        self.resume_tab = ttk.Frame(self.tab_control)
        self.interview_tab = ttk.Frame(self.tab_control)
        self.model_tab = ttk.Frame(self.tab_control)
        self.summary_tab = ttk.Frame(self.tab_control)
        
        # 添加标签页到标签控件
        self.tab_control.add(self.resume_tab, text="简历管理")
        self.tab_control.add(self.interview_tab, text="面试管理")
        self.tab_control.add(self.summary_tab, text="面试总结")
        self.tab_control.add(self.model_tab, text="模型配置")
        
        # 显示标签控件
        self.tab_control.pack(expand=1, fill="both")
        
        # 初始化各个标签页
        self._init_resume_tab()
        self._init_interview_tab()
        self._init_summary_tab()
        self._init_model_tab()
        
        # 存储当前选中的项目
        self.current_resume_id = None
        self.current_interview_id = None
        
        # 加载已有数据
        self._load_resumes()
        self._load_interviews()
    
    def _init_resume_tab(self):
        """初始化简历管理标签页"""
        # 创建上半部分（上传区域）
        upload_frame = ttk.LabelFrame(self.resume_tab, text="上传简历")
        upload_frame.pack(fill="x", padx=10, pady=10)

        # 按钮区域
        buttons_frame = ttk.Frame(upload_frame)
        buttons_frame.pack(pady=10)
        
        # 上传按钮
        self.upload_button = ttk.Button(buttons_frame, text="选择文件", command=self._upload_resume)
        self.upload_button.pack(side="left", padx=10)
        
        # 创建简历按钮
        self.create_resume_button = ttk.Button(buttons_frame, text="创建简历", command=self._create_resume)
        self.create_resume_button.pack(side="left", padx=10)

        # 文件路径显示
        self.file_path_var = tk.StringVar()
        self.file_path_label = ttk.Label(upload_frame, textvariable=self.file_path_var, wraplength=900)
        self.file_path_label.pack(padx=10, pady=5)
        
        # 下半部分（简历列表和信息）
        bottom_frame = ttk.Frame(self.resume_tab)
        bottom_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 简历列表
        list_frame = ttk.LabelFrame(bottom_frame, text="已上传简历")
        list_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 简历列表
        self.resume_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=30)
        self.resume_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.resume_listbox.bind("<<ListboxSelect>>", self._on_resume_select)
        
        # 绑定滚动条
        scrollbar.config(command=self.resume_listbox.yview)
        
        # 简历信息展示
        info_frame = ttk.LabelFrame(bottom_frame, text="简历信息")
        info_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        # 信息文本框
        self.resume_info_text = scrolledtext.ScrolledText(info_frame, wrap=tk.WORD)
        self.resume_info_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.resume_info_text.config(state=tk.DISABLED)
    
    def _init_interview_tab(self):
        """初始化面试管理标签页"""
        # 创建左侧部分（面试列表）
        left_frame = ttk.Frame(self.interview_tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # 面试操作按钮
        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.pack(fill="x", padx=5, pady=5)
        
        self.create_interview_button = ttk.Button(buttons_frame, text="创建面试", command=self._create_interview)
        self.create_interview_button.pack(side="left", padx=5)
        
        self.upload_interview_button = ttk.Button(buttons_frame, text="上传面试", command=self._upload_interview)
        self.upload_interview_button.pack(side="left", padx=5)
        
        # 面试列表
        list_frame = ttk.LabelFrame(left_frame, text="已创建面试")
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 面试列表
        self.interview_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=40)
        self.interview_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.interview_listbox.bind("<<ListboxSelect>>", self._on_interview_select)
        
        # 绑定滚动条
        scrollbar.config(command=self.interview_listbox.yview)
        
        # 创建右侧部分（面试详情）
        right_frame = ttk.Frame(self.interview_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # 面试详情标签
        details_frame = ttk.LabelFrame(right_frame, text="面试详情")
        details_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 面试信息
        info_frame = ttk.Frame(details_frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        
        # 面试标题
        ttk.Label(info_frame, text="标题：").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.interview_title_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.interview_title_var).grid(row=0, column=1, sticky="w", padx=5, pady=2)
        
        # 公司名称
        ttk.Label(info_frame, text="公司：").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.interview_company_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.interview_company_var).grid(row=1, column=1, sticky="w", padx=5, pady=2)
        
        # 面试岗位
        ttk.Label(info_frame, text="岗位：").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.interview_position_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.interview_position_var).grid(row=2, column=1, sticky="w", padx=5, pady=2)
        
        # 面试日期
        ttk.Label(info_frame, text="日期：").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.interview_date_var = tk.StringVar()
        ttk.Label(info_frame, textvariable=self.interview_date_var).grid(row=3, column=1, sticky="w", padx=5, pady=2)
        
        # 面试问答内容
        qa_frame = ttk.LabelFrame(details_frame, text="面试问答")
        qa_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.qa_text = scrolledtext.ScrolledText(qa_frame, wrap=tk.WORD)
        self.qa_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.qa_text.config(state=tk.DISABLED)
    
    def _init_summary_tab(self):
        """初始化面试总结标签页"""
        # 左侧部分（面试选择）
        left_frame = ttk.Frame(self.summary_tab)
        left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # 面试选择标签
        select_frame = ttk.LabelFrame(left_frame, text="选择面试")
        select_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(select_frame)
        scrollbar.pack(side="right", fill="y")
        
        # 面试列表
        self.summary_interview_listbox = tk.Listbox(select_frame, yscrollcommand=scrollbar.set, width=40)
        self.summary_interview_listbox.pack(fill="both", expand=True, padx=5, pady=5)
        self.summary_interview_listbox.bind("<<ListboxSelect>>", self._on_summary_interview_select)
        
        # 绑定滚动条
        scrollbar.config(command=self.summary_interview_listbox.yview)
        
        # 总结按钮
        self.generate_summary_button = ttk.Button(left_frame, text="生成总结", command=self._generate_summary, state=tk.DISABLED)
        self.generate_summary_button.pack(pady=10)
        
        # 右侧部分（总结内容）
        right_frame = ttk.Frame(self.summary_tab)
        right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # 总结内容标签
        content_frame = ttk.LabelFrame(right_frame, text="面试总结")
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # 总结文本框
        self.summary_text = scrolledtext.ScrolledText(content_frame, wrap=tk.WORD)
        self.summary_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.summary_text.config(state=tk.DISABLED)
    
    def _init_model_tab(self):
        """初始化模型配置标签页"""
        # 创建配置框架
        config_frame = ttk.LabelFrame(self.model_tab, text="LLM模型配置")
        config_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # API密钥
        api_frame = ttk.Frame(config_frame)
        api_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(api_frame, text="API密钥：").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.api_key_var = tk.StringVar(value=LLM_CONFIG['api_key'])
        self.api_key_entry = ttk.Entry(api_frame, textvariable=self.api_key_var, width=60, show="*")
        self.api_key_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 模型选择
        model_frame = ttk.Frame(config_frame)
        model_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Label(model_frame, text="模型选择：").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.model_var = tk.StringVar(value=LLM_CONFIG['model'])
        self.model_combobox = ttk.Combobox(model_frame, textvariable=self.model_var, width=57)
        # 设置常见模型选项
        self.model_combobox['values'] = (
            'doubao-seed-1-6-thinking-250715',
            'doubao-pro',
            'doubao-lite',
            'other'
        )
        self.model_combobox.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 保存按钮
        self.save_config_button = ttk.Button(config_frame, text="保存配置", command=self._save_model_config)
        self.save_config_button.pack(pady=20)
        
        # 测试连接按钮
        self.test_connection_button = ttk.Button(config_frame, text="测试连接", command=self._test_model_connection)
        self.test_connection_button.pack(pady=10)
    
    def _upload_resume(self):
        """上传简历文件"""
        # 正确格式应该是使用分号分隔的扩展名列表
        file_pattern = ";".join(["*" + ext for ext in SUPPORTED_RESUME_FORMATS])
        file_types = [("支持的文件格式", file_pattern)]
        file_path = filedialog.askopenfilename(title="选择简历文件", filetypes=file_types)
        
        if file_path:
            self.file_path_var.set(file_path)
            
            try:
                # 创建进度窗口
                progress_window = tk.Toplevel(self.root)
                progress_window.title("处理中")
                progress_window.geometry("300x100")
                progress_window.transient(self.root)
                progress_window.grab_set()
                
                # 居中显示
                progress_window.update_idletasks()
                width = progress_window.winfo_width()
                height = progress_window.winfo_height()
                x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
                y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
                progress_window.geometry(f"{width}x{height}+{x}+{y}")
                
                # 进度标签
                progress_label = ttk.Label(progress_window, text="正在上传并分析简历，请稍候...")
                progress_label.pack(pady=20)
                
                # 使用线程处理耗时操作
                def process_resume():
                    try:
                        # 上传简历
                        resume_id = self.assistant.upload_resume(file_path)
                        
                        # 在主线程中更新GUI
                        self.root.after(0, lambda: self._update_gui_after_resume_upload(progress_window, resume_id))
                    except Exception as e:
                        error_message = str(e)
                        self.root.after(0, lambda: self._show_upload_error(progress_window, error_message))
                
                # 启动线程
                import threading
                thread = threading.Thread(target=process_resume)
                thread.daemon = True
                thread.start()
            except Exception as e:
                messagebox.showerror("错误", f"上传过程中发生错误：{str(e)}")
                
    def _update_gui_after_resume_upload(self, progress_window, resume_id):
        """简历上传成功后更新GUI"""
        # 关闭进度窗口
        progress_window.destroy()
        
        # 重新加载简历列表
        self._load_resumes()
        
        # 显示成功消息
        if resume_id:
            messagebox.showinfo("成功", f"简历上传成功！简历ID: {resume_id}")
        else:
            messagebox.showerror("失败", "简历上传失败")
            
    def _show_upload_error(self, progress_window, error_message):
        """显示上传错误"""
        # 关闭进度窗口
        progress_window.destroy()
        
        # 显示错误消息
        messagebox.showerror("错误", f"上传过程中发生错误：{error_message}")
    
    def _load_resumes(self):
        """加载简历列表"""
        # 清空列表
        self.resume_listbox.delete(0, tk.END)
        
        # 从文件系统加载简历信息
        from models.resume import Resume
        try:
            # 获取所有简历文件
            import os
            from config import RESUMES_DIR
            resume_files = [f for f in os.listdir(RESUMES_DIR) if os.path.isfile(os.path.join(RESUMES_DIR, f))]
            
            # 添加到列表
            for file_name in resume_files:
                resume_id = os.path.splitext(file_name)[0]
                # 显示文件名而不是ID，更友好
                self.resume_listbox.insert(tk.END, file_name)
        except Exception as e:
            print(f"加载简历列表失败: {e}")
    
    def _on_resume_select(self, event):
        """处理简历选择事件"""
        selection = self.resume_listbox.curselection()
        if selection:
            index = selection[0]
            file_name = self.resume_listbox.get(index)
            resume_id = os.path.splitext(file_name)[0]

            # 保存当前选中的简历ID
            self.current_resume_id = resume_id

            # 加载简历信息
            try:
                from models.resume import Resume
                resume = Resume().load(resume_id)

                # 显示简历信息
                self.resume_info_text.config(state=tk.NORMAL)
                self.resume_info_text.delete(1.0, tk.END)

                # 格式化简历信息
                info_text = f"文件路径: {resume.file_path}\n"
                info_text += f"上传时间: {resume.upload_time}\n\n"
                info_text += "提取的信息:\n"

                for key, value in resume.user_info.items():
                    info_text += f"{key}: {value}\n"

                self.resume_info_text.insert(tk.END, info_text)
                self.resume_info_text.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror("错误", f"加载简历信息失败：{str(e)}")
                
    def _create_resume(self):
        """创建新的简历"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("创建简历")
        dialog.geometry("600x500")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # 设置对话框居中
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 创建滚动区域
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 简历基本信息
        # 姓名
        name_frame = ttk.Frame(scrollable_frame)
        name_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(name_frame, text="姓名：", width=15).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        name_var = tk.StringVar()
        name_entry = ttk.Entry(name_frame, textvariable=name_var, width=40)
        name_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 联系方式
        contact_frame = ttk.Frame(scrollable_frame)
        contact_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(contact_frame, text="联系方式：", width=15).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        contact_var = tk.StringVar()
        contact_entry = ttk.Entry(contact_frame, textvariable=contact_var, width=40)
        contact_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 邮箱
        email_frame = ttk.Frame(scrollable_frame)
        email_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(email_frame, text="邮箱：", width=15).grid(row=0, column=0, sticky="w", padx=5, pady=5)
        email_var = tk.StringVar()
        email_entry = ttk.Entry(email_frame, textvariable=email_var, width=40)
        email_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 学历背景
        education_frame = ttk.Frame(scrollable_frame)
        education_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(education_frame, text="学历背景：", width=15).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        education_var = tk.StringVar()
        education_text = scrolledtext.ScrolledText(education_frame, width=40, height=3, wrap=tk.WORD)
        education_text.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 工作经历
        work_frame = ttk.Frame(scrollable_frame)
        work_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(work_frame, text="工作经历：", width=15).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        work_text = scrolledtext.ScrolledText(work_frame, width=40, height=5, wrap=tk.WORD)
        work_text.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 项目经验
        project_frame = ttk.Frame(scrollable_frame)
        project_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(project_frame, text="项目经验：", width=15).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        project_text = scrolledtext.ScrolledText(project_frame, width=40, height=5, wrap=tk.WORD)
        project_text.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 专业证书
        cert_frame = ttk.Frame(scrollable_frame)
        cert_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(cert_frame, text="专业证书：", width=15).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        cert_text = scrolledtext.ScrolledText(cert_frame, width=40, height=3, wrap=tk.WORD)
        cert_text.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 学术著作
        pub_frame = ttk.Frame(scrollable_frame)
        pub_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(pub_frame, text="学术著作：", width=15).grid(row=0, column=0, sticky="nw", padx=5, pady=5)
        pub_text = scrolledtext.ScrolledText(pub_frame, width=40, height=3, wrap=tk.WORD)
        pub_text.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=10)
        
        def save_resume():
            # 收集简历信息
            user_info = {
                "姓名": name_var.get().strip() or "未提供",
                "联系方式": contact_var.get().strip() or "未提供",
                "邮箱": email_var.get().strip() or "未提供",
                "学历背景": education_text.get(1.0, tk.END).strip() or "未提供",
                "工作经历": work_text.get(1.0, tk.END).strip() or "未提供",
                "项目经验": project_text.get(1.0, tk.END).strip() or "未提供",
                "专业证书": cert_text.get(1.0, tk.END).strip() or "未提供",
                "学术著作": pub_text.get(1.0, tk.END).strip() or "未提供"
            }
            
            try:
                # 创建符合Resume类数据结构的JSON
                from models.resume import Resume
                from utils.file_utils import FileUtils
                from config import RESUMES_DIR
                
                # 生成简历ID
                resume_id = FileUtils.generate_unique_filename()
                
                # 创建简历对象
                resume = Resume(resume_id=resume_id, user_info=user_info)
                
                # 生成JSON内容
                resume_content = json.dumps(resume.to_dict(), ensure_ascii=False, indent=2).encode('utf-8')
                
                # 保存为JSON文件
                file_name = f"{resume_id}.json"
                file_path = os.path.join(RESUMES_DIR, file_name)
                
                with open(file_path, 'wb') as f:
                    f.write(resume_content)
                
                # 更新简历对象的文件路径
                resume.file_path = file_path
                
                messagebox.showinfo("成功", f"简历创建成功！简历ID: {resume_id}")
                dialog.destroy()
                self._load_resumes()
            except Exception as e:
                messagebox.showerror("错误", f"创建简历时发生错误：{str(e)}")
        
        save_button = ttk.Button(button_frame, text="保存", command=save_resume)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy)
        cancel_button.pack(side="left", padx=10)
    
    def _create_interview(self):
        """创建新的面试记录"""
        # 创建对话框
        dialog = tk.Toplevel(self.root)
        dialog.title("创建面试")
        dialog.geometry("400x300")
        dialog.resizable(False, False)
        dialog.grab_set()
        
        # 设置对话框居中
        dialog.update_idletasks()
        width = dialog.winfo_width()
        height = dialog.winfo_height()
        x = (dialog.winfo_screenwidth() // 2) - (width // 2)
        y = (dialog.winfo_screenheight() // 2) - (height // 2)
        dialog.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
        # 面试标题
        title_frame = ttk.Frame(dialog)
        title_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(title_frame, text="面试标题：").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        title_var = tk.StringVar()
        title_entry = ttk.Entry(title_frame, textvariable=title_var, width=30)
        title_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 公司名称
        company_frame = ttk.Frame(dialog)
        company_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(company_frame, text="公司名称：").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        company_var = tk.StringVar()
        company_entry = ttk.Entry(company_frame, textvariable=company_var, width=30)
        company_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 面试岗位
        position_frame = ttk.Frame(dialog)
        position_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(position_frame, text="面试岗位：").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        position_var = tk.StringVar()
        position_entry = ttk.Entry(position_frame, textvariable=position_var, width=30)
        position_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 面试日期
        date_frame = ttk.Frame(dialog)
        date_frame.pack(fill="x", padx=20, pady=10)
        ttk.Label(date_frame, text="面试日期：").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        # 默认使用今天的日期
        today = datetime.now().strftime('%Y-%m-%d')
        date_var = tk.StringVar(value=today)
        date_entry = ttk.Entry(date_frame, textvariable=date_var, width=30)
        date_entry.grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        # 按钮
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def save_interview():
            title = title_var.get().strip()
            company = company_var.get().strip()
            position = position_var.get().strip()
            interview_date = date_var.get().strip()
            
            if not title:
                messagebox.showwarning("警告", "请输入面试标题")
                return
            
            # 创建面试
            interview_id = self.assistant.create_interview(title, company, position, interview_date)
            
            if interview_id:
                messagebox.showinfo("成功", f"面试记录创建成功！面试ID: {interview_id}")
                dialog.destroy()
                self._load_interviews()
                self._load_summary_interviews()
            else:
                messagebox.showerror("失败", "创建面试记录失败")
        
        save_button = ttk.Button(button_frame, text="保存", command=save_interview)
        save_button.pack(side="left", padx=10)
        
        cancel_button = ttk.Button(button_frame, text="取消", command=dialog.destroy)
        cancel_button.pack(side="left", padx=10)
    
    def _upload_interview(self):
        """上传面试文件（JSON格式）"""
        # 明确设置JSON文件过滤格式
        file_types = [("JSON文件", "*.json")]
        file_path = filedialog.askopenfilename(title="选择面试文件", filetypes=file_types)
        
        if file_path:
            try:
                # 读取JSON文件
                with open(file_path, 'r', encoding='utf-8') as f:
                    interview_data = json.load(f)
                
                # 验证必要字段
                required_fields = ['title', 'company', 'position', 'interview_date']
                for field in required_fields:
                    if field not in interview_data:
                        raise ValueError(f"缺少必要字段: {field}")
                
                # 创建面试对象并保存
                from models.interview import Interview
                interview = Interview(
                    title=interview_data['title'],
                    company=interview_data['company'],
                    position=interview_data['position'],
                    interview_date=interview_data['interview_date'],
                    questions_answers=interview_data.get('questions_answers', [])
                )
                interview.save()
                
                messagebox.showinfo("成功", f"面试上传成功！面试ID: {interview.interview_id}")
                self._load_interviews()
                self._load_summary_interviews()
            except json.JSONDecodeError:
                messagebox.showerror("错误", "无效的JSON文件")
            except Exception as e:
                messagebox.showerror("错误", f"上传过程中发生错误：{str(e)}")
    
    def _load_interviews(self):
        """加载面试列表"""
        # 清空列表
        self.interview_listbox.delete(0, tk.END)
        
        # 加载面试记录
        from models.interview import Interview
        interviews = Interview.list_interviews()
        
        # 存储面试对象，用于快速访问
        self.interviews_dict = {}
        
        # 添加到列表
        for interview in interviews:
            display_text = f"{interview.title} - {interview.company} - {interview.position}"
            self.interview_listbox.insert(tk.END, display_text)
            # 使用索引作为键
            self.interviews_dict[len(self.interviews_dict)] = interview
    
    def _on_interview_select(self, event):
        """处理面试选择事件"""
        selection = self.interview_listbox.curselection()
        if selection:
            index = selection[0]
            interview = self.interviews_dict.get(index)
            
            if interview:
                # 保存当前选中的面试ID
                self.current_interview_id = interview.interview_id
                
                # 更新面试详情
                self.interview_title_var.set(interview.title)
                self.interview_company_var.set(interview.company)
                self.interview_position_var.set(interview.position)
                self.interview_date_var.set(interview.interview_date)
                
                # 显示面试问答
                self.qa_text.config(state=tk.NORMAL)
                self.qa_text.delete(1.0, tk.END)
                
                if interview.questions_answers:
                    for i, qa in enumerate(interview.questions_answers):
                        self.qa_text.insert(tk.END, f"问题 {i+1}: {qa['question']}\n")
                        self.qa_text.insert(tk.END, f"回答 {i+1}: {qa['answer']}\n")
                        if qa.get('notes'):
                            self.qa_text.insert(tk.END, f"备注: {qa['notes']}\n")
                        self.qa_text.insert(tk.END, "="*50 + "\n")
                else:
                    self.qa_text.insert(tk.END, "暂无面试问答内容")
                
                self.qa_text.config(state=tk.DISABLED)
    
    def _load_summary_interviews(self):
        """加载总结标签页的面试列表"""
        # 清空列表
        self.summary_interview_listbox.delete(0, tk.END)
        
        # 加载面试记录
        from models.interview import Interview
        interviews = Interview.list_interviews()
        
        # 存储面试对象，用于快速访问
        self.summary_interviews_dict = {}
        
        # 添加到列表
        for interview in interviews:
            display_text = f"{interview.title} - {interview.company} - {interview.position}"
            self.summary_interview_listbox.insert(tk.END, display_text)
            # 使用索引作为键
            self.summary_interviews_dict[len(self.summary_interviews_dict)] = interview
    
    def _on_summary_interview_select(self, event):
        """处理总结标签页的面试选择事件"""
        selection = self.summary_interview_listbox.curselection()
        if selection:
            index = selection[0]
            interview = self.summary_interviews_dict.get(index)
            
            if interview:
                # 保存当前选中的面试ID
                self.current_summary_interview_id = interview.interview_id
                # 启用生成总结按钮
                self.generate_summary_button.config(state=tk.NORMAL)
                
                # 检查是否已有总结
                self.summary_text.config(state=tk.NORMAL)
                self.summary_text.delete(1.0, tk.END)
                
                if interview.summary:
                    self.summary_text.insert(tk.END, interview.summary)
                else:
                    self.summary_text.insert(tk.END, "暂无面试总结，请点击'生成总结'按钮")
                
                self.summary_text.config(state=tk.DISABLED)
        else:
            # 禁用生成总结按钮
            self.generate_summary_button.config(state=tk.DISABLED)
    
    def _generate_summary(self):
        """生成面试总结"""
        if hasattr(self, 'current_summary_interview_id') and self.current_summary_interview_id:
            try:
                # 显示加载中提示
                self.summary_text.config(state=tk.NORMAL)
                self.summary_text.delete(1.0, tk.END)
                self.summary_text.insert(tk.END, "正在生成面试总结，请稍候...")
                self.summary_text.update()
                
                # 调用生成总结功能
                summary = self.assistant.summarize_interview(self.current_summary_interview_id)
                
                if summary:
                    self.summary_text.delete(1.0, tk.END)
                    self.summary_text.insert(tk.END, summary)
                else:
                    self.summary_text.delete(1.0, tk.END)
                    self.summary_text.insert(tk.END, "生成总结失败")
                
                self.summary_text.config(state=tk.DISABLED)
            except Exception as e:
                self.summary_text.config(state=tk.NORMAL)
                self.summary_text.delete(1.0, tk.END)
                self.summary_text.insert(tk.END, f"生成总结时发生错误：{str(e)}")
                self.summary_text.config(state=tk.DISABLED)
    
    def _save_model_config(self):
        """保存模型配置"""
        try:
            # 读取配置
            api_key = self.api_key_var.get().strip()
            model = self.model_var.get().strip()
            
            # 更新配置文件
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.py')
            
            # 读取现有配置
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # 更新API密钥
            import re
            config_content = re.sub(r"'api_key':\s*'.*?',", f"'api_key': '{api_key}',", config_content)
            # 更新模型
            config_content = re.sub(r"'model':\s*'.*?',", f"'model': '{model}',", config_content)
            
            # 写回配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            # 更新环境变量
            os.environ['ARK_API_KEY'] = api_key
            
            # 更新当前服务的配置
            self.llm_service.api_key = api_key
            self.llm_service.model = model
            self.llm_service.client = self.llm_service._init_client()
            
            messagebox.showinfo("成功", "模型配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存配置时发生错误：{str(e)}")
    
    def _test_model_connection(self):
        """测试模型连接"""
        try:
            # 显示测试中提示
            test_window = tk.Toplevel(self.root)
            test_window.title("测试连接")
            test_window.geometry("300x100")
            test_window.resizable(False, False)
            test_window.grab_set()
            
            # 设置对话框居中
            test_window.update_idletasks()
            width = test_window.winfo_width()
            height = test_window.winfo_height()
            x = (test_window.winfo_screenwidth() // 2) - (width // 2)
            y = (test_window.winfo_screenheight() // 2) - (height // 2)
            test_window.geometry('{}x{}+{}+{}'.format(width, height, x, y))
            
            ttk.Label(test_window, text="正在测试模型连接，请稍候...").pack(pady=20)
            test_window.update()
            
            # 发送测试请求
            test_prompt = "你好"
            response = self.llm_service.generate_response(test_prompt)
            
            # 关闭测试窗口
            test_window.destroy()
            
            # 显示测试结果
            if response and not response.startswith("错误:"):
                messagebox.showinfo("成功", "模型连接测试成功！")
            else:
                messagebox.showerror("失败", f"模型连接测试失败：{response}")
        except Exception as e:
            messagebox.showerror("错误", f"测试连接时发生错误：{str(e)}")

if __name__ == "__main__":
    # 创建主窗口
    root = tk.Tk()
    # 创建GUI应用
    app = InterviewAssistantGUI(root)
    # 运行主循环
    root.mainloop()