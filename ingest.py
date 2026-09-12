import os
import psycopg2                      # 跟 Postgres 说话的翻译官
from google import genai            # 昨天用过的 Gemini 库
from dotenv import load_dotenv

load_dotenv()

# ---- 1. 登录 Gemini ----
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 2. 准备几段练手文字（先写死，明天再换成真资料）----
chunks = [
    "光合作用是植物利用阳光、二氧化碳和水制造养分的过程，会释放氧气。",
    "牛顿第一定律说：物体在没有外力作用时，会保持静止或匀速直线运动。",
    "冒泡排序是一种简单的排序算法，通过反复交换相邻的逆序元素来排序。",
]

# ---- 3. 连接数据库 ----
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()                 # cursor = 你在数据库里干活的那只手

# ---- 4. 每段文字算 embedding，然后存进去 ----
for chunk in chunks:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=chunk
    )
    vector = result.embeddings[0].values      # 拿到 3072 个数字

    # 把 (原文, 向量) 插进 documents 表
    cur.execute(
        "insert into documents (content, embedding) values (%s, %s)",
        (chunk, vector)
    )
    print("已存入：", chunk[:15], "...")

conn.commit()                       # 提交，真正写进数据库
cur.close()
conn.close()
print("全部完成！")