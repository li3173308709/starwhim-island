#!/usr/bin/env python3
"""Chrome smoke tests for packaged game on desktop and narrow mobile screens.

Checks that actual MP3s, game voice controls, DOM layout, and audio dispatch work.
Playback is intercepted to record routing; this does not substitute for a real
physical device's speaker test.
"""
import base64
import json
import re
from pathlib import Path
from playwright.sync_api import sync_playwright

root = Path(__file__).resolve().parent.parent
html = root / "index.html"
text = html.read_text(encoding="utf-8")
match = re.search(r"window\.StarwhimVoicePack\s*=\s*({.*?});\s*</script>", text, re.S)
assert match, "No voice pack"
clips = json.loads(match.group(1))["audio"]
assert len(clips) >= 194, f"Expected 194 MP3, got {len(clips)}"
for name in ("voice-plan.json", "voice-extra-plan.json", "voice-panel-plan.json"):
    for line in json.loads((root / name).read_text(encoding="utf-8"))["lines"]:
        assert line["text"] in clips, f"{name} misses {line['id']}"
for utterance, uri in clips.items():
    assert uri.startswith("data:audio/mpeg;base64,"), utterance[:30]
    assert len(base64.b64decode(uri.split(",", 1)[1])) > 1000, utterance[:30]

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True, args=["--autoplay-policy=no-user-gesture-required"])
    for profile in [
        dict(name="desktop", width=1440, height=900, is_mobile=False, has_touch=False),
        dict(name="phone-390", width=390, height=844, is_mobile=True, has_touch=True),
        dict(name="phone-360", width=360, height=780, is_mobile=True, has_touch=True),
    ]:
        context = browser.new_context(
            viewport={"width": profile["width"], "height": profile["height"]},
            device_scale_factor=1, is_mobile=profile["is_mobile"],
            has_touch=profile["has_touch"],
        )
        page = context.new_page()
        errors=[]
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.add_init_script("""() => {
           window.__voiceEvents=[];
           const p=HTMLMediaElement.prototype.play;
           HTMLMediaElement.prototype.play=function() {
              window.__voiceEvents.push({src: this.currentSrc || this.src, media: this.tagName});
              return Promise.resolve();
           };
        }""")
        page.goto(html.as_uri(), wait_until="load", timeout=60000)
        page.wait_for_timeout(500)
        assert not errors, f"{profile['name']} script errors: {errors[:3]}"
        assert page.locator("body").count()==1
        # All declared recorded lines accessible in browser; not just Python parse.
        count=page.evaluate("Object.keys(window.StarwhimVoicePack?.audio||{}).length")
        assert count>=194, f"{profile['name']}: browser sees {count} audio clips"
        active=page.evaluate("""() => [...document.querySelectorAll('button')]
           .filter(b=>/待配音/.test(b.textContent||'')) .map(b=>b.outerHTML.slice(0,240))""")
        assert not active, f"{profile['name']}: placeholder buttons: {active}"
        # Try direct user gesture replay. The webpage may be on an intro screen.
        if page.locator("#voiceReplayBtn:visible").count():
            page.locator("#voiceReplayBtn").click(timeout=3000)
            page.wait_for_timeout(200)
            played=page.evaluate("window.__voiceEvents")
            assert any("data:audio/mpeg" in (v.get("src") or "") for v in played), (
                f"{profile['name']}: replay never routed to the packaged MP3")
        # No horizontal body scroll beyond 3 px. Intrinsic game canvas may be fixed.
        overflow=page.evaluate("""() => Math.max(0,
          document.documentElement.scrollWidth - document.documentElement.clientWidth)""")
        assert overflow<=3, f"{profile['name']} horizontal overflow {overflow}px"
        page.screenshot(path=str(root / f"smoke-{profile['name']}.png"), full_page=True)
        print(f"PASS {profile['name']}: {count} MP3 registered; no placeholder buttons; JS clean; horizontal overflow={overflow}px")
        context.close()
    browser.close()
