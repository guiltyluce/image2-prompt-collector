---
name: image2-prompt-collector
description: AI生图（image2）爆款提示词收集助手：收集公开可复用的 AI 生图提示词与例图，完成质量筛选、去重、标签化和飞书多维表入库；适用于 GPT Image 2、图像生成案例库和提示词资产运营。
---

# AI生图（image2）爆款提示词收集助手

GitHub: [guiltyluce/image2-prompt-collector](https://github.com/guiltyluce/image2-prompt-collector)

用于长期运营 AI 生图提示词资产库。它从公开来源或用户提供的材料中收集提示词和例图，筛掉低质量、重复、无图或风险较高的候选，再写入飞书多维表或本地候选队列。

# 触发场景

用户出现以下意图时使用：

- 收集 GPT Image 2 / image2 / AI 生图提示词。
- 维护提示词画廊、案例库、素材库。
- 从 GitHub、Reddit、X/Twitter、小红书、博客等公开来源筛选爆款提示词。
- 对候选提示词做去重、打标、质量审核。
- 将合格记录写入飞书多维表。

# 工作原则

主库沉淀可直接复用的图文资产，避免只留下纯文本清单。

每条正式记录至少需要：

- `例图`：可见图片附件。
- `提示词`：完整、可复用的生图提示词。
- `标题`：简短、可读。
- `项目标签`、`类型标签`、`风格标签`、`来源平台`、`资源状态`。
- `来源` 或 `来源链接`：方便回溯。

如果提示词很好但缺例图，先生成或补齐例图；当前环境无法补图时，放入 `needs_image` 队列，不写入主库。

# 工作流程

1. 阅读 `references/library-schema.md`，确认字段规范。
2. 阅读 `references/source-playbook.md`，确认公开来源和质量门槛。
3. 收集候选提示词、例图和来源信息。
4. 归一化为 JSON 数组。
5. 质量筛选：
   - 提示词足够具体。
   - 有明确主体、风格、构图、比例或约束。
   - 有例图，或当前可生成例图。
   - 来源公开或用户授权。
   - 不包含明显侵权、隐私、仿冒真人或不安全内容。
6. 先 dry-run：

```bash
python3 scripts/import_candidates.py \
  --candidates /path/to/candidates.json \
  --workspace /path/to/workspace \
  --base-token "$FEISHU_BASE_TOKEN" \
  --table-id "$FEISHU_TABLE_ID" \
  --dry-run
```

7. dry-run 通过后正式导入：

```bash
python3 scripts/import_candidates.py \
  --candidates /path/to/candidates.json \
  --workspace /path/to/workspace \
  --base-token "$FEISHU_BASE_TOKEN" \
  --table-id "$FEISHU_TABLE_ID"
```

8. 输出新增、重复、缺图、风险候选和失败原因。

# 本地队列建议

```text
prompt-gallery-intake/
├── candidates.json
├── media/
├── needs_image.json
└── import-report.json
```

# 注意事项

- 不为追求数量降低质量门槛。
- 先按来源 URL 和 prompt hash 去重。
- 不抓取私密群聊、付费内容或未授权材料。
- 不把本地图片路径写入用户可见字段。
- 不复制整篇文章，只保存提示词、短标题、例图和来源。
