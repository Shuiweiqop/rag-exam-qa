import os
import psycopg2
from google import genai
from dotenv import load_dotenv
from fastapi import FastAPI          # 新：开窗口的框架
from pydantic import BaseModel       # 新：定义"递进来的数据长什么样"

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 建一个数据库连接的小函数（把重复的连库代码抽出来）----
def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )

# ---- 创建 FastAPI 应用（相当于"开一家店"）----
app = FastAPI()

# ==================== 定义"递进来的数据格式" ====================
# 就像 Laravel 的 Request 验证：告诉系统前端会传什么字段
class UploadRequest(BaseModel):
    text: str            # /upload 接口：会收到一个 text 字段

class AskRequest(BaseModel):
    question: str        # /ask 接口：会收到一个 question 字段

# ==================== 接口 1：/upload ====================
# 相当于 Laravel: Route::post('/upload', ...)
@app.post("/upload")
def upload(req: UploadRequest):
    # ↓↓↓ 这段就是从 ingest.py 搬来的：算 embedding + 存库 ↓↓↓
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=req.text
    )
    vector = result.embeddings[0].values

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "insert into documents (content, embedding) values (%s, %s)",
        (req.text, str(vector))
    )
    conn.commit()
    cur.close()
    conn.close()
    # ↑↑↑ 搬运结束 ↑↑↑

    return {"message": "已存入", "text": req.text}   # 把结果递出窗口

# ==================== 接口 2：/ask ====================
# 相当于 Laravel: Route::post('/ask', ...)
@app.post("/ask")
def ask(req: AskRequest):
    # ↓↓↓ 这段就是从 ask.py 搬来的：检索 + 生成回答 ↓↓↓
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=req.question
    )
    query_vector = result.embeddings[0].values

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        select content, embedding <=> %s::vector as distance
        from documents
        order by distance
        limit 1
        """,
        (str(query_vector),)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    context = row[0]
    distance = row[1]

    prompt = f"""你是一个考试问答助手。请只根据下面提供的资料回答问题，不要用你自己的知识编造。

资料：
{context}

问题：{req.question}

请用一两句话回答。"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    # ↑↑↑ 搬运结束 ↑↑↑

    # 把回答 + 引用一起递出窗口
    return {
        "question": req.question,
        "answer": response.text,
        "source": context,
        "distance": distance,
    }