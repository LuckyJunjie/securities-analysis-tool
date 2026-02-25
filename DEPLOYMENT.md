# 证券分析工具 - 外网访问部署方案

**项目:** securities-analysis-tool  
**目标:** 从外网访问 Web 服务

---

## 方案对比

### 方案 1: 内网穿透 (推荐)

| 服务商 | 免费额度 | 速度 | 稳定性 |
|--------|----------|------|--------|
| **natapp.cn** | 1条隧道 | 快 | 稳定 |
| **ngrok** | 1条隧道 | 快 | 稳定 |
| **frp** | 自建 | 快 | 稳定 |

### 方案 2: 公网 IP + 端口转发

- 需要路由器设置端口转发
- 需要公网 IP (可能被回收)

### 方案 3: 云服务器

- 购买云服务器运行
- 成本较高

---

## 推荐: natapp 内网穿透

### 1. 注册 natapp

https://natapp.cn

### 2. 下载客户端

```bash
# Linux ARM64
wget https://dl.natapp.cn/releases/v2.0/autoload -O natapp
chmod +x natapp
```

### 3. 配置

```bash
# 创建配置目录
mkdir -p ~/.natapp
cat > ~/.natapp/config.yml << EOF
authtoken: 你的TOKEN
logto: /tmp/natapp.log
EOF
```

### 4. 启动

```bash
# 启动 securities-analysis-tool
cd /path/to/securities-analysis-tool
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 &

# 启动内网穿透
./natapp -config=~/.natapp/config.yml
```

---

## 部署脚本

```bash
#!/bin/bash
# 启动脚本

# 1. 启动后端
cd /path/to/securities-analysis-tool
source venv/bin/activate
uvicorn src.backend.main:app --host 0.0.0.0 --port 8000 &

# 2. 启动 natapp
/path/to/natapp -config=~/.natapp/config.yml
```

---

## 访问方式

启动后会显示外网 URL:
```
natapp -> Forwarding -> http://xxxxx.ngrok.io -> 127.0.0.1:8000
```

访问: http://xxxxx.ngrok.io/api/stocks

---

## 备选方案: Cloudflare Tunnel

免费，无需安装客户端:
```bash
# 安装 cloudflared
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-arm64 -o /usr/local/bin/cloudflared
chmod +x /usr/local/bin/cloudflared

# 登录并创建隧道
cloudflared tunnel login
cloudflared tunnel create my-tunnel

# 配置
cloudflared tunnel route dns my-tunnel mysubdomain.example.com

# 运行
cloudflared tunnel run --url http://localhost:8000 my-tunnel
```

---

*最后更新: 2026-02-25*
