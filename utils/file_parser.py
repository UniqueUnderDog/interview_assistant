# 文件解析工具

import os
import re
from io import BytesIO

class FileParser:
    """文件解析类，支持多种格式的文件解析"""
    
    @staticmethod
    def parse_file(file_path, file_content=None):
        """解析文件内容
        
        Args:
            file_path (str): 文件路径
            file_content (bytes, optional): 文件内容，如果为None则从文件路径读取
            
        Returns:
            str: 解析后的文本内容
        """
        # 获取文件扩展名
        _, ext = os.path.splitext(file_path.lower())
        
        # 如果没有提供文件内容，则从文件路径读取
        if file_content is None:
            with open(file_path, 'rb') as f:
                file_content = f.read()
        
        # 根据文件扩展名选择不同的解析方法
        if ext == '.txt':
            return FileParser._parse_txt(file_content)
        elif ext == '.pdf':
            return FileParser._parse_pdf(file_content)
        elif ext in ['.doc', '.docx']:
            return FileParser._parse_doc(file_content, ext)
        else:
            # 未知格式，尝试作为文本处理
            try:
                return file_content.decode('utf-8', errors='ignore')
            except:
                return f"无法解析的文件格式: {ext}"
    
    @staticmethod
    def _parse_txt(file_content):
        """解析TXT文件
        
        Args:
            file_content (bytes): 文件内容
            
        Returns:
            str: 解析后的文本内容
        """
        try:
            # 尝试多种编码解析
            encodings = ['utf-8', 'gbk', 'latin-1']
            for encoding in encodings:
                try:
                    return file_content.decode(encoding)
                except UnicodeDecodeError:
                    continue
            # 如果所有编码都失败，使用ignore模式
            return file_content.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"解析TXT文件失败: {e}")
            return f"解析TXT文件失败: {str(e)}"
    
    @staticmethod
    def _parse_pdf(file_content):
        """解析PDF文件
        
        Args:
            file_content (bytes): 文件内容
            
        Returns:
            str: 解析后的文本内容
        """
        try:
            # 尝试使用pdfplumber
            try:
                import pdfplumber
                with pdfplumber.open(BytesIO(file_content)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + '\n'
                    return text if text else "PDF文件中未提取到文本内容"
            except ImportError:
                # 如果pdfplumber不可用，尝试使用PyPDF2
                try:
                    from PyPDF2 import PdfReader
                    reader = PdfReader(BytesIO(file_content))
                    text = ""
                    for page in reader.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + '\n'
                    return text if text else "PDF文件中未提取到文本内容"
                except ImportError:
                    return "解析PDF文件需要安装pdfplumber或PyPDF2库"
                except Exception as e:
                    return f"使用PyPDF2解析PDF文件失败: {str(e)}"
            except Exception as e:
                return f"使用pdfplumber解析PDF文件失败: {str(e)}"
        except Exception as e:
            print(f"解析PDF文件失败: {e}")
            return f"解析PDF文件失败: {str(e)}"
    
    @staticmethod
    def _parse_doc(file_content, ext):
        """解析Word文件(.doc或.docx)
        
        Args:
            file_content (bytes): 文件内容
            ext (str): 文件扩展名
            
        Returns:
            str: 解析后的文本内容
        """
        try:
            if ext == '.docx':
                # 解析.docx文件
                try:
                    import docx
                    doc = docx.Document(BytesIO(file_content))
                    text = ""
                    for paragraph in doc.paragraphs:
                        if paragraph.text:
                            text += paragraph.text + '\n'
                    return text if text else "DOCX文件中未提取到文本内容"
                except ImportError:
                    return "解析DOCX文件需要安装python-docx库"
                except Exception as e:
                    return f"解析DOCX文件失败: {str(e)}"
            else:  # .doc格式
                # 解析.doc文件
                try:
                    import pywin32  # 仅Windows系统可用
                    import pythoncom
                    pythoncom.CoInitialize()
                    
                    # 保存临时文件
                    temp_path = os.path.join(os.environ.get('TEMP', '.'), f"temp_{os.urandom(8).hex()}.doc")
                    with open(temp_path, 'wb') as f:
                        f.write(file_content)
                    
                    # 使用Word COM对象打开文件
                    import win32com.client
                    word = win32com.client.Dispatch("Word.Application")
                    word.Visible = False
                    doc = word.Documents.Open(os.path.abspath(temp_path))
                    
                    # 提取文本
                    text = doc.Content.Text
                    
                    # 关闭文档和Word应用
                    doc.Close(False)
                    word.Quit()
                    
                    # 删除临时文件
                    os.unlink(temp_path)
                    
                    pythoncom.CoUninitialize()
                    
                    return text if text else "DOC文件中未提取到文本内容"
                except ImportError:
                    return "解析DOC文件需要安装pywin32库，且仅在Windows系统可用"
                except Exception as e:
                    return f"解析DOC文件失败: {str(e)}"
        except Exception as e:
            print(f"解析Word文件失败: {e}")
            return f"解析Word文件失败: {str(e)}"
    
    @staticmethod
    def clean_text(text):
        """清理文本内容
        
        Args:
            text (str): 原始文本
            
        Returns:
            str: 清理后的文本
        """
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text)
        # 移除不可见字符
        text = re.sub(r'[\x00-\x08\x0b-\x0c\x0e-\x1f]', '', text)
        # 去除首尾空白
        text = text.strip()
        return text