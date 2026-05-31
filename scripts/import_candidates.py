#!/usr/bin/env python3
"""Import normalized image prompt candidates into a Feishu Base.

This script assumes lark-cli is authenticated as the user. It creates records in
the main prompt gallery table, then uploads the local example image into the
`例图` attachment field. It never writes local paths into the Base.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

ALLOWED_PLATFORM = {"官方/项目整理", "小红书", "X/Twitter", "Reddit", "未提供", "其他"}
ALLOWED_TYPE = {"Prompt", "案例Prompt"}
ALLOWED_STATUS = {"可直接复用", "图片需复核", "缺例图待生成"}
DEFAULT_PROJECT = "public-curation"
DEFAULT_STYLE = "其他应用场景"
DEFAULT_TYPE = "案例Prompt"
DEFAULT_STATUS = "可直接复用"


def is_transient_cli_error(text: str) -> bool:
    lowered = text.lower()
    return any(marker in lowered for marker in (
        " eof",
        "unexpected eof",
        "failed to read response body",
        "connection reset",
        "timeout",
        "temporarily unavailable",
    ))


def run(args: list[str], cwd: Path | None = None) -> dict[str, Any]:
    last_error = ""
    for attempt in range(1, 4):
        cp = subprocess.run(args, cwd=str(cwd) if cwd else None, text=True, capture_output=True)
        if cp.returncode == 0:
            try:
                return json.loads(cp.stdout)
            except json.JSONDecodeError as exc:
                message = f"Command did not return JSON: {' '.join(args)}\n{cp.stdout}"
                if attempt < 3 and is_transient_cli_error(message):
                    time.sleep(0.8 * attempt)
                    continue
                raise RuntimeError(message) from exc

        last_error = f"Command failed: {' '.join(args)}\nSTDOUT:\n{cp.stdout}\nSTDERR:\n{cp.stderr}"
        if attempt < 3 and is_transient_cli_error(last_error):
            time.sleep(0.8 * attempt)
            continue
        raise RuntimeError(last_error)
    raise RuntimeError(last_error)


def fetch_records(base_token: str, table_id: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    offset = 0
    while True:
        data = run([
            "lark-cli", "--as", "user", "base", "+record-list",
            "--base-token", base_token,
            "--table-id", table_id,
            "--offset", str(offset),
            "--limit", "200",
        ])["data"]
        fields = data["fields"]
        for record_id, row in zip(data["record_id_list"], data["data"]):
            records.append({"record_id": record_id, "fields": dict(zip(fields, row))})
        if not data.get("has_more"):
            break
        offset += 200
    return records


def normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "").strip())


def prompt_hash(prompt: str) -> str:
    return hashlib.sha256(normalize_space(prompt).lower().encode("utf-8")).hexdigest()[:16]


def slug_date_id(existing_ids: set[str], index: int) -> str:
    today = time.strftime("%Y%m%d")
    candidate = f"PG-{today}-{index:03d}"
    while candidate in existing_ids:
        index += 1
        candidate = f"PG-{today}-{index:03d}"
    existing_ids.add(candidate)
    return candidate


def resolve_image(path_value: str, workspace: Path, candidates_file: Path) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value).expanduser()
    if not path.is_absolute():
        first = (candidates_file.parent / path).resolve()
        if first.exists():
            return first
        path = (workspace / path).resolve()
    return path if path.exists() else None


def make_record(candidate: dict[str, Any], asset_id: str) -> dict[str, Any]:
    platform = candidate.get("source_platform") or "其他"
    if platform not in ALLOWED_PLATFORM:
        platform = "其他"
    type_tag = candidate.get("type_tag") or DEFAULT_TYPE
    if type_tag not in ALLOWED_TYPE:
        type_tag = DEFAULT_TYPE
    status = candidate.get("resource_status") or DEFAULT_STATUS
    if status not in ALLOWED_STATUS:
        status = DEFAULT_STATUS
    title = normalize_space(candidate["title"])[:120]
    prompt = str(candidate["prompt"]).strip()
    usage = candidate.get("usage_note") or f"{candidate.get('style_tag') or DEFAULT_STYLE}｜{title}。复制提示词后替换主题、主体、场景和比例。"
    return {
        "资产ID": asset_id,
        "标题": title,
        "提示词": prompt,
        "项目标签": candidate.get("project_tag") or DEFAULT_PROJECT,
        "类型标签": type_tag,
        "风格标签": candidate.get("style_tag") or DEFAULT_STYLE,
        "来源平台": platform,
        "来源": candidate.get("source") or "",
        "来源链接": candidate.get("source_url") or "",
        "尺寸或比例": candidate.get("size_or_ratio") or "",
        "资源状态": status,
        "精选": bool(candidate.get("featured", False)),
        "用途说明": usage,
        "备注": candidate.get("notes") or f"Imported by image2-prompt-collector on {time.strftime('%Y-%m-%d')}",
    }


def batch_create(base_token: str, table_id: str, records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not records:
        return []
    endpoint = f"/open-apis/bitable/v1/apps/{base_token}/tables/{table_id}/records/batch_create"
    created: list[dict[str, Any]] = []
    for start in range(0, len(records), 20):
        batch = records[start:start + 20]
        body = {"records": [{"fields": record} for record in batch]}
        data = run(["lark-cli", "--as", "user", "api", "POST", endpoint, "--data", json.dumps(body, ensure_ascii=False)])
        if data.get("code") != 0:
            raise RuntimeError(json.dumps(data, ensure_ascii=False, indent=2))
        for source, result in zip(batch, data["data"]["records"]):
            created.append({"record_id": result.get("record_id") or result.get("id"), "fields": source})
        time.sleep(0.2)
    return created


def upload_attachment(
    base_token: str,
    table_id: str,
    attachment_field: str,
    record_id: str,
    image_path: Path,
    workspace: Path,
) -> None:
    try:
        rel = "./" + str(image_path.resolve().relative_to(workspace.resolve()))
        cwd = workspace
    except ValueError:
        rel = str(image_path.resolve())
        cwd = image_path.parent
        rel = "./" + image_path.name
    run([
        "lark-cli", "--as", "user", "base", "+record-upload-attachment",
        "--base-token", base_token,
        "--table-id", table_id,
        "--record-id", record_id,
        "--field-id", attachment_field,
        "--file", rel,
        "--name", image_path.name,
    ], cwd=cwd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", required=True, help="JSON array of normalized candidates")
    parser.add_argument("--workspace", default=".")
    parser.add_argument("--base-token", default=os.getenv("FEISHU_BASE_TOKEN", ""))
    parser.add_argument("--table-id", default=os.getenv("FEISHU_TABLE_ID", ""))
    parser.add_argument("--attachment-field", default=os.getenv("FEISHU_ATTACHMENT_FIELD", "例图"))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report", default="")
    args = parser.parse_args()

    workspace = Path(args.workspace).expanduser().resolve()
    candidates_file = Path(args.candidates).expanduser().resolve()
    candidates = json.loads(candidates_file.read_text(encoding="utf-8"))
    if not isinstance(candidates, list):
        raise SystemExit("Candidates file must be a JSON array.")

    base_token = args.base_token.strip()
    table_id = args.table_id.strip()
    attachment_field = args.attachment_field.strip() or "例图"
    if not base_token or not table_id:
        raise SystemExit("Set --base-token and --table-id, or env FEISHU_BASE_TOKEN / FEISHU_TABLE_ID.")

    existing = fetch_records(base_token, table_id)
    existing_ids = {str(row["fields"].get("资产ID", "")) for row in existing}
    existing_urls = {str(row["fields"].get("来源链接", "")).strip() for row in existing if row["fields"].get("来源链接")}
    existing_hashes = {prompt_hash(str(row["fields"].get("提示词", ""))) for row in existing if row["fields"].get("提示词")}

    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    next_index = len(existing_ids) + 1

    for candidate in candidates:
        title = candidate.get("title")
        prompt = candidate.get("prompt")
        image = resolve_image(candidate.get("image_path", ""), workspace, candidates_file)
        source_url = str(candidate.get("source_url") or "").strip()
        reasons: list[str] = []
        if not title:
            reasons.append("missing title")
        if not prompt or len(str(prompt).strip()) < 40:
            reasons.append("missing or weak prompt")
        if not image:
            reasons.append("missing local image")
        if source_url and source_url in existing_urls:
            reasons.append("duplicate source_url")
        if prompt and prompt_hash(str(prompt)) in existing_hashes:
            reasons.append("duplicate prompt")
        if reasons:
            rejected.append({"candidate": candidate, "reasons": reasons})
            continue
        asset_id = slug_date_id(existing_ids, next_index)
        next_index += 1
        accepted.append({"record": make_record(candidate, asset_id), "image_path": str(image)})
        existing_hashes.add(prompt_hash(str(prompt)))
        if source_url:
            existing_urls.add(source_url)

    report = {"accepted": accepted, "rejected": rejected, "dry_run": args.dry_run}
    report_path = Path(args.report).expanduser() if args.report else candidates_file.with_name("import-report.json")

    if args.dry_run:
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"accepted": len(accepted), "rejected": len(rejected), "report": str(report_path)}, ensure_ascii=False))
        return 0

    created = batch_create(base_token, table_id, [item["record"] for item in accepted])
    uploaded = []
    for item, result in zip(accepted, created):
        upload_attachment(base_token, table_id, attachment_field, result["record_id"], Path(item["image_path"]), workspace)
        uploaded.append({"record_id": result["record_id"], "asset_id": item["record"]["资产ID"], "image_path": item["image_path"]})
        time.sleep(0.25)

    report["created"] = created
    report["uploaded"] = uploaded
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"created": len(created), "uploaded": len(uploaded), "rejected": len(rejected), "report": str(report_path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
