import os
import requests
from dotenv import load_dotenv, find_dotenv

# 精准加载.env文件
load_dotenv(find_dotenv(), override=True)
API_KEY = os.getenv("DASHSCOPE_API_KEY")
API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
MODEL_NAME = "qwen-turbo"


def _call_qwen_api(prompt: str) -> str:
    if not API_KEY or API_KEY == "your_dashscope_api_key_here":
        return "❌ 错误：请配置有效的千问API Key"

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": MODEL_NAME,
        "input": {"messages": [{"role": "user", "content": prompt}]},
        "parameters": {"result_format": "message", "temperature": 0.7, "max_tokens": 2000}
    }

    try:
        response = requests.post(API_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["output"]["choices"][0]["message"]["content"]
    except Exception as e:
        return f"❌ 错误：{str(e)}"


# 对外AI功能
def ai_summarize_note(content: str) -> str:
    return _call_qwen_api(f"请总结这段笔记，提炼核心要点：\n{content}")


def ai_extract_keywords(content: str) -> str:
    return _call_qwen_api(f"提取5-8个核心关键词，逗号分隔：\n{content}")


def ai_rewrite_note(content: str, mode: str) -> str:
    mode_map = {
        "续写": "续写以下内容，保持风格一致：\n",
        "润色": "润色以下内容，优化表达：\n",
        "扩写": "扩写以下内容，丰富细节：\n"
    }
    return _call_qwen_api(mode_map.get(mode, mode_map["润色"]) + content)


def ai_generate_mindmap(content: str) -> str:
    return _call_qwen_api(f"生成Markdown格式的思维导图结构：\n{content}")


def ai_chat_with_notes(content: str, question: str) -> str:
    return _call_qwen_api(f"基于笔记回答问题：\n笔记：{content}\n问题：{question}")