# AI生图（image2）爆款提示词收集助手 / image2-prompt-collector

`image2-prompt-collector` 是一个用于运营 AI 生图提示词资产库的 Skill。它收集公开可复用的生图提示词和例图，经过质量筛选、去重、标签化后，导入飞书多维表或保存为本地候选队列。

`image2-prompt-collector` is a Skill for operating an AI image-prompt asset library. It collects reusable public image-generation prompts and example images, applies quality checks, deduplicates and tags records, then imports them into Feishu Bitable or keeps them in a local candidate queue.

## 适合场景 / Use Cases

- 建设 GPT Image 2 / image2 提示词案例库。
- Build a GPT Image 2 / image2 prompt case library.
- 从公开社区收集爆款生图提示词。
- Collect high-performing image prompts from public communities.
- 给提示词补标题、标签、用途说明和来源。
- Add titles, tags, usage notes, and attribution to prompts.
- 把有例图的优质提示词导入飞书多维表。
- Import high-quality prompts with example images into Feishu Bitable.
- 维护“缺例图待生成”“重复”“风险复核”等运营队列。
- Maintain queues such as "needs image", "duplicate", and "risk review".

## 核心能力 / Core Capabilities

- 公开来源采集规则。
- Public-source collection rules.
- 提示词质量门槛。
- Prompt quality gates.
- 例图必填检查。
- Required example-image checks.
- 来源 URL 和 prompt hash 去重。
- Deduplication by source URL and prompt hash.
- 风格、用途、平台、状态标签化。
- Tagging by style, use case, platform, and status.
- 飞书多维表导入和附件上传。
- Feishu Bitable import and attachment upload.
- dry-run 报告，避免误写入。
- Dry-run reports to avoid accidental writes.

## 目录 / Repository Layout

```text
.
├── README.md
├── LICENSE
├── references/
│   ├── library-schema.md
│   └── source-playbook.md
├── scripts/
│   ├── import_candidates.py
│   └── validate_skill_package.py
└── skill/
    └── image2-prompt-collector/
        ├── SKILL.md
        └── image2-prompt-collector.zip
```

## 快速检查 / Quick Check

```bash
python3 scripts/validate_skill_package.py --zip
python3 -m py_compile scripts/import_candidates.py
python3 scripts/import_candidates.py --help
```

## 导入示例 / Import Example

```bash
export FEISHU_BASE_TOKEN="your_base_token"
export FEISHU_TABLE_ID="your_table_id"

python3 scripts/import_candidates.py \
  --candidates ./prompt-gallery-intake/candidates.json \
  --workspace . \
  --dry-run
```

## Skill 安装 / Skill Installation

Skill 分发包位置：

The distributable Skill package is located at:

```text
skill/image2-prompt-collector/image2-prompt-collector.zip
```

安装到本地 Skill 目录：

Install it into the local Skill directory:

```bash
mkdir -p ~/.codex/skills
unzip -o skill/image2-prompt-collector/image2-prompt-collector.zip -d ~/.codex/skills/
```

## License

MIT
