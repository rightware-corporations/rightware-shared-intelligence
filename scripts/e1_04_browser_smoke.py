"""E1.04 real browser smoke of actual exported synthetic reviewer ZIPs.
No human attestations, completed submissions, model or scientific evaluation.
All packets, ZIPs, mapping and test drafts are temporary and ignored by Git.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from zipfile import ZipFile

from playwright.sync_api import sync_playwright
from e1_04_prepare_review import archive, PUBLIC

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/research/e1_04"
MARKER = "BROWSER SMOKE ONLY - NOT HUMAN REVIEW"


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def load(page, packet, record):
    page.locator("#packet").set_input_files(packet)
    page.locator("#blank").set_input_files(record)
    page.locator("#load").click()


def smoke(browser, out):
    extracted = {}
    for slot in ("A", "B"):
        target = out / f"REVIEWER_{slot}.zip"
        archive(out / f"reviewer_{slot}", target, ASSETS, slot)
        folder = out / f"smoke_{slot}"
        folder.mkdir()
        with ZipFile(target) as z:
            require(tuple(z.namelist()) == PUBLIC, "ZIP allowlist")
            for name in PUBLIC:
                (folder / name).write_bytes(z.read(name))
        extracted[slot] = folder

    for slot, other in (("A", "B"), ("B", "A")):
        folder = extracted[slot]
        packet, blank = folder / "packet.json", folder / "BLANK.json"
        wrong = extracted[other] / "BLANK.json"
        context = browser.new_context(accept_downloads=True, offline=True)
        remote, errors, downloads = [], [], []
        context.route("**/*", lambda route: route.abort()
                      if route.request.url.startswith(("http:", "https:"))
                      else route.continue_())
        context.on("request", lambda req: remote.append(True)
                   if req.url.startswith(("http:", "https:")) else None)
        page = context.new_page()
        page.on("pageerror", lambda _: errors.append(True))
        page.on("download", lambda _: downloads.append(True))
        try:
            page.goto((folder / "REVIEWER_OFFLINE.html").as_uri())
            load(page, packet, wrong)
            page.wait_for_function("document.querySelector('#loadstatus').textContent.startsWith('Error:')")
            require(not page.locator("#review").is_visible(), "wrong slot accepted")
            load(page, packet, blank)
            page.wait_for_function("!document.querySelector('#review').hidden")
            require(page.locator("#question option").count() == 24, "question count")
            require(page.locator("#progress").inner_text().startswith("0/560"), "blank coverage")
            page.locator("#finish").click()
            require("issue(s)" in page.locator("#messages").inner_text(), "blank accepted")
            require(not downloads, "blank completion download")
            page.locator("#question").select_option("23")
            require(page.locator("#next").is_disabled(), "last question navigation")
            page.locator("#prev").click()
            require(page.locator("#question").input_value() == "22", "previous navigation")
            page.locator("#question").select_option("0")
            card = page.locator("#questionbody article").first
            card.locator("select").first.select_option("0")
            card.locator("textarea").first.fill(MARKER)
            require(page.locator("#progress").inner_text().startswith("1/560"), "draft edit count")
            with page.expect_download() as event:
                page.locator("#draft").click()
            draft = folder / "SMOKE_DRAFT.json"
            event.value.save_as(draft)
            saved = json.loads(draft.read_text(encoding="utf-8"))
            require(saved["review_status"] == "NOT_SUBMITTED" and not saved["submitted_at"],
                    "draft status")
            require(not saved["reviewer_pseudonym"] and not saved["independence_attested"]
                    and not saved["provisional_gold_not_consulted"], "unexpected human attestation")
            require(sum(r["justification"] == MARKER for j in saved["judgments"]
                        for r in j["ratings"]) == 1, "draft marker")
            page.reload()
            load(page, packet, draft)
            page.wait_for_function("!document.querySelector('#review').hidden")
            require(page.locator("#progress").inner_text().startswith("1/560"), "draft reload")
            require(page.locator("#questionbody article").first.locator("textarea").first.input_value()
                    == MARKER, "draft restored text")
            page.locator("#finish").click()
            require("issue(s)" in page.locator("#messages").inner_text(), "partial accepted")
            require(len(downloads) == 1, "unexpected download")
            require(not remote and not errors, "external page request or script error")
        finally:
            context.close()
        print(f"E1_04_BROWSER_SLOT_{slot}_PASS zip_allowlist=true questions=24 ratings=560 "
              "wrong_pair_rejected=true blank_rejected=true draft_roundtrip=true "
              "partial_rejected=true external_page_requests=0")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--chromium-executable", default=None)
    args = parser.parse_args()
    runtime = ROOT / ".runtime"
    require(not runtime.is_symlink(), "refusing symlinked .runtime")
    runtime.mkdir(mode=0o700, exist_ok=True)
    require(subprocess.run(["git", "check-ignore", "-q", ".runtime/e1_04_probe"],
                           cwd=ROOT).returncode == 0, ".runtime not ignored")
    with tempfile.TemporaryDirectory(prefix="e1_04_smoke_", dir=runtime) as temp:
        out = Path(temp)
        subprocess.run([sys.executable, str(ROOT / "scripts/e1_03_review.py"),
                        "--mode", "export", "--output-dir", str(out.relative_to(ROOT))],
                       cwd=ROOT, check=True)
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=args.chromium_executable)
            try:
                print("E1_04_BROWSER_VERSION", browser.version)
                smoke(browser, out)
            finally:
                browser.close()
    print("E1_04_BROWSER_SMOKE_PASS synthetic_only=true actual_humans=0 "
          "submitted=0 adjudicated=0 operator_dispatch=false science_gate=REVIEW_REQUIRED")


if __name__ == "__main__":
    main()
