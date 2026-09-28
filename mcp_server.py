from mcp.server.mcpserver import MCPServer
from search import search        # 复用 search()，和 rag_agent.py 一样

# 注意：stdio 模式下 stdout 就是协议通道，这个进程里不能 print，调试信息写 stderr
mcp = MCPServer("rag-exam")


@mcp.tool()
def search_knowledge_base(query: str, top_k: int = 3) -> str:
    """用于在知识库/数据库中搜索与用户问题相关的参考资料。
    当你需要回答关于专业知识、特定文档内容（例如 OSI 模型）的问题时，请调用此工具。

    Args:
        query: 用户输入的具体搜索问题或提取出的核心关键词。
        top_k: 需要返回的最相关的文本段落数量，默认为 3。
    """
    return search(query, top_k)


if __name__ == "__main__":
    mcp.run(transport="stdio")
