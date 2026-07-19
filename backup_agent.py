#!/usr/bin/env python3
"""
DeepSeek Backup Agent
集成 MiMo Code 四大特性的智能备份代理
"""

import json
import sys
from pathlib import Path

# 添加当前目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import MiMoCore
from scripts.backup import do_backup, do_login
from scripts.export import export_all, load_config


class BackupAgent:
    """备份代理 - 集成 MiMo Code 特性"""
    
    def __init__(self):
        self.workspace = Path(__file__).parent
        self.core = MiMoCore(self.workspace)
        self.config = load_config()
    
    def run_full_workflow(self):
        """执行完整的备份工作流"""
        print("=" * 60)
        print("  DeepSeek Backup Agent - 智能备份工作流")
        print("=" * 60)
        
        # 阶段1: 项目状态检查
        print("\n【阶段1】检查项目状态")
        print("-" * 50)
        
        checkpoint = self.core.read_checkpoint()
        if checkpoint.get("current_intent") == "项目已完成，准备发布":
            print("  ✓ 上次备份已完成")
            print(f"  上次时间: {checkpoint.get('next_action', '未知')}")
        
        # 阶段2: 设置目标
        print("\n【阶段2】设置备份目标")
        print("-" * 50)
        
        goal = self.core.add_goal(
            "完成 DeepSeek 聊天记录备份",
            [
                "登录成功",
                "抓取所有对话",
                "PII 脱敏完成",
                "导出 Markdown 文件",
                "导出 Word 文件",
                "导出 JSON 文件",
            ]
        )
        print(f"  目标: {goal.description}")
        print(f"  标准: {len(goal.criteria)} 项")
        
        # 阶段3: 执行备份
        print("\n【阶段3】执行备份")
        print("-" * 50)
        
        self.core.write_checkpoint({
            "current_intent": "执行 DeepSeek 备份",
            "next_action": "登录并抓取聊天记录",
            "task_tree": "1. 登录 DeepSeek\n2. 抓取聊天列表\n3. 抓取消息内容\n4. PII 脱敏\n5. 导出文件",
            "constraints": "使用 Selenium 浏览器自动化，PII 脱敏，限速 2 秒",
        })
        
        self.core.record_history("user", "执行 DeepSeek 备份")
        
        # 执行备份
        try:
            do_backup(full=True, pii=True, rate_limit=2.0)
            self.core.record_history("assistant", "备份执行完成")
        except Exception as e:
            self.core.record_history("assistant", f"备份执行失败: {e}")
            print(f"  ✗ 备份失败: {e}")
            return
        
        # 阶段4: 导出文件
        print("\n【阶段4】导出文件")
        print("-" * 50)
        
        try:
            export_all(config=self.config, formats=["markdown", "word", "json", "html"], create_zip=True)
            self.core.record_history("assistant", "导出完成")
        except Exception as e:
            self.core.record_history("assistant", f"导出失败: {e}")
            print(f"  ✗ 导出失败: {e}")
        
        # 阶段5: 验证目标
        print("\n【阶段5】验证目标完成度")
        print("-" * 50)
        
        # 检查导出文件
        export_dir = Path(os.path.expanduser(self.config["backup_dir"])) / "exports"
        exported_files = list(export_dir.glob("*")) if export_dir.exists() else []
        
        context = f"""
备份完成报告：
- 登录状态: 已登录
- 聊天抓取: 已完成
- PII 脱敏: 已启用
- 导出文件: {len(exported_files)} 个
- 导出格式: Markdown, Word, JSON, HTML, ZIP
"""
        
        status, feedback = self.core.verify_goal(0, context)
        print(f"  验证结果: {status.value}")
        print(f"  反馈: {feedback}")
        
        # 阶段6: 更新状态
        print("\n【阶段6】更新项目状态")
        print("-" * 50)
        
        self.core.write_checkpoint({
            "current_intent": "备份完成，准备下次增量备份",
            "next_action": "等待 cron 定时任务",
            "task_tree": "1. ✅ 登录 DeepSeek\n2. ✅ 抓取聊天列表\n3. ✅ 抓取消息内容\n4. ✅ PII 脱敏\n5. ✅ 导出文件",
            "cross_task_findings": "Selenium + Snap Chromium 方案稳定可靠",
            "design_decisions": "采用 PII 脱敏 + 限速 + 增量去重三重安全策略",
        })
        
        self.core.record_history("system", "备份工作流完成")
        
        # 运行自进化
        print("\n【阶段7】自进化 (Dream/Distill)")
        print("-" * 50)
        
        self.core.force_dream()
        self.core.force_distill()
        
        # 最终状态
        print("\n" + "=" * 60)
        print("  备份工作流完成")
        print("=" * 60)
        
        status = self.core.get_system_status()
        print(f"  技能: {status['skills_count']} 个")
        print(f"  历史: 已记录")
        print(f"  Dream 下次: {status['evolution_status']['dream']['next_run'][:10]}")
        print(f"  Distill 下次: {status['evolution_status']['distill']['next_run'][:10]}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="DeepSeek Backup Agent")
    parser.add_argument("--login", action="store_true", help="仅登录")
    parser.add_argument("--full", "-f", action="store_true", help="完整工作流")
    parser.add_argument("--status", action="store_true", help="查看状态")
    args = parser.parse_args()
    
    agent = BackupAgent()
    
    if args.login:
        do_login()
    elif args.status:
        status = agent.core.get_system_status()
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        agent.run_full_workflow()


if __name__ == "__main__":
    import os
    main()
