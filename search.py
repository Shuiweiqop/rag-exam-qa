import os
import psycopg2
from google import genai
from dotenv import load_dotenv

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def search(query: str, top_k: int = 3) -> str:
    """（先别管 docstring，Step 2 再写。今天先让它变成能调用的函数）"""

    # ---- 把问题算成向量 ----
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=query
    )
    query_vector = result.embeddings[0].values

    # ---- 连数据库（原样搬）----
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )
    cur = conn.cursor()

    # ---- 查最近的 top_k 段 ----
    cur.execute(
        """
        select content, embedding <=> %s::vector as distance
        from documents
        order by distance
        limit %s
        """,
        (str(query_vector), top_k)
    )
    rows = cur.fetchall()

    cur.close()
    conn.close()

    # ---- 出口：把结果拼成一段文字【返回】，不是 print ----
    context = "\n\n".join(
        f"[片段{i}] {content}" for i, (content, distance) in enumerate(rows, 1)
    )
    return context



