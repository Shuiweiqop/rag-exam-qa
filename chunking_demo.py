# ---- 一篇完整的 OSI 长文（当作"原始文档"，等下用三种切法切它）----
document = """The OSI model is a conceptual framework that divides network communication into seven layers: physical, data link, network, transport, session, presentation, and application. It simplifies network design and allows changes at one layer without affecting others.

The physical layer transmits raw bits over a physical medium such as cables or wireless signals. The data link layer handles framing, addressing, error detection, and error correction. The network layer handles routing, forwarding, and addressing, and defines the logical topology of the network.

The transport layer ensures reliable, ordered, error-free end-to-end delivery of packets. TCP is connection-oriented and guarantees delivery through acknowledgment and retransmission, while UDP is connectionless, does not guarantee delivery, but is faster.

The session layer establishes and manages sessions between applications. The presentation layer handles translation, compression, and encryption of data. The application layer is the highest layer and provides services and protocols for specific applications such as HTTP, DNS, and SSH.

An IP address operates at the network layer and identifies a device logically, while a MAC address operates at the data link layer and is assigned by the network card manufacturer. A router works at the network layer to forward packets to their destination IP using a routing table.

CRC (Cyclic Redundancy Check) is an error-detecting code that operates at the data link layer. Flow control prevents the receiver's buffer from overflowing, while error control ensures reliable delivery through techniques like checksums and retransmission."""


# ---- 切法 1：按段落切（遇到空行就分一块）----
def chunk_by_paragraph(text):
    # split by blank line (段落之间的空行)
    paragraphs = text.split("\n\n")
    return [p.strip() for p in paragraphs if p.strip()]


# ---- 切法 2：按固定长度切（不管段落，每 200 字符硬切一块）----
def chunk_by_fixed(text, size=200):
    chunks = []
    for i in range(0, len(text), size):
        chunks.append(text[i:i + size])
    return chunks


# ---- 切法 3：带重叠切（每块 200 字符，但每块往前重叠 50 字符）----
def chunk_by_overlap(text, size=200, overlap=50):
    chunks = []
    step = size - overlap        # 每次前进 150，而不是 200，所以有 50 重叠
    for i in range(0, len(text), step):
        chunks.append(text[i:i + size])
    return chunks


# ---- 打印三种切法的效果对比 ----
for name, func in [
    ("按段落切", chunk_by_paragraph),
    ("按固定长度切", lambda t: chunk_by_fixed(t, 200)),
    ("带重叠切", lambda t: chunk_by_overlap(t, 200, 50)),
]:
    chunks = func(document)
    print("=" * 60)
    print(f"【{name}】切出 {len(chunks)} 块")
    print("=" * 60)
    for i, c in enumerate(chunks, start=1):
        print(f"--- 第 {i} 块（{len(c)} 字符）---")
        print(c[:80], "..." if len(c) > 80 else "")
    print()