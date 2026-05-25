# Release Notes — v4.4 (2026-05-25)

## 一句话总结
失败诊断工具从"能跑"升级到"好用"：9 种探查策略、AI RAG 智能建议、模型降级链，外加一个 DOM 向量知识库。

---

## 新增功能

### 1. DOM 向量知识库 (`tools/dom_kb.py`)
- 用 FAISS + SentenceTransformers 把 DOM 元素做成向量知识库
- 支持从 `ui_snapshot.py` 基线快照一键构建：`python tools/dom_kb.py build --env release`
- 支持语义查询：`python tools/dom_kb.py query --role button --name "Edit post"`
- 诊断工具每步成功后自动增量更新，知识库越跑越聪明

### 2. AI RAG 智能建议 (Probe 9)
- 失败诊断时，DOM KB 向量检索 Top-5 相似元素 → Gemini 判断最佳匹配 → 自动生成 YAML 定位修复
- 与规则建议（Probe 7/8）**同时展示**，按 confidence 排序，不互相替代
- HTML 报告里 AI 建议带 "View all RAG candidates" 折叠面板，可查看完整检索结果
- 终端输出带 `[AI RAG]` / `[Rule]` 标签，支持逐个确认/跳过

### 3. Gemini 模型降级链 + 多 Key 自动轮换
- 配额耗尽时自动切 Key，Key 用完自动降级模型
- 降级链：`gemini-2.5-flash` → `gemini-2.0-flash` → `gemini-2.0-flash-lite`
- 全自动，无需人工干预

### 4. 诊断报告增强
- 从 6 种探查策略扩展到 **9 种**（新增模糊定位预警、状态回溯异常、AI RAG 建议）
- 新增 ROOT CAUSE PREDICTION：Cascade Failure / Modal 遮挡 / 状态异常 三种根因预测
- 所有建议（规则 + AI）同时展示，不再只取最高分

---

## 改进与修复

- **诊断工具**: 完整执行 pre_condition（前置步骤全量重放，不是跳过）
- **Cookie 注入**: 统一使用 `storage_state`（与 conftest.py 一致）
- **Action Registry 兼容**: 104 个自定义 action 自动 fallback
- **Optional 步骤**: 自动跳过（步骤名含 "optional" 标记为 SKIPPED）
- **Mock AI 模块**: 默认关闭，启动时间从 ~20s 降至 ~0.6s

---

## 文档更新

- `README.md` / `README.en.md` / `TECHNICAL_GUIDE.md` 全部升级到 v4.4
- 新增 DOM KB 和 AI RAG 章节
- 更新工具总览表（新增 `dom_kb.py`）
- 更新 `.env` 配置说明（多 Key + 模型降级链）

---

## 升级指南

1. 拉取代码
2. 安装新依赖：`pip install faiss-cpu sentence-transformers`
3. 构建 DOM 知识库：`python tools/dom_kb.py build --env release`
4. 确认 `backend/.env` 中 `GEMINI_API_KEYS` 已配置（支持多 Key 逗号分隔）
5. 开始用：`python tools/diagnose_failed.py`

---

## 文件变更

```
.gitignore              |  11 +
README.en.md            |  72 ++
README.md               |  72 ++
TECHNICAL_GUIDE.md      | 146 ++
main.py                 |  15 +
Storefront_form.yaml    |   4 +-
Storefront_product...   |   2 +-
tools/diagnose_failed.py|1169 +++++++++++++++++++-
8 files changed, 1423 insertions(+), 68 deletions(-)
```
