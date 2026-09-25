from smolagents import CodeAgent, LiteLLMModel, tool
from dotenv import load_dotenv
import os
from search import search        # 复用你重构好的函数

load_dotenv()

@tool
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """用于在知识库/数据库中搜索与用户问题相关的参考资料。
    当你需要回答关于专业知识、特定文档内容（例如 OSI 模型）的问题时，请调用此工具。
    Args:
        query: 用户输入的具体搜索问题或提取出的核心关键词。
        top_k: 需要返回的最相关的文本段落数量，默认为 3。
    """
    return search(query, top_k)

model = LiteLLMModel(model_id="gemini/gemini-2.5-flash", api_key=os.environ["GEMINI_API_KEY"])

agent = CodeAgent(tools=[search_knowledge_base], model=model)   # 填：把你的工具挂上去

result = agent.run("你好，你是谁？")
print(result)