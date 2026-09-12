import os                          # 用来读环境变量
from google import genai          # 新版 Gemini 库
from dotenv import load_dotenv     # 读 .env 工具

load_dotenv()                      # 把 .env 里的 key 读进来

# 用 key 建一个"客户端"（相当于登录后拿到的操作台）
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# 把一句话变成 embedding（一串数字）
result = client.models.embed_content(
    model="gemini-embedding-001",   # 换成现在通用的型号名
    contents="我今天学会了怎么搭 Python 环境"
)

vector = result.embeddings[0].values   # 取出那串数字
print("这句话被变成了", len(vector), "个数字")
print("前 5 个数字长这样：", vector[:5])