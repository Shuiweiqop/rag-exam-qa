import os
import json
import psycopg2
from google import genai
from dotenv import load_dotenv
import time

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 1. 读评测题 ----
with open("eval_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# ---- 2. 连数据库 ----
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

# ---- 3. 检索函数：给一个问题，返回最相关的 top-k 段 ----
def retrieve(question, k):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=question
    )
    qvec = result.embeddings[0].values
    cur.execute(
        """
        select content
        from documents
        order by embedding <=> %s::vector
        limit %s
        """,
        (str(qvec), k)
    )
    return [row[0] for row in cur.fetchall()]   # 返回 k 段文字的列表

# ---- 4. 跑评测：同时算 recall@1 和 recall@3 ----
hit_at_1 = 0
hit_at_3 = 0
total = len(questions)

for i, q in enumerate(questions, start=1):
    question = q["question"]
    keyword = q["must_contain"]

    top3 = retrieve(question, 3)      # 取前 3 段

    # recall@1：只看第 1 段含不含关键词
    if keyword.lower() in top3[0].lower():
        hit_at_1 += 1
        mark1 = "O"
    else:
        mark1 = "X"

    # recall@3：前 3 段里任意一段含关键词就算命中
    if any(keyword.lower() in c.lower() for c in top3):
        hit_at_3 += 1
        mark3 = "O"
    else:
        mark3 = "X"
    
    print(f"[{i}/{total}] @1:{mark1} @3:{mark3}  {question[:40]}")
    time.sleep(1)
# ---- 5. 打印总分 ----
print("=" * 50)
print(f"Recall@1: {hit_at_1}/{total} = {hit_at_1/total:.1%}")
print(f"Recall@3: {hit_at_3}/{total} = {hit_at_3/total:.1%}")

cur.close()
conn.close()