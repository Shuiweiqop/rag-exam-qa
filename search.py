import os
import psycopg2
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ---- 1. 登录 Gemini ----
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 2. 你要问的问题（先写死，试完可以随便改）----
question = "苹果为什么会跌地上？"

# ---- 3. 把问题也算成向量（关键：型号要和存文档时一样）----
result = client.models.embed_content(
    model="gemini-embedding-001",
    contents=question
)
query_vector = result.embeddings[0].values

# ---- 4. 连数据库 ----
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

# ---- 5. 让数据库找"离问题最近"的 3 段 ----
cur.execute(
    """
    select content, embedding <=> %s::vector as distance
    from documents
    order by distance
    limit 3
    """,
    (str(query_vector),)
)

rows = cur.fetchall()

# ---- 6. 打印结果 ----
print("问题：", question)
print("-" * 40)
for content, distance in rows:
    print(f"距离 {distance:.4f}  |  {content}")

cur.close()
conn.close()