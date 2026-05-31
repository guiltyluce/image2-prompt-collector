# Image2 Prompt Collector / image2-prompt-collector

[中文](README.md) | English

`image2-prompt-collector` is a Skill for operating an AI image-prompt asset library. It collects reusable public image-generation prompts and example images, applies quality checks, deduplicates and tags records, then imports them into Feishu Bitable or keeps them in a local candidate queue.

## Use Cases

- Build a GPT Image 2 / image2 prompt case library.
- Collect high-performing image prompts from public communities.
- Add titles, tags, usage notes, and attribution to prompts.
- Import high-quality prompts with example images into Feishu Bitable.
- Maintain queues such as "needs image", "duplicate", and "risk review".

## Core Capabilities

- Public-source collection rules.
- Prompt quality gates.
- Required example-image checks.
- Deduplication by source URL and prompt hash.
- Tagging by style, use case, platform, and status.
- Feishu Bitable import and attachment upload.
- Dry-run reports to avoid accidental writes.

## Repository Layout

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

## Quick Check

```bash
python3 scripts/validate_skill_package.py --zip
python3 -m py_compile scripts/import_candidates.py
python3 scripts/import_candidates.py --help
```

## Import Example

```bash
export FEISHU_BASE_TOKEN="your_base_token"
export FEISHU_TABLE_ID="your_table_id"

python3 scripts/import_candidates.py \
  --candidates ./prompt-gallery-intake/candidates.json \
  --workspace . \
  --dry-run
```

## Skill Installation

The distributable Skill package is located at:

```text
skill/image2-prompt-collector/image2-prompt-collector.zip
```

Install it into the local Skill directory:

```bash
mkdir -p ~/.codex/skills
unzip -o skill/image2-prompt-collector/image2-prompt-collector.zip -d ~/.codex/skills/
```

## License

MIT
