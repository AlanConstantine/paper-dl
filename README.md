# Paper Downloader (paper-dl)

一个统一的命令行学术论文检索与下载工具。支持跨库检索、自动判断开放获取状态、下载全文或元数据，并通过 Microsoft MarkItDown 统一转换为 Markdown 格式。

---

## 快速开始

```bash
# 安装
pip install -e .

# 可选：启用 Sci-Hub fallback（见下方说明）
pip install paper-dl[scihub]

# 复制并编辑配置文件（至少填写 unpaywall_email）
cp paper_dl.toml.example paper_dl.toml

# 关键词检索（仅预览）
paper-dl search -q "lithium battery SEI formation" -n 10

# 检索并下载 OA 论文
paper-dl search -q "QM/MM electrochemistry" -n 20 --oa-only --download --output-dir ./papers

# 按作者检索（自动显示匹配度评分）
paper-dl search -a "Martin Z. Bazant" -n 50

# 按作者检索并过滤低匹配结果（保留分数 ≥ 0.70 的论文）
paper-dl search -a "Martin Z. Bazant" -n 50 --min-author-score 0.70 --download

# ChemRxiv 专项检索（化学预印本）
paper-dl search -q "solid state electrolyte" --source chemrxiv -n 20

# 通过 DOI 直接下载
paper-dl download -d "10.48550/arXiv.1706.03762" --output-dir ./papers

# 批量任务
paper-dl batch --input tasks.txt --output-dir ./literature

# 查看下载历史统计
paper-dl history stats
```

---

## 支持的数据源

| 数据源 | 覆盖领域 | 是否需要 API Key | 说明 |
|--------|---------|----------------|------|
| Semantic Scholar | 全领域 | 可选（提升速率） | 含引用数、参考文献数 |
| OpenAlex | 全领域 | 否 | 覆盖广，含开放获取状态 |
| CrossRef | 全领域 | 否 | 元数据最全（卷/期/页） |
| PubMed | 生物医学 | 可选 | NCBI E-utilities |
| arXiv | 预印本 | 否 | 全部为开放获取 |
| CORE | OA 论文聚合 | 是（免费注册） | 聚合多源开放获取 PDF |
| **ChemRxiv** ✨ | **化学预印本** | **否** | **ACS 官方 API，全部免费下载** |

在 `paper_dl.toml` 的 `[sources]` 中可启用/禁用各数据源：

```toml
[sources]
enabled = [
    "semantic_scholar",
    "openalex",
    "crossref",
    "pubmed",
    "arxiv",
    "core",
    "chemrxiv",
]
```

---

## 多维复合检索 ✨

`paper-dl search` 支持将多个检索维度**同时组合使用**，各条件之间为 AND 关系，可精准缩小结果范围。

### 支持的检索维度

| 维度 | 选项 | 说明 |
|------|------|------|
| 关键词 | `-q / --query` | 全文/摘要关键词 |
| 作者 | `-a / --author` | 作者姓名（支持模糊匹配评分） |
| 标题 | `-t / --title` | 论文标题关键词 |
| DOI | `-d / --doi` | 精确 DOI 匹配 |
| 年份范围 | `--year-from / --year-to` | 发表年份区间（含两端） |
| 仅开放获取 | `--oa-only` | 过滤出可免费获取全文的论文 |
| 指定数据源 | `--source` | 逗号分隔，如 `arxiv,openalex` |
| 排序方式 | `--sort` | `relevance`（默认）/ `date` / `citations` |
| 作者匹配阈值 | `--min-author-score` | 配合 `-a` 使用，过滤低置信结果 |

### 典型多维检索示例

```bash
# 示例 1：关键词 + 年份范围 + 仅 OA + 下载
paper-dl search -q "solid electrolyte interface" \
    --year-from 2020 --year-to 2024 \
    --oa-only --download --output-dir ./sei_papers

# 示例 2：作者 + 关键词 + 年份 + 作者匹配过滤 + 下载
paper-dl search -a "John Newman" -q "electrochemical" \
    --year-from 2015 --year-to 2023 \
    --min-author-score 0.70 -n 50 --download

# 示例 3：关键词 + 标题 + 年份 + 指定数据源 + 按引用数排序
paper-dl search -q "transformer attention mechanism" \
    -t "attention is all you need" \
    --year-from 2017 \
    --source semantic_scholar,openalex,crossref \
    --sort citations -n 20

# 示例 4：作者 + 年份 + 仅 OA + 指定化学预印本源
paper-dl search -a "Omar Yaghi" \
    --year-from 2022 --year-to 2024 \
    --oa-only --source chemrxiv,openalex \
    -n 30 --download

# 示例 5：关键词 + 仅 OA + 多源并发 + 下载（最大覆盖面）
paper-dl search -q "COVID-19 vaccine mRNA" \
    --year-from 2020 --oa-only \
    --source pubmed,openalex,semantic_scholar,core \
    --sort citations -n 100 --download --output-dir ./covid_papers
```

### 各数据源的多维支持情况

| 数据源 | 关键词 | 作者 | 标题 | DOI | 年份范围 | 实现方式 |
|--------|:------:|:----:|:----:|:---:|:--------:|----------|
| Semantic Scholar | ✅ | ✅ | ✅ | ✅ | ✅ | 多字段拼合查询 |
| OpenAlex | ✅ | ✅ | ✅ | ✅ | ✅ | 独立 filter 参数（AND） |
| CrossRef | ✅ | ✅ | ✅ | ✅ | ✅ | 多字段独立参数（AND） |
| PubMed | ✅ | ✅ | ✅ | ✅ | ✅ | 结构化布尔查询（`[Field]` 标签） |
| arXiv | ✅ | ✅ | ✅ | ✅ | ✅ | 布尔表达式（`ti: AND au:`） |
| CORE | ✅ | ✅ | ✅ | ✅ | — | 多字段拼合查询 |
| ChemRxiv | ✅ | ✅ | ✅ | ✅ | ✅ | 独立 filter 参数（AND） |

