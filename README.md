# AI Media Agent（Codex 项目）

面向中国大陆新媒体平台的低成本 AI Agent 运营辅助系统。此仓库是可继续开发的 MVP 骨架，不是已经完成的无人值守产品。当前不连接真实社交账号、不发布内容。

## 目标闭环
趋势采集 → 选题评分 → 文案/素材生成 → 人工审核 → 合规发布 → 数据采集 → 复盘优化。

## 技术栈
- Python 3.11+、FastAPI
- PostgreSQL
- SQLAlchemy 2 + Alembic 数据模型和迁移
- 标准库 RSS/Atom 采集（用户明确配置公开 HTTPS feed；不登录、不抓取社交平台页面）
- n8n（自托管工作流，后续启用）
- Docker Compose、pytest

## 本地运行
```bash
python -m venv .venv
# Ubuntu/macOS
source .venv/bin/activate
# Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload
```
打开 http://127.0.0.1:8000/docs。

## 数据库
默认使用项目目录中的 SQLite 文件，便于本地开发；配置 `DATABASE_URL` 可切换到 PostgreSQL。首次初始化先执行 `alembic upgrade head`。迁移目前包含 topics、content_items、content_metrics 三张表。应用启动不会自动改库。

RSS/Atom 采集器位于 `app/collectors/rss.py`。使用 `fetch_feed` 拉取公开 HTTPS feed，再用 `save_topics(session, records)` 幂等入库；项目暂未配置任何默认 feed，也不会后台定时抓取。feed 必须由操作者自行确认授权、条款和适用法律。

## 可选服务
复制 `.env.example` 为 `.env`，替换示例密码后运行 `docker compose up -d`。
服务端口默认只绑定 127.0.0.1。未配置安全措施前不要暴露到公网。

## 首期约束
- 先做一个垂直领域、一个账号、一个平台。
- 不假设平台开放了自动发布或完整数据接口；开发前核实官方文档、账号资质和授权。
- 未审核内容不得自动发布。
- 不实现绕过验证码、模拟未授权登录或隐蔽爬取。
- 不承诺变现收益；记录成本与真实转化数据。

## 当前范围与限制
- 已有健康检查、选题评分、基础数据模型/首个迁移、RSS/Atom feed 解析和入库函数。
- 采集内容代表配置 feed 的公开条目，不等于抖音/小红书/微信公众号趋势指标；不产生或推测热度数字。
- 尚无自动审批工作流、LLM 接口、平台发布适配器、真实账号接入和数据分析闭环。
- 本轮静态准备了测试，但依照用户要求没有执行命令或测试；依赖安装和运行状态未验证。
- 可行性、架构、缺口及费用估算见 [docs/STATIC_REVIEW.md](docs/STATIC_REVIEW.md)。
