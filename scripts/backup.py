#!/usr/bin/env python3
"""
DeepSeek Chat History Backup Tool
使用浏览器 profile 持久化登录态，无需反复登录。
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import yaml
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By


BACKUP_DIR = Path(os.path.expanduser("~/deepseek-backups"))
BROWSER_DATA = BACKUP_DIR / ".browser_data"
STATE_FILE = BACKUP_DIR / ".backup_state.json"
COOKIE_FILE = BACKUP_DIR / "cookies.json"


def load_config():
    config_path = Path(__file__).parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_backup_time": None, "chat_ids": {}}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ========== 浏览器 ==========

def create_driver(headless=False, login_mode=False):
    """创建 WebDriver。login_mode 时使用持久化 profile。"""
    options = Options()
    if headless:
        options.add_argument("--headless=new")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # 登录模式：使用持久化 profile 保存 session
    if login_mode:
        BROWSER_DATA.mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={BROWSER_DATA}")

    # 查找 Chromium
    chrome = "/snap/chromium/current/usr/lib/chromium-browser/chrome"
    chromedriver = "/snap/chromium/current/usr/lib/chromium-browser/chromedriver"
    if os.path.exists(chrome):
        options.binary_location = chrome
        service = Service(executable_path=chromedriver)
        driver = webdriver.Chrome(service=service, options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    })
    return driver


def is_logged_in(driver):
    try:
        for sel in ['textarea', 'div[contenteditable="true"]']:
            for el in driver.find_elements(By.CSS_SELECTOR, sel):
                if el.is_displayed():
                    return True
    except Exception:
        pass
    return False


def try_load_cookies(driver):
    """尝试用 cookie 文件登录。"""
    if not COOKIE_FILE.exists():
        return False
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        driver.get("https://chat.deepseek.com")
        time.sleep(2)
        for c in cookies:
            for k in ["sameSite", "storeId", "id"]:
                c.pop(k, None)
            if "domain" not in c:
                c["domain"] = ".deepseek.com"
            try:
                driver.add_cookie(c)
            except:
                pass
        driver.get("https://chat.deepseek.com")
        time.sleep(3)
        return is_logged_in(driver)
    except:
        return False


def save_cookies(driver):
    """保存 cookie 到文件。"""
    try:
        cookies = driver.get_cookies()
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
        print(f"[✓] Cookie 已保存: {COOKIE_FILE}")
    except Exception as e:
        print(f"[!] 保存 cookie 失败: {e}")


# ========== 抓取 ==========

def scrape_chat_list(driver):
    chats = []
    time.sleep(2)
    try:
        chats = driver.execute_script("""
            const chats = [];
            document.querySelectorAll('a[href*="/chat/"]').forEach(a => {
                const text = a.innerText.trim();
                const href = a.getAttribute('href') || '';
                if (text.length > 1) {
                    chats.push({
                        chat_id: href.split('/chat/')[1]?.split('?')[0] || '',
                        title: text.substring(0, 100),
                        href: href
                    });
                }
            });
            return chats;
        """) or []
    except:
        pass
    if chats:
        print(f"[i] 找到 {len(chats)} 个聊天")
    return chats


def scrape_chat_content(driver, chat_url):
    try:
        driver.get(chat_url)
        time.sleep(4)
        for _ in range(20):
            prev = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(1)
            if driver.execute_script("return document.body.scrollHeight") == prev:
                break
        return driver.execute_script("""
            const msgs = [];
            const sels = ['div[class*="message"]','div[class*="chat-message"]','[data-testid*="message"]'];
            let els = [];
            for (const s of sels) { els = document.querySelectorAll(s); if (els.length) break; }
            if (!els.length) els = document.querySelectorAll('div[class*="role"], div[class*="sender"]');
            els.forEach(el => {
                const text = el.innerText.trim();
                if (!text || text.length < 2) return;
                const cls = el.className || '';
                let role = 'unknown';
                if (cls.includes('user') || cls.includes('human')) role = 'user';
                else if (cls.includes('assistant') || cls.includes('bot') || cls.includes('ai')) role = 'assistant';
                else { const all = document.querySelectorAll('[class*="message"]'); role = Array.from(all).indexOf(el) % 2 === 0 ? 'user' : 'assistant'; }
                msgs.push({ role, content: text });
            });
            return msgs;
        """) or []
    except Exception as e:
        print(f"[✗] 抓取失败: {e}")
        return []


# ========== 登录 ==========

def do_login():
    """打开浏览器让用户登录。"""
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("DeepSeek 登录")
    print("=" * 50)
    print("浏览器即将打开，请登录...")
    print()

    driver = create_driver(headless=False, login_mode=True)
    driver.get("https://chat.deepseek.com")

    print("等待登录... (最长 5 分钟)")
    start = time.time()
    while time.time() - start < 300:
        try:
            if is_logged_in(driver):
                print("[✓] 登录成功！保存 session...")
                save_cookies(driver)
                driver.quit()
                print("完成！现在可以运行备份了：")
                print("  python3 backup.py --full")
                return True
        except:
            pass
        time.sleep(3)

    print("[✗] 超时")
    driver.quit()
    return False


# ========== 备份 ==========

def do_backup(full=False):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    state = load_state()
    is_first = not state.get("last_backup_time")

    # 首次且无 cookie → 需要登录
    if is_first and not COOKIE_FILE.exists():
        return do_login()

    print(f"{'='*50}")
    print(f"DeepSeek 聊天记录备份")
    print(f"模式: {'全量' if full or is_first else '增量'}")
    if state.get("last_backup_time"):
        print(f"上次: {state['last_backup_time']}")
    print(f"{'='*50}\n")

    # 方式1: 用 cookie
    driver = create_driver(headless=True)
    logged_in = False

    if COOKIE_FILE.exists():
        print("[i] 尝试 cookie 登录...")
        logged_in = try_load_cookies(driver)
        if logged_in:
            print("[✓] Cookie 登录成功")
        else:
            print("[✗] Cookie 已过期")

    # 方式2: 用持久化 profile
    if not logged_in:
        driver.quit()
        if BROWSER_DATA.exists():
            print("[i] 尝试 profile 登录...")
            driver = create_driver(headless=True, login_mode=True)
            driver.get("https://chat.deepseek.com")
            time.sleep(3)
            logged_in = is_logged_in(driver)
            if logged_in:
                print("[✓] Profile 登录成功")
                save_cookies(driver)

    if not logged_in:
        driver.quit()
        print("[✗] 未登录，请先运行:")
        print("  python3 backup.py --login")
        return

    # 抓取
    print("\n[i] 抓取聊天列表...")
    chat_list = scrape_chat_list(driver)
    if not chat_list:
        print("[✗] 未找到聊天记录")
        driver.quit()
        return

    existing_chats = {}
    existing_dir = BACKUP_DIR / "json"
    existing_dir.mkdir(exist_ok=True)
    for f in existing_dir.glob("*.json"):
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                existing_chats[data.get("chat_id", f.stem)] = data
        except:
            pass

    new_chats = []
    updated = 0

    for i, chat in enumerate(chat_list):
        chat_id = chat["chat_id"]
        title = chat["title"]

        if not full and chat_id in existing_chats:
            if existing_chats[chat_id].get("title") == title:
                continue

        print(f"[{i+1}/{len(chat_list)}] {title[:50]}...")

        chat_url = chat.get("href", "")
        if chat_url and not chat_url.startswith("http"):
            chat_url = "https://chat.deepseek.com" + chat_url
        elif not chat_url:
            chat_url = f"https://chat.deepseek.com/chat/{chat_id}"

        messages = scrape_chat_content(driver, chat_url)

        chat_data = {
            "chat_id": chat_id,
            "title": title,
            "url": chat_url,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
            "messages": messages,
        }

        if chat_id in existing_chats:
            updated += 1
        else:
            new_chats.append(chat_data)

        safe_id = "".join(c if c.isalnum() or c in "-_" else "_" for c in chat_id)[:60]
        safe_title = "".join(c if c.isalnum() or c in "-_" else "_" for c in title)[:50]
        with open(existing_dir / f"{safe_id}_{safe_title}.json", "w", encoding="utf-8") as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        time.sleep(1)

    driver.quit()

    state["last_backup_time"] = datetime.now(timezone.utc).isoformat()
    for chat in new_chats:
        state["chat_ids"][chat["chat_id"]] = chat["title"]
    save_state(state)

    print(f"\n{'='*50}")
    print(f"完成! 新增 {len(new_chats)} / 更新 {updated} / 总计 {len(state['chat_ids'])}")
    print(f"{'='*50}")

    # 导出
    print("\n导出 Markdown + Word...")
    sys.path.insert(0, str(Path(__file__).parent))
    from export import export_all
    export_all()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="DeepSeek 备份")
    parser.add_argument("--full", "-f", action="store_true", help="全量备份")
    parser.add_argument("--login", action="store_true", help="登录")
    args = parser.parse_args()

    if args.login:
        do_login()
    else:
        do_backup(full=args.full)


if __name__ == "__main__":
    main()
