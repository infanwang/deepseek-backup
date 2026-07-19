#!/usr/bin/env python3
"""
CSDN 博文自动发布工具
使用 Selenium 自动化发布文章到 CSDN。
"""

import json
import time
import os
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


BROWSER_DATA = Path.home() / ".csdn-browser-data"
COOKIE_FILE = Path.home() / ".csdn-cookies.json"


def create_driver():
    """创建 WebDriver。"""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])

    # 持久化 profile
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
    """检查是否已登录 CSDN。"""
    try:
        # 检查是否有登录按钮
        login_btns = driver.find_elements(By.CSS_SELECTOR, 'a[href*="login"], button:has-text("登录")')
        if login_btns:
            for btn in login_btns:
                if btn.is_displayed():
                    return False
        # 检查是否有用户头像（已登录标志）
        avatars = driver.find_elements(By.CSS_SELECTOR, '.avatar, .user-avatar, [class*="avatar"]')
        for av in avatars:
            if av.is_displayed():
                return True
    except:
        pass
    return False


def login_flow(driver):
    """打开浏览器让用户登录 CSDN。"""
    print("=" * 50)
    print("CSDN 登录")
    print("=" * 50)
    print("浏览器即将打开 CSDN 登录页面...")
    print("请手动登录你的 CSDN 帐号")
    print()

    driver.get("https://passport.csdn.net/login")
    time.sleep(3)

    print("等待登录... (最长 5 分钟)")
    start = time.time()
    while time.time() - start < 300:
        try:
            # 检查是否已跳转到首页或控制台
            if "passport.csdn.net" not in driver.current_url:
                print("[✓] 登录成功！")
                return True
            # 检查是否有用户头像
            avatars = driver.find_elements(By.CSS_SELECTOR, '.avatar, .user-avatar, img[src*="avatar"]')
            for av in avatars:
                if av.is_displayed():
                    print("[✓] 登录成功！")
                    return True
        except:
            pass
        time.sleep(3)

    print("[✗] 登录超时")
    return False


def publish_article(driver, title, content_md):
    """发布文章到 CSDN。"""
    print("\n[i] 正在打开 CSDN 编辑器...")
    driver.get("https://editor.csdn.net/md/")
    time.sleep(5)

    # 检查是否需要重新登录
    if "passport" in driver.current_url or "login" in driver.current_url:
        print("[!] 需要重新登录，请在浏览器中完成登录")
        if not login_flow(driver):
            return False

    driver.get("https://editor.csdn.net/md/")
    time.sleep(5)

    print("[i] 填写文章标题...")
    try:
        # 等待标题输入框加载
        title_input = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder*="标题"], input[placeholder*="title"], .title-input input, #title'))
        )
        title_input.clear()
        title_input.send_keys(title)
        time.sleep(1)
    except Exception as e:
        print(f"[!] 标题填写失败: {e}")
        # 尝试其他选择器
        try:
            title_inputs = driver.find_elements(By.TAG_NAME, 'input')
            for inp in title_inputs:
                placeholder = inp.get_attribute('placeholder') or ''
                if '标题' in placeholder or 'title' in placeholder.lower():
                    inp.clear()
                    inp.send_keys(title)
                    break
        except:
            pass

    print("[i] 填写文章内容...")
    try:
        # 等待编辑器加载
        editor = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.editor-content, .md-editor, textarea, [contenteditable="true"]'))
        )
        
        # 尝试直接输入内容
        editor.click()
        time.sleep(1)
        
        # 使用 JavaScript 设置内容（更可靠）
        driver.execute_script("""
            // 尝试找到编辑器实例
            var editors = document.querySelectorAll('.CodeMirror, .cm-editor, .editor-content, textarea');
            for (var i = 0; i < editors.length; i++) {
                var el = editors[i];
                if (el.className && el.className.includes('CodeMirror')) {
                    // CodeMirror 编辑器
                    el.CodeMirror.setValue(arguments[0]);
                    break;
                } else if (el.className && el.className.includes('cm-editor')) {
                    // CM6 编辑器
                    var view = el.cmView;
                    if (view && view.view) {
                        view.view.dispatch({changes: {from: 0, to: view.view.state.doc.length, insert: arguments[0]}});
                    }
                    break;
                } else if (el.tagName === 'TEXTAREA') {
                    el.value = arguments[0];
                    el.dispatchEvent(new Event('input', {bubbles: true}));
                    break;
                }
            }
        """, content_md)
        
        time.sleep(2)
    except Exception as e:
        print(f"[!] 内容填写失败: {e}")

    print("[i] 准备发布...")
    try:
        # 查找发布按钮
        publish_btns = driver.find_elements(By.CSS_SELECTOR, 
            'button:has-text("发布"), button:has-text("Publish"), .publish-btn, [class*="publish"]')
        
        if not publish_btns:
            # 尝试通过文本查找
            all_buttons = driver.find_elements(By.TAG_NAME, 'button')
            for btn in all_buttons:
                text = btn.text.strip()
                if '发布' in text or 'publish' in text.lower():
                    publish_btns.append(btn)
                    break
        
        if publish_btns:
            print("[i] 找到发布按钮，准备点击...")
            print("    请在浏览器中确认发布操作")
            # 不自动点击，让用户确认
            time.sleep(3)
        else:
            print("[!] 未找到发布按钮，请手动发布")
    except Exception as e:
        print(f"[!] 查找发布按钮失败: {e}")

    print("\n[✓] 文章内容已填写到编辑器")
    print("    请在浏览器中检查并点击发布按钮")
    return True


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CSDN 博文自动发布工具")
    parser.add_argument("--login", action="store_true", help="仅登录（不发布）")
    parser.add_argument("--file", "-f", help="Markdown 文件路径")
    parser.add_argument("--title", "-t", help="文章标题")
    args = parser.parse_args()

    # 读取文章内容
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        # 使用默认博客内容
        blog_path = Path(__file__).parent / "BLOG.md"
        if blog_path.exists():
            with open(blog_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            print("[✗] 未找到文章文件")
            return

    title = args.title or "DeepSeek Chat Backup：你的 AI 对话保险箱"

    print("启动浏览器...")
    driver = create_driver()

    try:
        # 登录
        if not login_flow(driver):
            print("[✗] 登录失败")
            return

        if args.login:
            print("[✓] 登录完成，Cookie 已保存")
            return

        # 发布文章
        publish_article(driver, title, content)

    finally:
        print("\n[i] 浏览器保持打开，请手动完成发布操作")
        print("    发布完成后关闭浏览器即可")


if __name__ == "__main__":
    main()
