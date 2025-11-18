from flask import Flask, request, jsonify, Response, render_template
import base64, json, uuid, os

app = Flask(__name__)

DB_FILE = "db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            f.write("{}")
    return json.load(open(DB_FILE, "r"))

def save_db(data):
    json.dump(data, open(DB_FILE, "w"), indent=2)

### ------------------ 节点解析 ------------------ ###
def decode_vmess(url):
    url = url.replace("vmess://", "")
    padded = url + "=" * (-len(url) % 4)
    return json.loads(base64.b64decode(padded).decode())

def decode_ss(url):
    # ss://method:password@server:port
    url = url.replace("ss://", "")
    padded = url + "=" * (-len(url) % 4)
    decoded = base64.b64decode(padded).decode()
    method, tail = decoded.split(":", 1)
    password, tail2 = tail.split("@", 1)
    server, port = tail2.split(":")
    return {
        "type": "ss",
        "server": server,
        "port": port,
        "method": method,
        "password": password
    }

def decode_trojan(url):
    url = url.replace("trojan://", "")
    password, rest = url.split("@", 1)
    server, port = rest.split(":")
    return {
        "type": "trojan",
        "server": server,
        "port": port,
        "password": password
    }

### ------------------ 转 Clash 节点 ------------------ ###
def vmess_to_clash(v):
    return {
        "name": v.get("ps", "vmess"),
        "type": "vmess",
        "server": v["add"],
        "port": int(v["port"]),
        "uuid": v["id"],
        "alterId": int(v.get("aid", 0)),
        "cipher": "auto",
        "udp": True,
        "network": v.get("net", "tcp")
    }

def ss_to_clash(v):
    return {
        "name": "shadowsocks",
        "type": "ss",
        "server": v["server"],
        "port": int(v["port"]),
        "cipher": v["method"],
        "password": v["password"],
        "udp": True
    }

def trojan_to_clash(v):
    return {
        "name": "trojan",
        "type": "trojan",
        "server": v["server"],
        "port": int(v["port"]),
        "password": v["password"],
        "udp": True,
        "sni": ""
    }

### ------------------ 页面 ------------------ ###
@app.route("/")
def index():
    return render_template("index.html")

### ------------------ 提交节点 → 返回 Token ------------------ ###
@app.route("/submit", methods=["POST"])
def submit():
    nodes = request.form["nodes"].strip().splitlines()
    token = str(uuid.uuid4())

    db = load_db()
    db[token] = nodes
    save_db(db)

    url = f"{request.host_url}sub/{token}"
    return jsonify({"ok": True, "url": url})

### ------------------ Clash 订阅链接 ------------------ ###
@app.route("/sub/<token>")
def sub(token):
    db = load_db()
    if token not in db:
        return "Invalid token", 404

    links = db[token]

    clash_nodes = []
    for link in links:
        if link.startswith("vmess://"):
            clash_nodes.append(vmess_to_clash(decode_vmess(link)))
        elif link.startswith("ss://"):
            clash_nodes.append(ss_to_clash(decode_ss(link)))
        elif link.startswith("trojan://"):
            clash_nodes.append(trojan_to_clash(decode_trojan(link)))

    yaml = "proxies:\n"
    for n in clash_nodes:
        yaml += f"  - {json.dumps(n, ensure_ascii=False)}\n"

    return Response(yaml, mimetype="text/plain")

### ------------------ 启动 ------------------ ###
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
