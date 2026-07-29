"""Async Playwright wrapper for filling and submitting job application forms.

The actual form-submit action (`submit_form`) is guarded: it raises
ApprovalNotGrantedError unless called with approved=True, which callers must
only set after a human_approval interrupt resolves to "approved".
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

logger = logging.getLogger("app.agents.tools.playwright")


class ApprovalNotGrantedError(Exception):
    """Raised if form submission is attempted without explicit human approval."""


class PlaywrightTool:
    """Thin async wrapper around Playwright for ATS form automation."""

    def __init__(self, headless: bool = True) -> None:
        self.headless = headless
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    async def launch(self) -> None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(headless=self.headless)
        self._context = await self._browser.new_context()
        self.page = await self._context.new_page()

    async def attach(self, page: Page) -> None:
        """Attach to an already-open page instead of launching a new browser."""
        self.page = page

    async def goto(self, url: str) -> None:
        assert self.page is not None, "Call launch() or attach() first"
        await self.page.goto(url)

    async def fill_text(self, selector: str, value: str) -> None:
        assert self.page is not None, "Call launch() or attach() first"
        await self.page.fill(selector, value)

    async def select_dropdown(self, selector: str, value: str) -> None:
        assert self.page is not None, "Call launch() or attach() first"
        await self.page.select_option(selector, label=value)

    async def upload_file(self, selector: str, file_path: str) -> None:
        assert self.page is not None, "Call launch() or attach() first"
        await self.page.set_input_files(selector, file_path)

    async def click(self, selector: str) -> None:
        assert self.page is not None, "Call launch() or attach() first"
        await self.page.click(selector)

    async def wait_for_selector(self, selector: str, timeout_ms: int = 10000) -> None:
        assert self.page is not None, "Call launch() or attach() first"
        await self.page.wait_for_selector(selector, timeout=timeout_ms)

    async def screenshot(self, path: str) -> str:
        assert self.page is not None, "Call launch() or attach() first"
        await self.page.screenshot(path=path, full_page=True)
        return path

    async def fill_form(self, field_actions: List[Dict[str, Any]]) -> None:
        """Fill multiple fields in sequence. Each action: {selector, type, value}."""
        for action in field_actions:
            selector = action["selector"]
            field_type = action.get("type", "text")
            value = action.get("value", "")

            if field_type == "select":
                await self.select_dropdown(selector, value)
            elif field_type == "file":
                await self.upload_file(selector, value)
            elif field_type in ("checkbox", "radio"):
                if str(value).lower() in ("true", "yes", "1"):
                    await self.click(selector)
            else:
                await self.fill_text(selector, value)

    async def submit_form(self, submit_selector: str, *, approved: bool) -> None:
        """Click the final submit button. NEVER auto-submits: raises unless
        called with approved=True, which must only ever be set after human
        approval has been granted via the human_approval interrupt.
        """
        if not approved:
            raise ApprovalNotGrantedError(
                "Refusing to submit application form: human approval was not granted."
            )
        assert self.page is not None, "Call launch() or attach() first"
        await self.click(submit_selector)

    async def close(self) -> None:
        if self._context is not None:
            await self._context.close()
        if self._browser is not None:
            await self._browser.close()
        if self._playwright is not None:
            await self._playwright.stop()
