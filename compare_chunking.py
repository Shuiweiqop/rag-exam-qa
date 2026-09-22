import os
import json
import time
import psycopg2
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# ---- 长文（和 demo 里一样）----
document = """The OSI model is a conceptual framework that divides network communication into seven layers: physical, data link, network, transport, session, presentation, and application. It simplifies network design and allows changes at one layer without affecting others.

The physical layer transmits raw bits over a physical medium such as cables or wireless signals. The data link layer handles framing, addressing, error detection, and error correction. The network layer handles routing, forwarding, and addressing, and defines the logical topology of the network.

The transport layer ensures reliable, ordered, error-free end-to-end delivery of packets. TCP is connection-oriented and guarantees delivery through acknowledgment and retransmission, while UDP is connectionless, does not guarantee delivery, but is faster.

The session layer establishes and manages sessions between applications. The presentation layer handles translation, compression, and encryption of data. The application layer is the highest layer and provides services and protocols for specific applications such as HTTP, DNS, and SSH.

An IP address operates at the network layer and identifies a device logically, while a MAC address operates at the data link layer and is assigned by the network card manufacturer. A router works at the network layer to forward packets to their destination IP using a routing table.

CRC (Cyclic Redundancy Check) is an error-detecting code that operates at the data link layer. Flow control prevents the receiver's buffer from overflowing, while error control ensures reliable delivery through techniques like checksums and retransmission."""

# ---- 三种切法 ----
def chunk_by_paragraph(text):
    return [p.strip() for p in text.split("\n\n") if p.strip()]

def chunk_by_fixed(text, size=200):
    return [text[i:i+size] for i in range(0, len(text), size)]

def chunk_by_overlap(text, size=200, overlap=50):
    step = size - overlap
    return [text[i:i+size] for i in range(0, len(text), step)]

# ---- 读评测题 ----
with open("eval_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# ---- 连库 ----
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"), port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"), user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

# ---- 算 embedding 的小函数（带重试，撞限速就等着再来）----
def embed(text):
    while True:
        try:
            r = client.models.embed_content(model="gemini-embedding-001", contents=text)
            return r.embeddings[0].values
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                print("   ...限速了，等 30 秒")
                time.sleep(30)
            else:
                raise

# ---- 用某种切法：清空→切→存 ----
def load_with_strategy(chunks):
    cur.execute("delete from documents")
    for c in chunks:
        vec = embed(c)
        cur.execute("insert into documents (content, embedding) values (%s, %s)", (c, str(vec)))
        time.sleep(1)
    conn.commit()

# ---- 跑评测：返回 (recall@1, recall@3) ----
def run_eval():
    hit1 = hit3 = 0
    for q in questions:
        qvec = embed(q["question"])
        cur.execute(
            "select content from documents order by embedding <=> %s::vector limit 3",
            (str(qvec),)
        )
        top3 = [row[0] for row in cur.fetchall()]
        kw = q["must_contain"].lower()
        if top3 and kw in top3[0].lower():
            hit1 += 1
        if any(kw in c.lower() for c in top3):
            hit3 += 1
        time.sleep(1)
    n = len(questions)
    return hit1/n, hit3/n

# ---- 主流程：三种切法各跑一遍 ----
strategies = [
    ("按段落切", chunk_by_paragraph(document)),
    ("固定长度切", chunk_by_fixed(document, 200)),
    ("带重叠切", chunk_by_overlap(document, 200, 50)),
]

results = []
for name, chunks in strategies:
    print(f"\n>>> 正在测试【{name}】（{len(chunks)} 块）...")
    load_with_strategy(chunks)
    r1, r3 = run_eval()
    results.append((name, len(chunks), r1, r3))
    print(f"    {name}: Recall@1={r1:.1%}  Recall@3={r3:.1%}")

# ---- 打印对比表 ----
print("\n" + "=" * 55)
print("Chunking 策略对比")
print("=" * 55)
print(f"{'策略':<12}{'块数':<8}{'Recall@1':<12}{'Recall@3':<12}")
print("-" * 55)
for name, n, r1, r3 in results:
    print(f"{name:<12}{n:<8}{r1:<12.1%}{r3:<12.1%}")

cur.close()
conn.close()
print("\n完成！")