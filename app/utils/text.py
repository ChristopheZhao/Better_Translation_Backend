import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from html import unescape

class TextProcessor:
    @staticmethod
    def clean_html(html_content: str) -> str:
        """清理HTML内容，保留必要的格式"""
        soup = BeautifulSoup(html_content, 'html.parser')
        # 移除脚本和样式
        for script in soup(['script', 'style']):
            script.decompose()
        return soup.get_text()
    
    @staticmethod
    def extract_paragraphs(text: str) -> List[str]:
        """提取段落，保持格式"""
        paragraphs = re.split(r'\n\s*\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    @staticmethod
    def is_sentence_complete(text: str) -> bool:
        """检查句子是否完整"""
        if not text:
            return False
        
        end_marks = '.!?。！？'
        # 修改这里的引号使用
        quote_pairs = {
            '"': '"',
            "'": "'",
            '(': ')',
            '[': ']',
            '{': '}'
        }
        stack = []
        
        for char in text:
            if char in quote_pairs.keys():
                stack.append(char)
            elif char in quote_pairs.values():
                if not stack:
                    return False
                if char != quote_pairs[stack[-1]]:
                    return False
                stack.pop()
        
        return len(stack) == 0 and text[-1] in end_marks
        stack = []
        
        for char in text:
            if char in quote_pairs.keys():
                stack.append(char)
            elif char in quote_pairs.values():
                if not stack:
                    return False
                if char != quote_pairs[stack[-1]]:
                    return False
                stack.pop()
        
        return len(stack) == 0 and text[-1] in end_marks
    
    @staticmethod
    def merge_translations(original: str, translated: str) -> str:
        """合并原文和翻译，保持格式"""
        return f"{translated}\n\n原文：\n{original}"
    
    @staticmethod
    def detect_language(text: str) -> str:
        """简单的语言检测"""
        # 这里可以集成更复杂的语言检测库
        chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
        english_chars = re.findall(r'[a-zA-Z]', text)
        
        if len(chinese_chars) > len(english_chars):
            return 'zh'
        return 'en'

class MarkdownProcessor:
    @staticmethod
    def extract_code_blocks(markdown: str) -> tuple[str, List[str]]:
        """提取代码块，返回处理后的文本和代码块列表"""
        code_blocks = []
        
        def replace_code_block(match):
            code = match.group(1)
            code_blocks.append(code)
            return f"[CODE_BLOCK_{len(code_blocks)-1}]"
        
        # 替换代码块
        processed_text = re.sub(
            r'```[\w]*\n(.*?)```',
            replace_code_block,
            markdown,
            flags=re.DOTALL
        )
        
        return processed_text, code_blocks
    
    @staticmethod
    def restore_code_blocks(text: str, code_blocks: List[str]) -> str:
        """还原代码块"""
        for i, code in enumerate(code_blocks):
            text = text.replace(
                f"[CODE_BLOCK_{i}]",
                f"```\n{code}```"
            )
        return text