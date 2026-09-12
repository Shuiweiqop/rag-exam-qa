import os
import psycopg2
from google import genai
from dotenv import load_dotenv

load_dotenv()

# ---- 1. 登录 Gemini ----
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 2. 你要问的问题 ----
question = "植物是怎么制造养分的？"

# ---- 3. 把问题算成向量 ----
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

# ---- 5. 找出最相关的 1 段（这就是"改一个数字"的地方：limit 1）----
cur.execute(
    """
    select content, embedding <=> %s::vector as distance
    from documents
    order by distance
    limit 1
    """,
    (str(query_vector),)
)
row = cur.fetchone()          # 只取 1 段，所以用 fetchone
context = row[0]              # 找到的那段原文
distance = row[1]

cur.close()
conn.close()

# ========== 以下是今天新增的部分：让 AI 基于这段资料回答 ==========

# ---- 6. 拼提示词：告诉 AI"只能根据这段资料回答" ----
prompt = f"""你是一个考试问答助手。请只根据下面提供的资料回答问题，不要用你自己的知识编造。

资料：
{context}

问题：{question}

请用一两句话回答。"""

# ---- 7. 让 Gemini 生成回答 ----
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

# ---- 8. 打印结果 + 引用来源 ----
print("问题：", question)
print("=" * 45)
print("回答：", response.text)
print("-" * 45)
print("引用来源（距离 {:.4f}）：".format(distance))
print(context)