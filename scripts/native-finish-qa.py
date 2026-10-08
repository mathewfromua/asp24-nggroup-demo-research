#!/usr/bin/env python3
"""Native HTTP acceptance of ASP24 / NG Group — Demo & Research.

Run in the parent's installed Playwright environment, for example:
  python native_finish_qa.py --base-url http://127.0.0.1:4173 --out-dir native-proof
Default: both exact viewports. --viewport 390x844 selects just mobile; repeatable.
This script does not publish, change the checkout, inject state, clear storage,
intercept network requests, replace modules, or submit an order. All writes are
normal UI actions in newly created, nonpersistent isolated browser contexts.
DOM evaluations below only read the rendered DOM/geometry/focus. Screenshots are
unmodified viewport captures, with JSON proof after every successful step and on
failure. A failed step aborts its flow, not the other independent flows.
"""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import traceback
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright, expect

BUILD = "asp24-nggroup-demo-research-3.1.1-demo.1"
PAGE1 = ["s56", "s61", "s55", "s44", "s31", "s20", "s19", "s64", "s40", "s16", "s45", "s50", "s21", "s26", "s59", "s35", "s11", "s46", "s51", "s60", "s24", "s36", "s54", "s30"]
PAGE2 = ["s34", "s14", "s10", "s39"]
SIX = ["u01", "u02", "u03", "u04", "u05", "u06"]
REPLACED = ["u01", "u02", "u03", "u04", "u07", "u06"]
EXPECTED = {
    "catalog": ["BUILD_384", "A_OR_TWO", "A_REMOVE_ONE", "C_EXPLICIT_SORT", "C_MAP_ZERO_TO_ONE", "D_CATEGORY", "D_MANUFACTURER_OR", "D_PRICE", "D_NUMERIC", "D_PAGE1", "D_PAGE2", "D_DOCUMENT_U02_D1", "D_LONG_CATALOG_NAME", "D_LONG_DETAIL_NAME"],
    "project": ["B1_DRAFT_BEFORE_ADD", "B1_ADD_U02_RETAIN_QUERY", "B1_ADD_U04_RETAIN_QUERY", "B1_CHOSEN_DRAFT", "B1_QUANTITY_DRAFT", "B2_SAVE_RELOAD"],
    "compare": ["E_EMPTY", *[f"E_ADD_{i.upper()}" for i in SIX], "E_SIX_ORDER", "E_PAIR_SLOT0", "E_PAIR_SLOT1", "E_LIMIT_NO_IMPLICIT_REPLACE", "E_EXPLICIT_REPLACEMENT", "E_REMOVE", "E_UNDO", "E_MODE_RELOAD", "E_KEYBOARD_FOCUS", "E_CART_ADD", "E_CART_QUANTITIES", "E_CART_RELOAD"],
}


def check(condition, message):
    if not condition:
        raise AssertionError(message)


def query(page):
    return parse_qs(urlsplit(page.url).fragment.partition("?")[2])


def digits(text):
    return int("".join(re.findall(r"\d", text)))


def ids(page, selector, attribute="data-product-id"):
    return page.locator(selector).evaluate_all("(nodes, attr) => nodes.map(n => n.getAttribute(attr))", attribute)


def assert_ids(page, selector, expected, attribute="data-product-id"):
    expect(page.locator(selector)).to_have_count(len(expected))
    page.wait_for_function("({selector, attr, values}) => JSON.stringify([...document.querySelectorAll(selector)].map(n => n.getAttribute(attr))) === JSON.stringify(values)", arg={"selector": selector, "attr": attribute, "values": expected})
    check(ids(page, selector, attribute) == expected, f"Unexpected order at {selector}")


def reveal(locator):
    # Open only native <details> ancestors, using their real summaries.
    while locator.locator("xpath=ancestor::details[not(@open)]").count():
        locator.locator("xpath=ancestor::details[not(@open)]").first.locator(":scope > summary").click()


def close_modal(page):
    page.locator('#modal [data-action="close"]').first.click()
    expect(page.locator("#modal")).not_to_be_visible()


