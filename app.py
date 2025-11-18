import json
from flask import Flask, request, jsonify, send_file
import yaml
import uuid

app = Flask(__name__)
DB_FILE = "db.json"

# 读取 db.json
def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

# 保存 db.json
def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f)

# 添加策略组和规则
def add_proxy_groups(yaml_dict):
    nodes = [p['name'] for p in yaml_dict['proxies']]
    yaml_dict['proxy-groups'] = [
        {
            'name': 'Auto',
            'type': 'url-test',
            'proxies': nodes,
            'url': 'http://www.gstatic.com/generate_204',
            'interval': 300
        },
        {
            'name': 'Proxy',
            'type': 'select',
            'proxies': nodes + ['Auto']
        }
    ]
    yaml_dict['rules'] = [
        'DOMAIN-SUFFIX,google.com,Auto',
        'DOMAIN-SUFFIX,facebook.com,Auto',
        'GEOIP,CN,DIRECT',
        'MATCH,Proxy'
    ]
    return yaml_dict

# 转换 VMess 链接为 Clash 节点
def vmess_to_clash(vmess_link):
    import base64
    if vmess_link.startswith("vmess://"):
        vmess_link = vmess_link[8:]
    data = json.loads(base64.b64decode(vmess_link).decode())
    node = {
        'name': data.get('ps', 'vmess-node'),
        'type': 'vmess',
        'server': data['add'],
        'port': int(data['port']),
        'uuid': data['id'],
        'alterId': int(data.get('aid', 0)),
        'cipher': 'auto',
        'network': data.get('net', 'tcp'),
        'tls': data.get('tls', 'none'),
        'skip-cert-verify': True if data.get('tls','none') != 'none' else False,
        'ws-opts': {
            'path': data.get('path', ''),
            'headers': {'Host': data.get('host','')} if data.get('host') else {}
        } if data.get('net','tcp')=='ws' else {}
    }
    return node

@app.route("/sub", methods=["POST","GET"])
def generate_sub():
    db = load_db()
    vmess_links = request.args.get("links") or request.form.get("links")
    if not vmess_links:
        return "请提供 vmess 链接", 400

    vmess_links = vmess_links.strip().splitlines()
    proxies = []
    for link in vmess_links:
        node = vmess_to_clash(link.strip())
        proxies.append(node)

    yaml_dict = {'proxies': proxies}
    yaml_dict = add_proxy_groups(yaml_dict)

    yaml_data = yaml.dump(yaml_dict, allow_unicode=True)
    return yaml_data, 200, {'Content-Type': 'text/yaml; charset=utf-8'}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=58000)