> **说明：** CrossRef、OpenAlex、PubMed 和 arXiv 支持真正的多字段 AND 查询，精度最高；Semantic Scholar 和 CORE 对多字段条件会合并为单一文本检索，精度略低，但仍可通过**作者匹配后处理评分**二次过滤。

### 多维检索的内部流程

```
输入条件（query + author + title + year + oa_only + source）
        │
        ▼
  并发调用所有激活的数据源适配器（asyncio.gather）
        │
        ▼
  跨源去重合并（DOI 优先，否则 title+author+year 哈希）
        │
        ▼
  作者匹配评分（若指定 -a，对全部结果打分并降序排列）
        │
        ▼
  --min-author-score 阈值过滤（可选）
        │
        ▼
  --oa-only 过滤（可选）
        │
        ▼
  max_results 截断 → 输出结果 / 触发下载
```

---

## 作者匹配度验证 ✨

使用 `-a` 按作者检索时，工具会自动对每篇结果计算**作者匹配分数**（0.0 ~ 1.0），并在结果表格中以彩色显示：

- 🟢 ≥ 0.80：高置信匹配（姓氏完全一致 + 名字相似）
- 🟡 0.50 ~ 0.79：中等置信（姓氏基本一致）
- 🔴 < 0.50：低置信（可能为同姓不同人）

结果默认按匹配分数从高到低排列。

**按阈值过滤**，可通过 `--min-author-score` 参数或配置文件控制：

```bash
# 命令行：仅保留分数 ≥ 0.70 的结果
paper-dl search -a "John Smith" -n 100 --min-author-score 0.70
```

```toml
# paper_dl.toml：全局设置过滤阈值（0.0 = 仅标注，不过滤）
[filters]
author_match_threshold = 0.60
```

---

## 输出结构

```
papers/
├── 2017_vaswani_attention_all_you_need_1706.03762/
│   ├── metadata.json    # 结构化元数据（含作者匹配分数）
│   ├── paper.md         # MarkItDown 转换的 Markdown（含 YAML front matter）
│   └── paper.pdf        # 原始 PDF（若已下载全文）
├── _index.md            # 论文索引（Markdown 表格）
├── _index.json          # 论文索引（JSON）
└── _download_log.db     # 下载历史 SQLite 数据库
```

---

## 配置文件

复制 `paper_dl.toml.example` 为 `paper_dl.toml` 并编辑。各主要配置节说明：

| 配置节 | 说明 |
|--------|------|
| `[general]` | 输出目录、默认结果数、排序方式 |
| `[download]` | 并发数、超时、重试次数、User-Agent |
| `[sources]` | 启用的数据源列表 |
| `[api_keys]` | Semantic Scholar / PubMed / CORE / Unpaywall 邮箱 |
| `[markitdown]` | MarkItDown 格式转换开关 |
| `[filters]` | OA 过滤、年份范围、**作者匹配阈值** |
| `[scihub]` | Sci-Hub fallback 配置（默认关闭，见下方说明） |

`unpaywall_email` 为必填项（用于 Unpaywall API 标识）。

---

## Sci-Hub Fallback（可选）⚠️

> **法律提示：** Sci-Hub 在美国、欧盟等地区属于版权侵权行为。使用前请确认您所在地区的法律状况及机构网络使用政策。建议优先通过合法 OA 渠道获取全文。

本工具支持将 Sci-Hub 作为**最后手段**的下载 fallback：当所有合法 OA 渠道均无法获取全文时，若用户显式启用，则尝试通过 Sci-Hub 下载。

**启用步骤：**

```bash
# 1. 安装 scidownl（需额外安装）
pip install paper-dl[scihub]
```

```toml
# 2. 在 paper_dl.toml 中启用
[scihub]
enabled = true
proxy = ""   # 如需代理："socks5://127.0.0.1:7890"
```

---

## 所有 CLI 命令

```
paper-dl search    检索论文（支持关键词/作者/标题/DOI）
paper-dl download  通过 DOI 或 URL 直接下载单篇论文
paper-dl batch     从文件批量执行检索+下载任务
paper-dl convert   将本地 PDF/HTML/DOCX 转换为 Markdown
paper-dl history   查询下载历史记录（list / stats）
paper-dl config    配置管理（init / show）
```

**`paper-dl search` 主要选项：**

| 选项 | 说明 |
|------|------|
| `-q`, `--query` | 关键词检索 |
| `-a`, `--author` | 作者名检索 |
| `-t`, `--title` | 题目检索 |
| `-d`, `--doi` | DOI 精确检索 |
| `-n`, `--max-results` | 最大结果数（默认 20） |
| `--year-from` / `--year-to` | 发表年份范围 |
| `--source` | 指定数据源（逗号分隔，如 `arxiv,chemrxiv`） |
| `--sort` | 排序：`relevance` / `date` / `citations` |
| `--oa-only` | 仅返回开放获取论文 |
| `--min-author-score` | 最低作者匹配分数（0.0~1.0）✨ |
| `--download` | 检索后自动下载 |
| `--output-dir` | 输出目录（默认 `./papers`） |
| `--format` | 结果格式：`table` / `json` / `md` |
| `--dry-run` | 模拟运行，不实际下载 |

---

## 合规声明

本工具默认仅通过以下合法开放获取渠道下载全文：Unpaywall、PubMed Central、arXiv、OpenAlex、Semantic Scholar、CORE、ChemRxiv。下载内容仅供个人学术研究使用。Sci-Hub 功能需用户显式启用，并由用户自行承担相关法律责任。