def native_quantity(page, selector, target):
    # Arrow keys + native blur exercise change, including project rerenders.
    current = int(page.locator(selector).input_value())
    while current != target:
        direction = 1 if current < target else -1
        page.locator(selector).press("ArrowUp" if direction > 0 else "ArrowDown")
        page.locator(selector).press("Tab")
        current += direction
        expect(page.locator(selector)).to_have_value(str(current))


class Proof:
    def __init__(self, args):
        self.args = args
        self.out = Path(args.out_dir).resolve()
        self.out.mkdir(parents=True, exist_ok=True)
        self.report = {"at": datetime.now(timezone.utc).isoformat(), "base_url": args.base_url, "build": BUILD,
                       "method": "Native HTTP/ES modules; sandboxed Chromium; new nonpersistent contexts; real UI and reload; read-only DOM assertions",
                       "limitations": ["Chromium only; viewport emulation is not physical-device/Safari/zoom testing.", "Automated geometry and focus assertions plus screenshots require visual review; not a full WCAG audit.", "Authoring alone is not execution. Only recorded PASS steps count; skipped/not-run steps are not PASS.", "No deployment, order submission, or persistent user-context storage access."],
                       "contexts": [], "steps": [], "failures": [], "page_errors": [], "console_errors": [], "passed": False}
        self.flush()

    def flush(self):
        (self.out / "native-finish-qa.json").write_text(json.dumps(self.report, ensure_ascii=False, indent=2), encoding="utf-8")

    def snapshot(self, page):
        return page.evaluate("""() => {
          const q = s => document.querySelector(s), qa = s => [...document.querySelectorAll(s)];
          const rect = el => { const r=el.getBoundingClientRect(), c=getComputedStyle(el); return {width:r.width,left:r.left,right:r.right,clientWidth:el.clientWidth,scrollWidth:el.scrollWidth,overflowX:c.overflowX}; };
          const visible = el => !!el.getClientRects().length;
          const a=document.activeElement, r=a?.getBoundingClientRect(), c=a?getComputedStyle(a):null;
          return {viewport:{width:innerWidth,height:innerHeight,devicePixelRatio},
            document:{clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,bodyScrollWidth:document.body.scrollWidth},
            focus:a?{tag:a.tagName,id:a.id,action:a.dataset.action,model:a.dataset.id,visible:visible(a),focusVisible:a.matches(':focus-visible'),outlineStyle:c.outlineStyle,outlineWidth:c.outlineWidth,rect:{left:r.left,top:r.top,right:r.right,bottom:r.bottom}}:null,
            components:qa('.catalog-results,.detail-head,.science-project-meta,.science-project-line,.science-model-map,.science-map-table-wrap,.research-workspace,.research-head-scroll,.research-scroll,.research-mobile,.research-pair,.document-page,.document-page .spec-table,.cart-layout,#modal[open]').filter(visible).map(el=>({selector:el.id?'#'+el.id:'.'+el.className.split(' ').join('.'),...rect(el)})),
            resultCount:q('.result-count')?.textContent,
            catalog:qa('[data-product-id]').map(el=>({id:el.dataset.productId,text:el.innerText.slice(0,700)})),
            checkedFacets:qa('[data-multi-filter]:checked').map(el=>({key:el.dataset.multiFilter,value:el.value})),
            fullComparison:qa('.research-desktop [data-compare-id]').map(el=>el.dataset.compareId),
            visiblePair:qa('.research-mobile [data-compare-id]').filter(visible).map(el=>el.dataset.compareId),
            comparisonCount:qa('.research-count span').filter(visible).map(el=>el.textContent),
            modes:{differences:q('#differences')?.checked,expanded:q('[data-action="expand-compare"]')?.getAttribute('aria-pressed')},
            project:{name:q('.science-project-meta [name=name]')?.value,note:q('.science-project-meta [name=note]')?.value,lines:qa('[data-project-model]').map(el=>({id:el.dataset.projectModel,quantity:el.querySelector('[data-field=quantity]')?.value,chosen:el.querySelector('[data-field=chosen]')?.checked,text:el.innerText})),total:q('.science-project-total')?.innerText},
            picker:q('#modal[open]')?{query:q('#modal input[name=q]')?.value??q('#candidate-search')?.value,group:q('#modal select[name=group]')?.value,text:q('#modal').innerText.slice(0,5000)}:null,
            documentMeta:q('.document-meta')?.innerText,
            cart:qa('[data-cart-id]').map(el=>({id:el.dataset.cartId,quantity:el.querySelector('[data-quantity]')?.value,text:el.innerText})),total:q('.cart-layout .total strong')?.innerText};
        }""")

    @contextmanager
    def step(self, page, context_id, step_id):
        item = {"context": context_id, "id": step_id, "status": "RUNNING"}
        self.report["steps"].append(item)
        self.flush()
        try:
            yield item
            item["url"] = page.url
            item["dom"] = self.snapshot(page)
            v = item["dom"]["viewport"]
            check(v["width"] == page.viewport_size["width"] and v["height"] == page.viewport_size["height"], f"Actual viewport mismatch: {v}")
            d = item["dom"]["document"]
            check(d["scrollWidth"] <= d["clientWidth"] + 1, f"Global horizontal overflow: {d}")
            # Dedicated map/table scrollers may overflow internally; their boxes must fit.
            for box in item["dom"]["components"]:
                check(box["left"] >= -1 and box["right"] <= d["clientWidth"] + 1, f"Component box escapes viewport: {box}")
            item["status"] = "PASS"
        except Exception as exc:
            item["status"] = "FAIL"
            item["error"] = str(exc)
            item["traceback"] = traceback.format_exc()
            self.report["failures"].append({"context": context_id, "id": step_id, "error": str(exc)})
            try:
                item["url"] = page.url
                item["dom"] = self.snapshot(page)
            except Exception as evidence_error:
                item["evidence_error"] = str(evidence_error)
            raise
        finally:
            shot = self.out / f"{context_id}--{step_id}.png"
            try:
                page.screenshot(path=str(shot), full_page=False)
                item["screenshot"] = shot.name
            except Exception as screenshot_error:
                item["screenshot_error"] = str(screenshot_error)
                if item["status"] == "PASS":
                    item["status"] = "FAIL"
                    self.report["failures"].append({"context": context_id, "id": step_id, "error": f"Screenshot failed: {screenshot_error}"})
            self.flush()
            print(f"{context_id} {step_id}: {item['status']}", flush=True)


