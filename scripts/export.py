#!/usr/bin/env python3
"""
导出模块：将 DeepSeek 聊天记录导出为 Markdown 和 Word 格式。
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List

import yaml
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH


def load_config(config_path: str = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_all_chats(backup_dir: Path) -> List[dict]:
    """加载所有已备份的聊天 JSON 文件。"""
    chats = []
    json_dir = backup_dir / "json"
    if not json_dir.exists():
        return chats

    for f in sorted(json_dir.glob("*.json")):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                chats.append(data)
        except Exception as e:
            print(f"[!] 加载失败: {f.name} - {e}")
    return chats


def export_markdown(chats: List[dict], output_path: Path, config: dict):
    """导出为 Markdown 格式。"""
    lines = []
    lines.append("# DeepSeek 聊天记录备份\n")
    lines.append(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    lines.append(f"共 {len(chats)} 个对话\n")
    lines.append("---\n")

    for chat in chats:
        title = chat.get("title", "未命名对话")
        chat_id = chat.get("chat_id", "")
        scraped_at = chat.get("scraped_at", "")
        messages = chat.get("messages", [])

        lines.append(f"\n## {title}\n")
        lines.append(f"- **对话ID**: `{chat_id}`")
        if scraped_at:
            lines.append(f"- **抓取时间**: {scraped_at}")
        lines.append(f"- **消息数**: {len(messages)}")
        lines.append("")

        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")

            role_label = "🤖 Assistant" if role == "assistant" else "👤 User" if role == "user" else f"❓ {role}"

            lines.append(f"### {role_label}\n")
            if timestamp and config.get("markdown", {}).get("include_timestamps", True):
                lines.append(f"*{timestamp}*\n")
            lines.append(f"{content}\n")
            lines.append("---\n")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"[✓] Markdown 导出完成: {output_path}")


def export_word(chats: List[dict], output_path: Path, config: dict):
    """导出为 Word 格式。"""
    doc = Document()

    # 设置默认字体
    style = doc.styles["Normal"]
    font = style.font
    font.name = config.get("word", {}).get("font_name", "微软雅黑")
    font.size = Pt(config.get("word", {}).get("font_size", 11))

    # 标题
    title = doc.add_heading("DeepSeek 聊天记录备份", level=0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # 元信息
    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = meta.add_run(f"备份时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 共 {len(chats)} 个对话")
    run.font.size = Pt(10)
    run.font.color.rgb = RGBColor(128, 128, 128)

    doc.add_page_break()

    # 目录页
    doc.add_heading("目录", level=1)
    for i, chat in enumerate(chats, 1):
        title_text = chat.get("title", "未命名对话")
        p = doc.add_paragraph(f"{i}. {title_text}")
        p.paragraph_format.space_after = Pt(2)

    doc.add_page_break()

    # 每个对话的内容
    for chat in chats:
        title_text = chat.get("title", "未命名对话")
        chat_id = chat.get("chat_id", "")
        scraped_at = chat.get("scraped_at", "")
        messages = chat.get("messages", [])

        # 对话标题
        doc.add_heading(title_text, level=1)

        # 元信息
        meta_para = doc.add_paragraph()
        if chat_id:
            run = meta_para.add_run(f"对话ID: {chat_id}")
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(128, 128, 128)
        if scraped_at:
            run = meta_para.add_run(f"  |  抓取时间: {scraped_at}")
            run.font.size = Pt(9)
            run.font.color.rgb = RGBColor(128, 128, 128)

        doc.add_paragraph("")  # 空行

        # 消息内容
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")

            # 角色标签
            if role == "assistant":
                role_label = "Assistant"
                color = RGBColor(0, 100, 200)
            elif role == "user":
                role_label = "User"
                color = RGBColor(0, 150, 0)
            else:
                role_label = role
                color = RGBColor(128, 128, 128)

            # 角色标题
            role_heading = doc.add_heading(level=2)
            run = role_heading.add_run(role_label)
            run.font.color.rgb = color
            run.font.size = Pt(12)

            # 时间戳
            if timestamp:
                ts_para = doc.add_paragraph()
                run = ts_para.add_run(timestamp)
                run.font.size = Pt(8)
                run.font.color.rgb = RGBColor(160, 160, 160)

            # 消息内容
            content_para = doc.add_paragraph(content)
            content_para.paragraph_format.space_after = Pt(12)

            # 分隔线
            doc.add_paragraph("─" * 40)

        # 对话之间分页
        doc.add_page_break()

    doc.save(str(output_path))
    print(f"[✓] Word 导出完成: {output_path}")


def export_all(config: dict = None):
    """执行导出操作。"""
    if config is None:
        config = load_config()

    backup_dir = Path(os.path.expanduser(config["backup_dir"]))
    chats = load_all_chats(backup_dir)

    if not chats:
        print("[✗] 没有找到已备份的聊天记录")
        print("    请先运行 backup.py 进行备份")
        return

    print(f"[i] 找到 {len(chats)} 个对话，开始导出...")

    export_dir = backup_dir / "exports"
    export_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    formats = config.get("export_formats", ["markdown", "word"])

    if "markdown" in formats:
        md_path = export_dir / f"deepseek_backup_{timestamp}.md"
        export_markdown(chats, md_path, config)

    if "word" in formats:
        docx_path = export_dir / f"deepseek_backup_{timestamp}.docx"
        export_word(chats, docx_path, config)

    print(f"\n[✓] 所有导出完成！文件位于: {export_dir}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DeepSeek 聊天记录导出工具")
    parser.add_argument("--config", "-c", help="配置文件路径", default=None)
    parser.add_argument("--format", "-f", choices=["markdown", "word", "all"], default="all",
                        help="导出格式")
    args = parser.parse_args()

    config = load_config(args.config)
    if args.format != "all":
        config["export_formats"] = [args.format]

    export_all(config)


if __name__ == "__main__":
    main()
