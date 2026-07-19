#!/usr/bin/env python3
"""
调度器：管理 DeepSeek 聊天记录备份的定时任务。
支持首次全量备份和后续每日增量备份。
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def load_config(config_path: str = None) -> dict:
    if config_path is None:
        config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_backup_dir(config: dict) -> Path:
    return Path(os.path.expanduser(config["backup_dir"]))


def is_first_run(config: dict) -> bool:
    """判断是否为首次运行。"""
    backup_dir = get_backup_dir(config)
    state_file = backup_dir / ".backup_state.json"
    return not state_file.exists()


def run_backup(config: dict, full_backup: bool = False):
    """执行备份。"""
    script_dir = Path(__file__).parent
    backup_script = script_dir / "backup.py"
    export_script = script_dir / "export.py"

    print(f"\n{'='*50}")
    print(f"开始备份 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模式: {'全量备份' if full_backup else '增量备份'}")
    print(f"{'='*50}\n")

    # 运行备份脚本
    cmd = [sys.executable, str(backup_script)]
    if full_backup:
        cmd.append("--full")

    # 如果有 cookie 文件，传入参数
    backup_dir = get_backup_dir(config)
    cookie_file = backup_dir / "cookies.json"
    if cookie_file.exists():
        cmd.extend(["--cookie", str(cookie_file)])

    result = subprocess.run(cmd, cwd=str(script_dir))

    if result.returncode == 0:
        # 运行导出脚本
        print("\n[i] 开始导出...")
        subprocess.run([sys.executable, str(export_script)], cwd=str(script_dir))
    else:
        print(f"[✗] 备份失败，退出码: {result.returncode}")


def install_cron(config: dict):
    """安装 cron 定时任务。"""
    script_dir = Path(__file__).parent
    backup_script = script_dir / "backup.py"
    export_script = script_dir / "export.py"
    python_path = sys.executable

    # cron 命令：每天凌晨2点执行增量备份和导出
    cron_cmd = f"0 2 * * * cd {script_dir} && {python_path} {backup_script} && {python_path} {export_script} >> {get_backup_dir(config)}/backup.log 2>&1"

    # 检查是否已存在
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    current_cron = result.stdout if result.returncode == 0 else ""

    marker = "# deepseek-backup auto"
    if marker in current_cron:
        # 更新已有的 cron 任务
        lines = current_cron.split("\n")
        new_lines = [l for l in lines if marker not in l and "deepseek-backup" not in l]
        new_lines.append(f"{cron_cmd}  {marker}")
        new_cron = "\n".join(new_lines)
    else:
        # 添加新的 cron 任务
        new_cron = current_cron.rstrip() + "\n" + cron_cmd + "  " + marker + "\n"

    # 写入新的 crontab
    process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    process.communicate(input=new_cron)

    if process.returncode == 0:
        print(f"[✓] Cron 任务已安装")
        print(f"    执行时间: 每天凌晨 2:00")
        print(f"    日志文件: {get_backup_dir(config)}/backup.log")
    else:
        print("[✗] Cron 任务安装失败")


def uninstall_cron():
    """卸载 cron 定时任务。"""
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode != 0:
        print("[i] 没有找到 crontab")
        return

    lines = result.stdout.split("\n")
    new_lines = [l for l in lines if "deepseek-backup" not in l]
    new_cron = "\n".join(new_lines)

    process = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE, text=True)
    process.communicate(input=new_cron)

    print("[✓] Cron 任务已卸载")


def show_status(config: dict):
    """显示当前备份状态。"""
    backup_dir = get_backup_dir(config)
    state_file = backup_dir / ".backup_state.json"

    print(f"\n{'='*50}")
    print(f"DeepSeek 备份状态")
    print(f"{'='*50}")
    print(f"备份目录: {backup_dir}")

    if state_file.exists():
        with open(state_file, "r", encoding="utf-8") as f:
            state = json.load(f)
        print(f"上次备份: {state.get('last_backup_time', '从未')}")
        print(f"已备份聊天: {len(state.get('chat_ids', {}))} 个")
    else:
        print("状态: 从未备份")

    # 检查导出文件
    export_dir = backup_dir / "exports"
    if export_dir.exists():
        exports = list(export_dir.glob("*"))
        print(f"导出文件: {len(exports)} 个")
        for f in sorted(exports)[-3:]:  # 显示最近3个
            print(f"  - {f.name}")
    else:
        print("导出文件: 0 个")

    # 检查 cron
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    if result.returncode == 0 and "deepseek-backup" in result.stdout:
        print(f"定时任务: ✓ 已安装 (每天凌晨2:00)")
    else:
        print(f"定时任务: ✗ 未安装")

    print(f"{'='*50}\n")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DeepSeek 聊天记录备份调度器")
    parser.add_argument("action", choices=["run", "full", "install-cron", "uninstall-cron", "status"],
                        help="执行操作")
    parser.add_argument("--config", "-c", help="配置文件路径", default=None)
    args = parser.parse_args()

    config = load_config(args.config)

    if args.action == "run":
        # 增量备份
        run_backup(config, full_backup=False)
    elif args.action == "full":
        # 全量备份
        run_backup(config, full_backup=True)
    elif args.action == "install-cron":
        install_cron(config)
    elif args.action == "uninstall-cron":
        uninstall_cron()
    elif args.action == "status":
        show_status(config)


if __name__ == "__main__":
    main()