class Flow:
    def __init__(self, page, proof, context_id):
        self.p, self.proof, self.cid = page, proof, context_id
        self.mobile = page.viewport_size["width"] == 390

    def step(self, name):
        return self.proof.step(self.p, self.cid, name)

    def goto(self, route):
        response = self.p.goto(self.proof.args.base_url.rstrip("/") + "/#" + route, wait_until="domcontentloaded")
        if response is not None:
            check(response.ok, f"HTTP {response.status}")
        expect(self.p.locator('meta[name="app-build"]')).to_have_attribute("content", BUILD)
        expect(self.p.locator("#main")).not_to_be_empty()

    def count(self, number):
        expect(self.p.locator(".result-count")).to_contain_text(re.compile(rf"^{number} \D"))

    def facet(self, key, value):
        target = self.p.locator(f'[data-multi-filter="{key}"][value="{value}"]')
        reveal(target)
        target.check()
        expect(target).to_be_checked()

    def draft(self, name, note):
        expect(self.p.locator('.science-project-meta [name="name"]')).to_have_value(name)
        expect(self.p.locator('.science-project-meta [name="note"]')).to_have_value(note)

    def full_group(self, values):
        # Rendered desktop columns also expose full retained group on mobile;
        # the visible order dialog below independently confirms all six through UI.
        assert_ids(self.p, ".research-desktop [data-compare-id]", values, "data-compare-id")
        if self.mobile:
            expect(self.p.locator(".mobile-count")).to_have_text(f"{min(2,len(values))} з {len(values)}")
        else:
            expect(self.p.locator(".desktop-count")).to_have_text(f"{len(values)} із 6")

    def pair(self, values):
        assert_ids(self.p, ".research-mobile [data-compare-id]", values, "data-compare-id")

    def model_focus(self, model):
        # Assert the visible model name, never a hidden desktop duplicate.
        scope = ".research-mobile" if self.mobile else ".research-desktop"
        expect(self.p.locator(f'{scope} .model-name[data-id="{model}"]')).to_be_focused()

    def catalog(self):
        p = self.p
        with self.step("BUILD_384"):
            self.goto("/asp/catalog")
            self.count(384)
            expect(p.locator(".grid > article.product")).to_have_count(24)
        with self.step("A_OR_TWO"):
            self.goto("/asp/catalog?cat=ups&q=VOLTYN")
            available = p.locator('[data-filter="available"]')
            reveal(available)
            available.check()
            expect(available).to_be_checked()
            expect(p.locator('[data-action="remove-filter"][data-key="available"]')).to_be_visible()
            self.facet("f0", "18 Вт")
            self.count(1)
            self.facet("f0", "36 Вт")
            self.count(3)
            p.locator('[data-filter="sort"]').select_option("price-down")
            expect(p.locator('[data-filter="sort"]')).to_have_value("price-down")
            assert_ids(p,".grid > article.product",["u04","u02","u01"])
            p.locator('[data-action="catalog-view"][data-key="list"]').click()
            expect(p.locator(".technical-item")).to_have_count(3)
        with self.step("A_REMOVE_ONE"):
            p.locator('[data-action="remove-filter"][data-key="f0"][data-value="18 Вт"]').click()
            assert_ids(p, ".technical-item", ["u04", "u02"])
            check(query(p) == {"cat":["ups"], "q":["VOLTYN"], "available":["1"], "f0":["36 Вт"], "sort":["price-down"], "view":["list"]}, f"A lost conditions: {query(p)}")
            check(p.locator('[data-multi-filter="f0"]:checked').evaluate_all("xs=>xs.map(x=>x.value)") == ["36 Вт"], "OR checkbox mismatch")
        with self.step("C_EXPLICIT_SORT"):
            self.goto("/asp/catalog?cat=ups&q=VOLTYN%20N36&view=list")
            assert_ids(p, ".technical-item", ["u02", "u04"])
            p.locator('[data-filter="sort"]').select_option("price-down")
            assert_ids(p, ".technical-item", ["u04", "u02"])
            check([digits(t) for t in p.locator(".technical-offer > strong").all_text_contents()] == [2490,2190], "Price order incorrect")
        with self.step("C_MAP_ZERO_TO_ONE"):
            p.locator('.catalog-viewbar a[href*="/model-map?"]').click()
            expect(p.locator(".science-map-context")).to_contain_text("2 моделі")
            counter = p.locator('nav[aria-label="Мій вибір"] a[href="#/asp/compare"] .count')
            expect(counter).to_have_text("0")
            p.locator('[data-action="science-map-compare"][data-id="u02"]').click()
            expect(counter).to_have_text("1")
            expect(p.locator('[data-action="science-map-compare"][data-id="u02"]')).to_be_disabled()
            expect(p.locator('.science-model-map [data-model-id="u02"]')).to_have_class(re.compile("is-selected"))
        with self.step("D_CATEGORY"):
            self.goto("/asp/catalog?view=cards")
            category = p.locator('[data-action="category"][data-key="switches"]')
            reveal(category)
            category.click()
            self.count(64)
        with self.step("D_MANUFACTURER_OR"):
            for value, count in [("KRYNET",12),("OBRYS",23),("TYVRA",34)]:
                self.facet("manufacturer", value)
                self.count(count)
        for step, low, high, count in [("D_PRICE", "price_min", "price_max",31), ("D_NUMERIC", "n_lanPorts_min", "n_lanPorts_max",28)]:
            with self.step(step):
                target = p.locator(f'input[name="{low}"]')
                reveal(target)
                target.fill("4000" if low == "price_min" else "8")
                p.locator(f'input[name="{high}"]').fill("23000" if high == "price_max" else "48")
                target.locator("xpath=ancestor::form").locator('button[type="submit"]').click()
                self.count(count)
        with self.step("D_PAGE1"):
            p.locator('[data-filter="sort"]').select_option("price-down")
            expect(p.locator('[data-filter="sort"]')).to_have_value("price-down")
            assert_ids(p,".grid > article.product",PAGE1)
            p.locator('[data-action="catalog-view"][data-key="list"]').click()
            assert_ids(p, ".technical-item", PAGE1)
            expect(p.locator(".result-count")).to_contain_text("показано 1–24")
        with self.step("D_PAGE2"):
            before = query(p)
            p.locator('.catalog-pagination [aria-label="Сторінка 2"]').click()
            assert_ids(p, ".technical-item", PAGE2)
            check(query(p) == {**before, "page":["2"]}, "Pagination lost conditions")
            check([digits(t) for t in p.locator(".technical-offer > strong").all_text_contents()] == [4315,4095,4051,4050], "Page2 prices")
            expect(p.locator(".result-count")).to_contain_text("28 моделей · показано 25–28")
        with self.step("D_DOCUMENT_U02_D1"):
            self.goto("/ng/documents")
            p.locator("#search").fill("DEMO-U02")
            p.locator('#search-form button[aria-label="Знайти"]').click()
            expect(p.locator(".document-row")).to_have_count(1)
            p.locator('.document-row[href="#/ng/document/u02"]').click()
            expect(p.locator(".document-page h1")).to_have_text("VOLTYN N36")
            for text in ["DEMO-U02", "D1", "українська"]:
                expect(p.locator(".document-meta")).to_contain_text(text)
            expect(p.locator(".document-page .spec-table tr")).not_to_have_count(0)
        with self.step("D_LONG_CATALOG_NAME"):
            self.goto("/asp/catalog?q=DEMO-O64&view=cards")
            assert_ids(p,".grid > article.product",["o64"])
            expect(p.locator('[data-product-id="o64"] h3')).to_have_text("KRYNET QSFP28 100G 0,1K MPO Industrial Trace")
            p.locator('[data-product-id="o64"]').scroll_into_view_if_needed()
        with self.step("D_LONG_DETAIL_NAME"):
            p.locator('[data-product-id="o64"] h3 a').click()
            expect(p.locator('.detail-head h1')).to_have_text("KRYNET QSFP28 100G 0,1K MPO Industrial Trace")
            p.locator('.detail-head h1').scroll_into_view_if_needed()
            check(p.locator('.detail-head h1').evaluate("el=>el.scrollWidth<=el.clientWidth+1"),"Long detail title overflows its box")

    def project(self):
        p = self.p
        name = f"QA {self.cid} — незбережена назва проєкту обладнання"
        note = "QA: незбережена примітка. Перевірити сумісність, кількість і одиниці."
        with self.step("B1_DRAFT_BEFORE_ADD"):
            self.goto("/asp/projects")
            p.locator('[data-action="science-create"]').click()
            expect(p.locator(".science-project-meta")).to_be_visible()
            project_url = p.url
            p.locator('.science-project-meta [name="name"]').fill(name)
            p.locator('.science-project-meta [name="note"]').fill(note)
            self.draft(name,note)
            p.locator('[data-action="science-candidates"]').click()
            p.locator('#modal input[name="q"]').fill("VOLTYN")
            p.locator('#modal select[name="group"]').select_option("ups")
            p.locator('#modal [data-science-form="candidate-search"] button[type="submit"]').click()
            expect(p.locator('#modal [data-action="science-add-candidate"]')).to_have_count(8)
        for model in ["u02", "u04"]:
            with self.step(f"B1_ADD_{model.upper()}_RETAIN_QUERY"):
                p.locator(f'#modal [data-action="science-add-candidate"][data-id="{model}"]').click()
                expect(p.locator(f'#modal [data-action="science-add-candidate"][data-id="{model}"]')).to_be_disabled()
                expect(p.locator('#modal input[name="q"]')).to_have_value("VOLTYN")
                expect(p.locator('#modal select[name="group"]')).to_have_value("ups")
                self.draft(name,note)
        with self.step("B1_CHOSEN_DRAFT"):
            close_modal(p)
            p.locator('[data-field="chosen"][data-id="u02"]').check()
            expect(p.locator('[data-field="chosen"][data-id="u02"]')).to_be_checked()
            expect(p.locator('.science-title p')).to_have_text("2 кандидати · 1 вибрано")
            self.draft(name,note)
        with self.step("B1_QUANTITY_DRAFT"):
            native_quantity(p, '[data-field="quantity"][data-id="u02"]',3)
            self.draft(name,note)
            native_quantity(p, '[data-field="quantity"][data-id="u04"]',2)
            self.draft(name,note)
            check(digits(p.locator('[data-project-model="u02"] .money').inner_text()) == 6570, "U02 project sum")
            check(digits(p.locator('[data-project-model="u04"] .money').inner_text()) == 4980, "U04 project sum")
            check(digits(p.locator('.science-project-total strong').inner_text()) == 6570, "Chosen-only project total")
        with self.step("B2_SAVE_RELOAD"):
            p.locator('.science-project-meta button[type="submit"]').click()
            expect(p.locator('.science-title h1')).to_have_text(name)
            p.reload(wait_until="domcontentloaded")
            self.draft(name,note)
            check(p.url == project_url, "Project route did not persist")
            assert_ids(p, "[data-project-model]", ["u02","u04"], "data-project-model")
            expect(p.locator('[data-field="quantity"][data-id="u02"]')).to_have_value("3")
            expect(p.locator('[data-field="quantity"][data-id="u04"]')).to_have_value("2")
            expect(p.locator('[data-field="chosen"][data-id="u02"]')).to_be_checked()
            expect(p.locator('[data-field="chosen"][data-id="u04"]')).not_to_be_checked()
            expect(p.locator('.science-title p')).to_have_text("2 кандидати · 1 вибрано")
            check(digits(p.locator('.science-project-total strong').inner_text()) == 6570, "Reload chosen sum")

    def compare(self):
        p = self.p
        with self.step("E_EMPTY"):
            self.goto("/asp/compare")
            expect(p.locator(".research-empty")).to_be_visible()
            p.locator("#compare-group").select_option("ups")
            expect(p.locator("#compare-group")).to_have_value("ups")
        for i,model in enumerate(SIX):
            with self.step(f"E_ADD_{model.upper()}"):
                p.locator('.research-toolbar [data-action="add-compare-models"]').click()
                expect(p.locator("#candidate-search")).to_be_focused()
                p.locator("#candidate-search").fill("DEMO-" + model.upper())
                p.locator(f'#modal [data-action="pick-candidate"][data-id="{model}"]').click()
                expect(p.locator("#modal")).not_to_be_visible()
                self.full_group(SIX[:i+1])
        with self.step("E_SIX_ORDER"):
            self.full_group(SIX)
            self.pair(["u01","u02"])
            p.locator('[data-action="order-models"]').click()
            assert_ids(p, '#modal .order-list [data-delta="-1"]', SIX, "data-id")
            close_modal(p)
        if self.mobile:
            for slot,model,expected in [(0,"u05",["u05","u02"]),(1,"u06",["u05","u06"])]:
                with self.step(f"E_PAIR_SLOT{slot}"):
                    p.locator(f'.research-mobile [data-action="choose-pair"][data-slot="{slot}"]').click()
                    expect(p.locator('#modal [data-action="select-pair"]')).to_have_count(6)
                    p.locator(f'#modal [data-action="select-pair"][data-slot="{slot}"][data-id="{model}"]').click()
                    self.pair(expected)
                    self.full_group(SIX)
                    self.model_focus(model)
        with self.step("E_LIMIT_NO_IMPLICIT_REPLACE"):
            p.locator('.research-toolbar [data-action="add-compare-models"]').click()
            expect(p.locator("#replace-target")).to_have_value("")
            p.locator("#candidate-search").fill("DEMO-U07")
            p.locator('#modal [data-action="pick-candidate"][data-id="u07"]').click()
            expect(p.locator("#replace-target")).to_have_value("")
            self.full_group(SIX)
        with self.step("E_EXPLICIT_REPLACEMENT"):
            p.locator("#replace-target").select_option("u05")
            expect(p.locator("#replace-target")).to_have_count(0)
            expect(p.locator("#candidate-search")).to_be_focused()
            p.locator("#candidate-search").fill("DEMO-U07")
            p.locator('#modal [data-action="pick-candidate"][data-id="u07"]').click()
            self.full_group(REPLACED)
            self.pair(["u07","u06"] if self.mobile else ["u01","u02"])
            self.model_focus("u07")
        scope = ".research-mobile" if self.mobile else ".research-desktop"
        with self.step("E_REMOVE"):
            p.locator(f'{scope} [data-action="remove-compare"][data-id="u07"]').click()
            self.full_group(["u01","u02","u03","u04","u06"])
            expect(p.locator('#toast [data-action="undo-compare"]')).to_be_visible()
        with self.step("E_UNDO"):
            p.locator('#toast [data-action="undo-compare"]').click()
            self.full_group(REPLACED)
            self.pair(["u07","u06"] if self.mobile else ["u01","u02"])
            self.model_focus("u07")
        with self.step("E_MODE_RELOAD"):
            p.locator("#differences").check()
            expect(p.locator("#differences")).to_be_checked()
            expect(p.locator(".mode-description")).to_have_text("Показано різні значення")
            p.locator('[data-action="expand-compare"]').click()
            expect(p.locator('[data-action="expand-compare"]')).to_have_attribute("aria-pressed", "true")
            p.reload(wait_until="domcontentloaded")
            self.full_group(REPLACED)
            self.pair(["u07","u06"] if self.mobile else ["u01","u02"])
            expect(p.locator("#differences")).to_be_checked()
            expect(p.locator('[data-action="expand-compare"]')).to_have_attribute("aria-pressed", "true")
            expect(p.locator("body")).to_have_class(re.compile(r"\bcomparison-expanded\b"))
            expect(p.locator(scope + " [data-row].same")).to_have_count(0)
        with self.step("E_KEYBOARD_FOCUS"):
            # Real click then Tab, with actual focus-visible styling and viewport proof.
            p.locator('[data-action="expand-compare"]').click()
            p.keyboard.press("Tab")
            focus = self.proof.snapshot(p)["focus"]
            check(focus["visible"] and focus["focusVisible"], f"Missing keyboard focus: {focus}")
            check(focus["outlineStyle"] != "none" and float(focus["outlineWidth"].replace("px","")) > 0, f"No visible focus outline: {focus}")
            r=focus["rect"]
            check(r["left"]>=0 and r["right"]<=p.viewport_size["width"] and r["top"]>=0 and r["bottom"]<=p.viewport_size["height"], f"Focused control clipped: {focus}")
        with self.step("E_CART_ADD"):
            for model in ["u02", "c04"]:
                self.goto("/asp/product/" + model)
                p.locator(f'.detail-panel [data-action="cart"][data-id="{model}"]').click()
                expect(p.locator('.detail-panel .status-save')).to_contain_text("У вашому кошику")
            self.goto("/asp/cart")
            assert_ids(p,"[data-cart-id]",["u02","c04"],"data-cart-id")
        with self.step("E_CART_QUANTITIES"):
            native_quantity(p,'[data-quantity="u02"]',3)
            native_quantity(p,'[data-quantity="c04"]',2)
            self.cart_assertions()
        with self.step("E_CART_RELOAD"):
            p.reload(wait_until="domcontentloaded")
            self.cart_assertions()

    def cart_assertions(self):
        p=self.p
        expect(p.locator('[data-quantity="u02"]')).to_have_value("3")
        expect(p.locator('[data-quantity="c04"]')).to_have_value("2")
        expect(p.locator('[data-cart-id="c04"]')).to_contain_text("за бухту 305 м · разом 610 м")
        check(digits(p.locator('[data-cart-id="u02"] .line-price > span').inner_text())==6570,"U02 cart subtotal")
        check(digits(p.locator('[data-cart-id="c04"] .line-price > span').inner_text())==10380,"C04 cart subtotal")
        check(digits(p.locator('.cart-layout .total strong').inner_text())==16950,"Cart total")
        expect(p.locator('nav[aria-label="Мій вибір"] a[href="#/asp/cart"] .count')).to_have_text("5")


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url",required=True)
    parser.add_argument("--out-dir",required=True)
    parser.add_argument("--executable",help="Optional Chromium executable; otherwise Playwright's installed Chromium")
    parser.add_argument("--viewport",action="append",choices=["1440x900","390x844"],help="Repeatable; default is both exact viewports")
    args=parser.parse_args()
    check(urlsplit(args.base_url).scheme in ("http","https"),"--base-url must be a native HTTP(S) origin/path")
    proof=Proof(args)
    try:
        with sync_playwright() as pw:
            opts={"headless":True,"chromium_sandbox":True}
            if args.executable:
                opts["executable_path"]=args.executable
            browser=pw.chromium.launch(**opts)
            proof.report["browser_version"]=browser.version
            proof.report["launch"]={"headless":True,"chromium_sandbox":True,"executable_override":bool(args.executable)}
            for viewport in dict.fromkeys(args.viewport or ["1440x900","390x844"]):
                width,height=map(int,viewport.split("x"))
                for group in ["catalog","project","compare"]:
                    cid=viewport+"-"+group
                    context=browser.new_context(viewport={"width":width,"height":height},device_scale_factor=1,locale="uk-UA")
                    page=context.new_page()
                    page.set_default_timeout(12000)
                    page.on("pageerror",lambda error,cid=cid: proof.report["page_errors"].append({"context":cid,"error":str(error)}))
                    page.on("console",lambda message,cid=cid: proof.report["console_errors"].append({"context":cid,"text":message.text}) if message.type=="error" else None)
                    proof.report["contexts"].append({"id":cid,"viewport":{"width":width,"height":height},"new_nonpersistent_context":True})
                    try:
                        getattr(Flow(page,proof,cid),group)()
                    except Exception as exc:
                        # Each step has already captured its own error; keep independent flows running.
                        if not any(f["context"]==cid for f in proof.report["failures"]):
                            proof.report["failures"].append({"context":cid,"id":"FLOW","error":str(exc),"traceback":traceback.format_exc()})
                    finally:
                        done={s["id"] for s in proof.report["steps"] if s["context"]==cid}
                        for missing in EXPECTED[group]:
                            if missing not in done:
                                status="NOT_APPLICABLE" if width==1440 and missing in ("E_PAIR_SLOT0","E_PAIR_SLOT1") else "NOT_RUN"
                                proof.report["steps"].append({"context":cid,"id":missing,"status":status,"reason":"Mobile pair selector is hidden on desktop" if status=="NOT_APPLICABLE" else "Earlier flow step failed"})
                        context.close()
                        proof.flush()
            browser.close()
    except Exception as exc:
        proof.report["failures"].append({"id":"NATIVE_EXECUTION_BLOCKED_OR_FAILED","error":str(exc),"traceback":traceback.format_exc()})
        # A launch blocker is never an empty, apparently successful test run.
        for viewport in dict.fromkeys(args.viewport or ["1440x900","390x844"]):
            for group in ["catalog","project","compare"]:
                cid=viewport+"-"+group
                done={s["id"] for s in proof.report["steps"] if s["context"]==cid}
                for missing in EXPECTED[group]:
                    if missing not in done:
                        proof.report["steps"].append({"context":cid,"id":missing,"status":"NOT_RUN","reason":"Native execution blocked before this step"})
    proof.report["passed"]=bool(proof.report["contexts"]) and not proof.report["failures"] and not proof.report["page_errors"] and all(s["status"] in ("PASS","NOT_APPLICABLE") for s in proof.report["steps"])
    proof.report["summary"]={status:sum(s["status"]==status for s in proof.report["steps"]) for status in ["PASS","FAIL","NOT_RUN","NOT_APPLICABLE"]}
    proof.flush()
    print(json.dumps({"passed":proof.report["passed"],"summary":proof.report["summary"],"report":str(proof.out/"native-finish-qa.json"),"failures":proof.report["failures"]},ensure_ascii=False,indent=2))
    return 0 if proof.report["passed"] else 1


if __name__=="__main__":
    sys.exit(main())
