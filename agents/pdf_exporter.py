"""
PDF Exporter - Converts the static HTML newsletter to PDF using Playwright
"""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class PDFExporter:
    """
    Converts HTML content to a clean PDF using Playwright's Chromium renderer.

    Falls back gracefully if Playwright or Chromium is unavailable,
    saving the HTML file instead with a clear message.
    """

    def export(self, html_content: str, output_path: str) -> str:
        """
        Export HTML content to PDF.

        Args:
            html_content: Full HTML document string (static variant preferred)
            output_path: Destination file path for the PDF

        Returns:
            Path to the generated file (PDF or fallback HTML)
        """
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright not installed — saving HTML fallback")
            return self._save_html_fallback(html_content, output_path)

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_content, wait_until="networkidle")
                page.pdf(
                    path=output_path,
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "20mm",
                        "bottom": "20mm",
                        "left": "15mm",
                        "right": "15mm",
                    },
                )
                browser.close()

            size_kb = os.path.getsize(output_path) / 1024
            logger.info("PDF exported: %s (%.1f KB)", output_path, size_kb)
            return output_path

        except Exception as e:
            logger.error("PDF export failed: %s — saving HTML fallback", e)
            return self._save_html_fallback(html_content, output_path)

    def _save_html_fallback(self, html_content: str, output_path: str) -> str:
        """Save the HTML file as a fallback when PDF generation fails."""
        html_path = output_path.replace(".pdf", ".html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        logger.info("HTML fallback saved: %s", html_path)
        return html_path
