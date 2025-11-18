# VMess/SS/Trojan → Clash 订阅转换器

一个轻量级在线转换器，可以将 VMess / Shadowsocks / Trojan / VLESS 节点转换为 Clash 订阅链接，支持 Docker 一键部署和网页管理界面。

---

## 功能

* 支持 VMess、Shadowsocks、Trojan 节点解析
* 自动生成 Clash YAML 订阅链接
* 提供网页界面，输入节点即可生成订阅
* 支持 Docker / Docker Compose 部署
* 支持内网或公网访问（可配域名 + HTTPS）

---

## 目录结构

```
vmess2clash/
├─ app.py                # Flask 后端主程序
├─ db.json               # 节点存储文件
├─ docker-compose.yml    # Docker Compose 配置
├─ Dockerfile            # Docker 镜像构建文件
├─ requirements.txt      # Python 依赖
├─ templates/
│    └─ index.html       # 前端网页模板
└─ README.md             # 项目说明文件
```

---

## 部署步骤（Docker）

1. **克隆仓库**

```bash
git clone https://github.com/oldxianyu/vmess2clash.git
cd vmess2clash
```

2. **确保 db.json 存在**

```bash
echo "{}" > db.json
```

3. **修改端口（可选，默认 8000）**

* 在 `app.py` 修改：

```python
app.run(host="0.0.0.0", port=58000)
```

* 在 `docker-compose.yml` 对应修改端口映射：

```yaml
ports:
  - "58000:58000"
```

4. **构建并启动容器**

```bash
docker compose up -d --build
```

5. **检查容器状态**

```bash
docker ps
```

---

## 使用方法

1. 打开浏览器访问：

```
http://服务器IP:58000/
```

2. 在网页上输入节点，每行一个（支持 VMess、SS、Trojan）
3. 点击 **生成订阅链接**
4. 拷贝生成的 URL，添加到 Clash / Clash.Meta 中即可使用：

```
http://服务器IP:58000/sub/<token>
```

5. 节点会保存在 `db.json`，重复访问订阅链接不会丢失。

---

## 注意事项

* 防火墙或云服务安全组需要放行端口（例如 58000）
* Docker Compose V2 不再需要 `version` 字段，可删除
* 若端口被占用，可修改 `app.py` 和 `docker-compose.yml` 端口
* 推荐配合 Nginx 反向代理 + HTTPS 提供安全访问

---

## 更新与维护

更新代码：

```bash
git pull
docker compose down
docker compose up -d --build
```

重启容器：

```bash
docker compose restart
```

停止容器：

```bash
docker compose down
```

---

## License

MIT License
