import os
import psycopg2
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
# ---- 20 OSI knowledge chunks (English) ----
chunks = [
    "The OSI (Open Systems Interconnection) model is a conceptual framework that divides network communication into seven layers: physical, data link, network, transport, session, presentation, and application. Its benefits are simplifying network design, easier troubleshooting, and allowing changes at one layer without affecting others.",
    "The physical layer transmits and receives raw bits over a physical medium such as cables, wires, or wireless signals. The data link layer is the second layer, responsible for framing, addressing, error detection, and error correction of data frames.",
    "The network layer handles routing, forwarding, addressing, and congestion control, and defines the logical structure and topology of the network. The transport layer is the fourth layer, responsible for reliable, ordered, error-free end-to-end delivery of packets, and defines connection-oriented or connectionless services.",
    "The session layer establishes, maintains, and terminates sessions between applications, and defines synchronization, authentication, authorization, and encryption. The presentation layer is the sixth layer, handling translation, formatting, compression, and encryption of data, and defines syntax and semantics. The application layer is the seventh and highest layer, providing services and protocols for specific applications.",
    "Common protocols per layer. Physical: ADSL, ISDN, Bluetooth, Ethernet. Data link: ARP, MAC, HDLC, STP. Network: IP, ICMP, IGMP, RIP, BGP. Transport: TCP, UDP, GRE. Session: NFS. Presentation: SSL. Application: SSH, DNS, DHCP, NTP, HTTP.",
    "TCP is connection-oriented: it establishes a connection before transfer, uses sequence numbers to keep packet order, guarantees delivery via acknowledgment and retransmission, checks errors with checksums and windowing, does not support broadcasting, retransmits lost packets, and is slower than UDP. UDP is connectionless: no connection setup, does not keep order, does not guarantee delivery, minimal error checking with checksums only, supports broadcast and multicast, does not retransmit, and is faster than TCP.",
    "Devices operating at each layer. Physical: hub, repeater. Data link: switch, bridge, network interface card (NIC). Network: router. Transport: gateway, firewall. Session: proxy server. Presentation: encryption device. Application: web server, phones.",
    "An alternative to the OSI model is the TCP/IP model, a condensed version with four layers instead of seven, also known as the Internet model. Its four layers are: application layer, transport layer, internet layer, and network access layer.",
    "Common network problems per layer. Physical: damaged cables, loose connectors, interference, signal attenuation. Data link: frame errors, collisions, MAC address conflicts. Network: IP address conflicts, routing loops, packet loss. Transport: port conflicts, connection timeouts, segment reordering. Session: session hijacking, session termination. Presentation: data corruption, encryption errors. Application: protocol mismatch, service unavailability.",
    "Encapsulation is the process of adding headers and trailers to data at each layer as it travels down from the application layer to the physical layer; headers hold layer-specific info, trailers hold error-detection info such as CRC. Decapsulation is the reverse: as data travels up from physical to application, each layer reads and removes header and trailer info before passing data up.",
    "An IP address is an Internet Protocol address, 4 bytes for IPv4 and 16 bytes for IPv6, assigned by an ISP or network administrator, operating at the network layer, retrieved via RARP. A MAC address is a Media Access Control address, 6 bytes, assigned by the NIC manufacturer, operating at the data link layer, retrieved via ARP.",
    "A port number is a logical address assigned to each network application or process, uniquely identifying an application on a computer, as a 16-bit integer. Common ports: FTP 20/21, SSH 22, Telnet 23, SMTP 25, DNS 53, DHCP 67/68, HTTP 80, POP3 110, IMAP4 143, HTTPS 443.",
    "A router operates at the network layer, managing traffic between different networks and forwarding packets to their destination IP. Its functions include routing (choosing the best path), logical address assignment, and host-to-host forwarding. A router only needs the destination IP, routing table, and routing protocol info to make forwarding decisions, without inspecting the entire packet payload.",
    "Unicast is one-to-one, from a single sender to a single receiver. Broadcast sends from a sender to all receivers within the same network, commonly used for ARP and RIP management packets. Multicast sends from a single source to a specific group of interested hosts, sitting between unicast and broadcast.",
    "Segmentation is the transport layer (layer 4) process of dividing a data packet into smaller units for network transmission. Data arriving at the transport layer is split into segments, each with a sequence number, so the transport layer can correctly reassemble them at the destination and identify and replace lost packets.",
    "Flow control ensures proper data transmission from sender to receiver, preventing receiver buffer overflow and data loss, using methods like sliding window and stop-and-wait. Error control delivers error-free reliable data to the receiver, detecting errors via parity check, CRC, and checksum, using methods like stop-and-wait ARQ and sliding window ARQ.",
    "A firewall mainly does static packet filtering at the network layer (layer 3), inspecting packets by source and destination address; at the transport layer (layer 4) it inspects TCP and UDP traffic; some advanced firewalls understand the application layer (layer 7). Packet-filtering firewalls work at layers 3 and 4, stateful firewalls at layer 4, and next-generation firewalls at layer 7.",
    "CRC stands for Cyclic Redundancy Check, an error-detecting code commonly used in digital networks and storage devices to detect accidental changes to data. It is good at detecting common errors caused by transmission-channel noise, and its check value has a fixed length. CRC operates at the data link layer.",
    "Half-duplex is bidirectional but only one direction at a time, using one channel, with lower performance, saving bandwidth by alternating on a single channel. Full-duplex is bidirectional and simultaneous, using two channels, with better performance and doubled bandwidth utilization.",
    "Ping sends an ICMP echo request packet to a target device, which replies with a packet; it is most commonly used to measure reply time in milliseconds (lower is better). On Windows, open Command Prompt and type ping followed by an IP or URL; it sends four packets, and 'request timed out' means no reply was received from the target.",
]
# ---- 连数据库 ----
conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

# ---- 先清空表（把旧的 4 条测试数据删掉）----
cur.execute("delete from documents")
print("已清空旧数据")

# ---- 循环：每段算 embedding 并存入 ----
for i, chunk in enumerate(chunks, start=1):
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=chunk
    )
    vector = result.embeddings[0].values
    cur.execute(
        "insert into documents (content, embedding) values (%s, %s)",
        (chunk, str(vector))
    )
    print(f"[{i}/{len(chunks)}] 已存入：{chunk[:20]}...")

conn.commit()
cur.close()
conn.close()
print("全部完成！共存入", len(chunks), "条")