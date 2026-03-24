"""
HTML Newsletter Generator - Builds an interactive HTML newsletter from research outputs
"""
import html
import logging
from datetime import datetime
from typing import List, Dict, Optional

import sys
sys.path.append('..')
from config import (
    NEWSLETTER_TITLE,
    NEWSLETTER_SUBTITLE,
    NEWSLETTER_QUARTER,
    NEWSLETTER_YEAR,
    MAX_FEATURED_ITEMS,
    CUSTOMER_CORNER_ENABLED,
)
from .tracker_reader import ResearchOutput

logger = logging.getLogger(__name__)


class HTMLNewsletterGenerator:
    """
    Builds a polished, interactive HTML newsletter from ResearchOutput objects.

    Produces two variants:
    - Interactive HTML with expandable sections and hover effects (for web)
    - Static HTML suitable for PDF export (no JS, simplified layout)
    """

    def generate(
        self,
        featured: List[ResearchOutput],
        listed: List[ResearchOutput],
        customer_corner_html: str = "",
        static: bool = False,
    ) -> str:
        """
        Generate the complete HTML newsletter.

        Args:
            featured: Priority-1 research outputs for prominent display
            listed: Priority-2 outputs shown as grouped one-liners
            customer_corner_html: Pre-rendered HTML for the customer corner section
            static: If True, produce PDF-friendly static HTML

        Returns:
            Complete HTML document string
        """
        featured = featured[:MAX_FEATURED_ITEMS]

        sections = []
        sections.append(self._render_header())
        sections.append(self._render_featured(featured, static))

        if listed:
            sections.append(self._render_listed(listed))

        if CUSTOMER_CORNER_ENABLED and customer_corner_html:
            sections.append(self._render_customer_corner(customer_corner_html))

        sections.append(self._render_appendix(featured + listed))
        sections.append(self._render_footer())

        body = "\n".join(sections)
        return self._wrap_document(body, static)

    def _esc(self, text: str) -> str:
        return html.escape(str(text))

    def _render_header(self) -> str:
        return f"""
    <header class="newsletter-header">
      <div class="header-badge">{self._esc(NEWSLETTER_QUARTER)} {NEWSLETTER_YEAR}</div>
      <h1>{self._esc(NEWSLETTER_TITLE)}</h1>
      <p class="subtitle">{self._esc(NEWSLETTER_SUBTITLE)}</p>
      <p class="intro">Welcome to the quarterly Research &amp; Insights newsletter.
        Here's a look at the key outputs and insights from across the team.</p>
    </header>"""

    def _render_featured(self, items: List[ResearchOutput], static: bool) -> str:
        if not items:
            return ""

        cards = []
        for item in items:
            link_html = ""
            if item.output_links:
                link_html = f'<a href="{self._esc(item.output_links[0])}" class="card-link" target="_blank">View full output &rarr;</a>'

            detail_id = f"detail-{id(item)}"

            if static:
                expand_html = f"""
        <div class="card-detail">
          <p>{self._esc(item.display_summary)}</p>
          {link_html}
        </div>"""
            else:
                expand_html = f"""
        <div class="card-detail" id="{detail_id}" style="display:none;">
          <p>{self._esc(item.display_summary)}</p>
          {link_html}
        </div>
        <button class="expand-btn" onclick="toggleDetail('{detail_id}', this)" aria-expanded="false">
          Read more <span class="chevron">&#9660;</span>
        </button>"""

            end_date_label = f' &middot; Completed {self._esc(item.project_end_date)}' if item.project_end_date else ""
            cards.append(f"""
      <div class="featured-card">
        <div class="card-meta">
          <span class="card-author">{self._esc(item.submitter)}{end_date_label}</span>
        </div>
        <h3>{self._esc(item.display_title)}</h3>
        <p class="card-desc">{self._esc(item.description)}</p>
        {expand_html}
      </div>""")

        return f"""
    <section class="section featured-section">
      <h2><span class="section-icon">&#9733;</span> Featured Research</h2>
      <div class="featured-grid">
        {"".join(cards)}
      </div>
    </section>"""

    def _render_listed(self, items: List[ResearchOutput]) -> str:
        rows = []
        for item in items:
            link_html = ""
            if item.output_links:
                link_html = f' <a href="{self._esc(item.output_links[0])}" class="inline-link" target="_blank">View &rarr;</a>'
            rows.append(f"""
          <li>
            <strong>{self._esc(item.display_title)}</strong>
            <span class="listed-desc">&mdash; {self._esc(item.description)}</span>
            <span class="listed-author">({self._esc(item.submitter)})</span>
            {link_html}
          </li>""")

        return f"""
    <section class="section listed-section">
      <h2><span class="section-icon">&#9776;</span> More from R&amp;I</h2>
      <ul class="listed-list">{"".join(rows)}
      </ul>
    </section>"""

    def _render_customer_corner(self, inner_html: str) -> str:
        return f"""
    <section class="section customer-corner">
      <h2><span class="section-icon">&#128100;</span> Customer Corner</h2>
      {inner_html}
    </section>"""

    def _render_appendix(self, all_outputs: List[ResearchOutput]) -> str:
        rows = []
        for o in sorted(all_outputs, key=lambda x: x.submitter):
            links = ", ".join(
                f'<a href="{self._esc(l)}" target="_blank">Link</a>'
                for l in o.output_links
            ) or "—"
            rows.append(f"""
        <tr>
          <td>{self._esc(o.title)}</td>
          <td>{self._esc(o.submitter)}</td>
          <td>{self._esc(o.project_end_date or '—')}</td>
          <td class="priority-{o.priority}">P{o.priority}</td>
          <td>{links}</td>
        </tr>""")

        return f"""
    <section class="section appendix-section">
      <h2><span class="section-icon">&#128218;</span> Appendix — All Research Outputs</h2>
      <table class="appendix-table">
        <thead>
          <tr>
            <th>Project</th>
            <th>Contributor</th>
            <th>End Date</th>
            <th>Priority</th>
            <th>Links</th>
          </tr>
        </thead>
        <tbody>{"".join(rows)}
        </tbody>
      </table>
    </section>"""

    def _render_footer(self) -> str:
        generated = datetime.now().strftime("%d %B %Y")
        return f"""
    <footer class="newsletter-footer">
      <p>This newsletter was generated on {generated} from the
        <a href="https://docs.google.com/spreadsheets/d/{self._esc(NEWSLETTER_QUARTER)}">R&amp;I Output Tracker</a>.</p>
      <p>Questions or feedback? Reach out to the Research &amp; Insights team.</p>
    </footer>"""

    def _wrap_document(self, body: str, static: bool) -> str:
        js_block = "" if static else self._render_js()
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{self._esc(NEWSLETTER_TITLE)} — {self._esc(NEWSLETTER_SUBTITLE)}</title>
  <style>
{self._render_css()}
  </style>
