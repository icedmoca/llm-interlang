#!/usr/bin/env python3
"""
ChatGPT Chromium Bridge
Two modes:
  1. xdotool (default) — works with any existing Chromium window, no restart needed
  2. cdp               — uses Playwright CDP, more reliable DOM access

Usage:
  python3 chatgpt_bridge.py "your message"
  python3 chatgpt_bridge.py --mode cdp "your message"
  python3 chatgpt_bridge.py --wait 60 "your message"

CDP mode requires:
  pip install playwright && playwright install chromium
  chromium --remote-debugging-port=9222 https://chatgpt.com
"""

import argparse, subprocess, sys, time


def run(cmd):
    subprocess.run(cmd, capture_output=True)

def clipboard_get():
    return subprocess.run(["xclip", "-selection", "clipboard", "-o"],
                          capture_output=True, text=True).stdout

def clipboard_set(text):
    proc = subprocess.Popen(["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE)
    proc.communicate(text.encode())


# ── xdotool mode ────────────────────────────────────────────────────────────

def xdotool_find_window():
    for args in [["--name", "ChatGPT"], ["--class", "chromium"], ["--class", "google-chrome"]]:
        out = subprocess.run(["xdotool", "search"] + args,
                             capture_output=True, text=True).stdout.strip()
        if out:
            return out.splitlines()[0]
    return None

def xdotool_send(message, wait_seconds=30):
    wid = xdotool_find_window()
    if not wid:
        sys.exit("ERROR: No Chromium/ChatGPT window found.")
    print(f"[xdotool] Window: {wid}")

    subprocess.run(["xdotool", "windowactivate", "--sync", wid])
    subprocess.run(["xdotool", "windowraise", wid])
    time.sleep(0.3)

    # Put message in clipboard to handle special chars
    clipboard_set(message)
    time.sleep(0.1)

    # Use address bar to run JS that focuses the ChatGPT input
    js = "javascript:void(document.querySelector('#prompt-textarea,div[contenteditable=true]').focus())"
    subprocess.run(["xdotool", "key", "--window", wid, "ctrl+l"])
    time.sleep(0.3)
    subprocess.run(["xdotool", "type", "--window", wid, "--clearmodifiers", js])
    time.sleep(0.1)
    subprocess.run(["xdotool", "key", "--window", wid, "Return"])
    time.sleep(0.5)

    # Paste and send
    subprocess.run(["xdotool", "key", "--window", wid, "ctrl+v"])
    time.sleep(0.3)
    subprocess.run(["xdotool", "key", "--window", wid, "Return"])
    print(f"[xdotool] Sent. Waiting {wait_seconds}s...")

    time.sleep(wait_seconds)

    # Select-all, copy, then parse out the reply
    subprocess.run(["xdotool", "key", "--window", wid, "ctrl+a"])
    time.sleep(0.2)
    subprocess.run(["xdotool", "key", "--window", wid, "ctrl+c"])
    time.sleep(0.2)
    subprocess.run(["xdotool", "key", "--window", wid, "Escape"])

    page_text = clipboard_get()
    if not page_text:
        return "(clipboard empty)"

    parts = page_text.split(message, maxsplit=1)
    if len(parts) > 1:
        after = parts[1].strip()
        for marker in ["Regenerate", "Copy code", "Share", "Edit message"]:
            idx = after.find(marker)
            if idx != -1:
                after = after[:idx].strip()
        return after
    return page_text


# ── CDP / Playwright mode ────────────────────────────────────────────────────

def cdp_send(message, port=9222, wait_seconds=60):
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        sys.exit("pip install playwright && playwright install chromium")

    with sync_playwright() as p:
        print(f"[cdp] Connecting on port {port}...")
        try:
            browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")
        except Exception as e:
            sys.exit(f"Cannot connect: {e}\nLaunch: chromium --remote-debugging-port={port} https://chatgpt.com")

        # Find the ChatGPT tab
        page = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                if "chatgpt.com" in pg.url or "chat.openai.com" in pg.url:
                    page = pg
                    break
            if page: break

        if page is None:
            pages = [pg for ctx in browser.contexts for pg in ctx.pages]
            if not pages: sys.exit("No pages found.")
            page = pages[0]
            print(f"[cdp] Warning: using {page.url}")

        page.bring_to_front()

        # Find input
        INPUT_SELECTORS = [
            "#prompt-textarea",
            "div[contenteditable='true'][data-id]",
            "div.ProseMirror[contenteditable='true']",
            "textarea[placeholder]",
        ]
        input_el = None
        for sel in INPUT_SELECTORS:
            try:
                el = page.wait_for_selector(sel, timeout=5000, state="visible")
                if el:
                    input_el = el
                    print(f"[cdp] Input found: {sel}")
                    break
            except PWTimeout:
                continue

        if not input_el:
            sys.exit("ChatGPT input not found. Is the page loaded?")

        def count_responses():
            return page.eval_on_selector_all(
                "[data-message-author-role='assistant']", "els => els.length")

        initial = count_responses()

        # Clear and insert text
        input_el.click()
        time.sleep(0.2)
        page.keyboard.press("Control+a")
        page.keyboard.press("Delete")
        time.sleep(0.1)

        page.evaluate(f"""
            const el = document.querySelector(
                "#prompt-textarea, div[contenteditable='true'][data-id], div.ProseMirror[contenteditable='true']"
            );
            if (el) {{
                el.focus();
                if (el.tagName === 'TEXTAREA') {{
                    el.value = {repr(message)};
                    el.dispatchEvent(new Event('input', {{bubbles: true}}));
                }} else {{
                    document.execCommand('insertText', false, {repr(message)});
                }}
            }}
        """)
        time.sleep(0.5)

        # Click send or press Enter
        sent = False
        for sel in ["button[data-testid='send-button']",
                    "button[aria-label='Send message']",
                    "button[aria-label='Send prompt']"]:
            btn = page.query_selector(sel)
            if btn and btn.is_enabled():
                btn.click()
                print(f"[cdp] Send button: {sel}")
                sent = True
                break
        if not sent:
            input_el.press("Enter")
            print("[cdp] Pressed Enter.")

        # Wait for new response
        print(f"[cdp] Waiting up to {wait_seconds}s...")
        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if count_responses() > initial: break
            time.sleep(0.5)

        # Wait for streaming to finish
        STOP = "button[aria-label='Stop streaming'],button[data-testid='stop-button']"
        try:
            page.wait_for_selector(STOP, timeout=5000, state="visible")
            page.wait_for_selector(STOP, timeout=wait_seconds * 1000, state="hidden")
            print("[cdp] Stream done.")
        except PWTimeout:
            pass

        time.sleep(0.5)

        response = page.evaluate("""
            () => {
                const msgs = document.querySelectorAll("[data-message-author-role='assistant']");
                if (!msgs.length) return null;
                const last = msgs[msgs.length - 1];
                return (last.querySelector('.markdown,.prose') || last).innerText.trim();
            }
        """)
        browser.close()
        return response or "(no response found)"


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("message")
    parser.add_argument("--mode", choices=["xdotool", "cdp"], default="xdotool")
    parser.add_argument("--wait", type=int, default=30)
    parser.add_argument("--cdp-port", type=int, default=9222)
    args = parser.parse_args()

    print(f"Mode: {args.mode} | Message: {args.message!r}\n")

    if args.mode == "cdp":
        r = cdp_send(args.message, port=args.cdp_port, wait_seconds=args.wait)
    else:
        r = xdotool_send(args.message, wait_seconds=args.wait)

    print("\n" + "=" * 60 + "\nRESPONSE:\n" + "=" * 60)
    print(r if isinstance(r, str) else str(r))

if __name__ == "__main__":
    main()