</head>
<body>
  <div class="container">
{body}
  </div>
{js_block}
</body>
</html>"""

    def _render_js(self) -> str:
        return """  <script>
    function toggleDetail(id, btn) {
      var el = document.getElementById(id);
      var expanded = btn.getAttribute('aria-expanded') === 'true';
      el.style.display = expanded ? 'none' : 'block';
      btn.setAttribute('aria-expanded', !expanded);
      btn.querySelector('.chevron').style.transform = expanded ? '' : 'rotate(180deg)';
    }
  </script>"""

    def _render_css(self) -> str:
        return """
    :root {
      --teal: #00CCBC;
      --teal-dark: #00A89D;
      --dark: #2E3333;
      --grey-100: #F7F8F8;
      --grey-200: #E8EAEB;
      --grey-400: #ABB1B1;
      --grey-600: #6B7070;
      --white: #FFFFFF;
      --radius: 12px;
      --shadow: 0 2px 8px rgba(0,0,0,0.06);
      --shadow-hover: 0 4px 16px rgba(0,0,0,0.10);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      color: var(--dark);
      background: var(--grey-100);
      line-height: 1.6;
      -webkit-font-smoothing: antialiased;
    }

    .container {
      max-width: 820px;
      margin: 0 auto;
      padding: 40px 24px;
    }

    /* Header */
    .newsletter-header {
      text-align: center;
      padding: 48px 24px 40px;
      background: linear-gradient(135deg, var(--teal), var(--teal-dark));
      color: var(--white);
      border-radius: var(--radius);
      margin-bottom: 32px;
    }
    .header-badge {
      display: inline-block;
      background: rgba(255,255,255,0.2);
      padding: 4px 14px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 1px;
      text-transform: uppercase;
      margin-bottom: 16px;
    }
    .newsletter-header h1 {
      font-size: 32px;
      font-weight: 700;
      margin-bottom: 8px;
    }
    .subtitle {
      font-size: 16px;
      opacity: 0.9;
      margin-bottom: 16px;
    }
    .intro {
      font-size: 15px;
      max-width: 560px;
      margin: 0 auto;
      opacity: 0.85;
    }

    /* Sections */
    .section {
      background: var(--white);
      border-radius: var(--radius);
      padding: 32px;
      margin-bottom: 24px;
      box-shadow: var(--shadow);
    }
    .section h2 {
      font-size: 22px;
      font-weight: 700;
      margin-bottom: 24px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--grey-200);
    }
    .section-icon {
      margin-right: 8px;
    }

    /* Featured Cards */
    .featured-grid {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
      gap: 20px;
    }
    .featured-card {
      background: var(--grey-100);
      border-radius: 10px;
      padding: 24px;
      border: 1px solid var(--grey-200);
      transition: box-shadow 0.2s, transform 0.2s;
    }
    .featured-card:hover {
      box-shadow: var(--shadow-hover);
      transform: translateY(-2px);
    }
    .card-meta {
      display: flex;
      justify-content: space-between;
      font-size: 12px;
      color: var(--grey-600);
      margin-bottom: 10px;
    }
    .card-team {
      background: var(--teal);
      color: var(--white);
      padding: 2px 10px;
      border-radius: 12px;
      font-weight: 600;
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }
    .featured-card h3 {
      font-size: 17px;
      font-weight: 700;
      margin-bottom: 8px;
      line-height: 1.35;
    }
    .card-desc {
      font-size: 14px;
      color: var(--grey-600);
      margin-bottom: 12px;
    }
    .card-detail {
      font-size: 14px;
      color: var(--dark);
      padding-top: 12px;
      border-top: 1px solid var(--grey-200);
      margin-top: 8px;
    }
    .card-detail p { margin-bottom: 10px; }
    .card-link {
      display: inline-block;
      color: var(--teal-dark);
      font-weight: 600;
      font-size: 13px;
      text-decoration: none;
    }
    .card-link:hover { text-decoration: underline; }
    .expand-btn {
      background: none;
      border: 1px solid var(--grey-200);
      border-radius: 6px;
      padding: 6px 14px;
      font-size: 13px;
      color: var(--teal-dark);
      cursor: pointer;
      font-weight: 600;
      transition: background 0.15s;
    }
    .expand-btn:hover { background: var(--grey-200); }
    .chevron {
      display: inline-block;
      font-size: 10px;
      margin-left: 4px;
      transition: transform 0.2s;
    }

    /* Listed Section */
    .listed-list {
      list-style: none;
      padding: 0;
    }
    .listed-list li {
      padding: 10px 0;
      border-bottom: 1px solid var(--grey-200);
      font-size: 14px;
      line-height: 1.5;
    }
    .listed-list li:last-child { border-bottom: none; }
    .listed-desc { color: var(--grey-600); }
    .listed-author { color: var(--grey-400); font-size: 13px; }
    .inline-link {
      color: var(--teal-dark);
      text-decoration: none;
      font-size: 13px;
      font-weight: 600;
    }
    .inline-link:hover { text-decoration: underline; }

    /* Customer Corner */
    .customer-corner {
      background: linear-gradient(135deg, #FFF8E1 0%, var(--white) 100%);
    }

    /* Appendix */
    .appendix-table {
      width: 100%;
      border-collapse: collapse;
      font-size: 13px;
    }
    .appendix-table th {
      text-align: left;
      padding: 10px 12px;
      background: var(--grey-100);
      border-bottom: 2px solid var(--grey-200);
      font-weight: 700;
      color: var(--grey-600);
      text-transform: uppercase;
      font-size: 11px;
      letter-spacing: 0.5px;
    }
    .appendix-table td {
      padding: 10px 12px;
      border-bottom: 1px solid var(--grey-200);
      vertical-align: top;
    }
    .priority-1 { color: var(--teal-dark); font-weight: 700; }
    .priority-2 { color: var(--grey-600); }

    /* Footer */
    .newsletter-footer {
      text-align: center;
      padding: 24px;
      font-size: 13px;
      color: var(--grey-600);
    }
    .newsletter-footer a { color: var(--teal-dark); text-decoration: none; }
    .newsletter-footer a:hover { text-decoration: underline; }

    /* Print / PDF styles */
    @media print {
      body { background: white; }
      .container { max-width: 100%; padding: 0; }
      .section { box-shadow: none; break-inside: avoid; }
      .expand-btn { display: none; }
      .card-detail { display: block !important; }
      .featured-card { break-inside: avoid; }
      .newsletter-header { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    }

    @media (max-width: 600px) {
      .featured-grid { grid-template-columns: 1fr; }
      .newsletter-header h1 { font-size: 24px; }
      .container { padding: 16px; }
    }
"""
