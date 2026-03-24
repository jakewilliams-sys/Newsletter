"""
Customer Corner - Renders a "Meet the Customer" profile for the newsletter.

Combines continuous discovery interview insights with Deliveroo ordering
data to produce an editorial-style profile section. Data is sourced from
Marvin (interviews), Askable (contact details), and Snowflake (orders).
"""
import html
import logging
from typing import Optional, List, Tuple
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CustomerProfile:
    """Rich customer data combining interview insights with ordering history."""
    name: str
    location: str = ""
    age: int = 0
    customer_since: str = ""
    plus_plan: str = ""
    total_orders: int = 0
    headline: str = ""
    interview_theme: str = ""
    interview_summary: str = ""
    quote: str = ""
    quote_context: str = ""
    top_restaurants: List[Tuple[str, int]] = field(default_factory=list)
    peak_time: str = ""
    recent_orders: List[Tuple[str, str]] = field(default_factory=list)
    ordering_insight: str = ""
    image_url: str = ""


class CustomerCorner:
    """
    Renders the Meet the Customer section of the newsletter.

    Toggle on/off via config.CUSTOMER_CORNER_ENABLED. Pass a CustomerProfile
    to render, or call with None to get an empty string (section omitted).
    """

    def render(self, profile: Optional[CustomerProfile] = None) -> str:
        if profile is None:
            return ""

        esc = html.escape

        # Stats ribbon
        stats = []
        if profile.customer_since:
            stats.append(("Customer since", profile.customer_since))
        if profile.total_orders:
            stats.append(("Lifetime orders", str(profile.total_orders)))
        if profile.plus_plan:
            stats.append(("Plus plan", profile.plus_plan))
        if profile.peak_time:
            stats.append(("Peak ordering", profile.peak_time))

        stats_html = "".join(
            f'<div class="cc-stat"><span class="cc-stat-val">{esc(val)}</span>'
            f'<span class="cc-stat-lbl">{esc(lbl)}</span></div>'
            for lbl, val in stats
        )

        # Quote
        quote_html = ""
        if profile.quote:
            ctx = f'<span class="cc-quote-ctx">{esc(profile.quote_context)}</span>' if profile.quote_context else ""
            quote_html = (
                f'<blockquote class="cc-quote">'
                f'<span class="cc-quote-mark">&ldquo;</span>'
                f'{esc(profile.quote)}'
                f'<span class="cc-quote-mark">&rdquo;</span>'
                f'{ctx}</blockquote>'
            )

        # Favourite restaurants
        fav_html = ""
        if profile.top_restaurants:
            items = ""
            for i, (name, count) in enumerate(profile.top_restaurants[:5]):
                bar_w = min(100, int((count / profile.top_restaurants[0][1]) * 100))
                items += (
                    f'<div class="cc-fav">'
                    f'<span class="cc-fav-rank">{i + 1}</span>'
                    f'<div class="cc-fav-body">'
                    f'<span class="cc-fav-name">{esc(name)}</span>'
                    f'<div class="cc-fav-bar-bg"><div class="cc-fav-bar" style="width:{bar_w}%"></div></div>'
                    f'</div>'
                    f'<span class="cc-fav-cnt">{count}</span>'
                    f'</div>'
                )
            fav_html = f'<div class="cc-favs"><h4 class="cc-sub">Top restaurants</h4>{items}</div>'

        # Recent orders timeline
        recent_html = ""
        if profile.recent_orders:
            dots = ""
            for date, restaurant in profile.recent_orders[:5]:
                dots += (
                    f'<div class="cc-tl-item">'
                    f'<span class="cc-tl-dot"></span>'
                    f'<span class="cc-tl-date">{esc(date)}</span>'
                    f'<span class="cc-tl-rest">{esc(restaurant)}</span>'
                    f'</div>'
                )
            recent_html = f'<div class="cc-timeline"><h4 class="cc-sub">Recent orders</h4>{dots}</div>'

        # Interview insight callout
        insight_html = ""
        if profile.interview_summary:
            insight_html = (
                f'<div class="cc-insight">'
                f'<span class="cc-insight-tag">{esc(profile.interview_theme or "Continuous Discovery")}</span>'
                f'<p class="cc-insight-text">{esc(profile.interview_summary)}</p>'
                f'</div>'
            )

        # Ordering insight
        ordering_insight_html = ""
        if profile.ordering_insight:
            ordering_insight_html = f'<p class="cc-ord-insight">{esc(profile.ordering_insight)}</p>'

        # Location + age tagline
        tagline_parts = []
        if profile.age:
            tagline_parts.append(f"{profile.age}")
        if profile.location:
            tagline_parts.append(profile.location)
        tagline = " · ".join(tagline_parts)

        return f"""
      <div class="cc-section">
        <div class="cc-label">Meet the Customer</div>
        <div class="cc-card">
          <div class="cc-header">
            <div class="cc-identity">
              <h3 class="cc-name">{esc(profile.name)}</h3>
              <p class="cc-tagline">{esc(tagline)}</p>
              <p class="cc-headline">{esc(profile.headline)}</p>
            </div>
          </div>
          <div class="cc-stats">{stats_html}</div>
          {quote_html}
          {insight_html}
          <div class="cc-data-grid">
            {fav_html}
            <div class="cc-data-right">
              {recent_html}
              {ordering_insight_html}
            </div>
          </div>
        </div>
      </div>
      <style>
        .cc-section {{
          margin: 40px 0;
        }}
        .cc-label {{
          font-family: 'Source Sans 3', 'Source Sans Pro', sans-serif;
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 1.5px;
          color: #00CCBC;
          margin-bottom: 12px;
        }}
        .cc-card {{
          background: #FAFBFB;
          border: 1px solid #E8EAEB;
          border-radius: 4px;
          padding: 32px;
        }}
        .cc-header {{
          margin-bottom: 24px;
        }}
        .cc-name {{
          font-size: 24px;
          font-weight: 700;
          color: #2E3333;
          margin: 0 0 4px 0;
          line-height: 1.2;
        }}
        .cc-tagline {{
          font-size: 13px;
          color: #858B8B;
          margin: 0 0 8px 0;
          font-weight: 500;
        }}
        .cc-headline {{
          font-size: 15px;
          color: #585E5E;
          margin: 0;
          line-height: 1.5;
        }}
        .cc-stats {{
          display: flex;
          gap: 0;
          border-top: 1px solid #E8EAEB;
          border-bottom: 1px solid #E8EAEB;
          margin-bottom: 24px;
        }}
        .cc-stat {{
          flex: 1;
          padding: 16px 0;
          text-align: center;
          border-right: 1px solid #E8EAEB;
        }}
        .cc-stat:last-child {{ border-right: none; }}
        .cc-stat-val {{
          display: block;
          font-size: 16px;
          font-weight: 700;
          color: #2E3333;
        }}
        .cc-stat-lbl {{
          display: block;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: #858B8B;
          margin-top: 4px;
        }}
        .cc-quote {{
          margin: 0 0 24px 0;
          padding: 20px 24px;
          background: #f0faf9;
          border-left: 3px solid #00CCBC;
          border-radius: 0 4px 4px 0;
          font-size: 15px;
          line-height: 1.7;
          color: #2E3333;
          font-style: italic;
          position: relative;
        }}
        .cc-quote-mark {{
          color: #00CCBC;
          font-size: 20px;
          font-style: normal;
          font-weight: 700;
        }}
        .cc-quote-ctx {{
          display: block;
          font-style: normal;
          font-size: 12px;
          color: #858B8B;
          margin-top: 8px;
        }}
        .cc-insight {{
          background: #2E3333;
          color: #F5F6F6;
          padding: 20px 24px;
          border-radius: 4px;
          margin-bottom: 24px;
        }}
        .cc-insight-tag {{
          display: inline-block;
          font-size: 10px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 1px;
          color: #00CCBC;
          background: rgba(0,204,188,0.12);
          padding: 3px 8px;
          border-radius: 2px;
          margin-bottom: 10px;
        }}
        .cc-insight-text {{
          font-size: 14px;
          line-height: 1.65;
          margin: 0;
          color: #D4D6D6;
        }}
        .cc-sub {{
          font-size: 11px;
          font-weight: 700;
          text-transform: uppercase;
          letter-spacing: 0.8px;
          color: #858B8B;
          margin: 0 0 12px 0;
        }}
        .cc-data-grid {{
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 32px;
        }}
        .cc-favs {{ }}
        .cc-fav {{
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 6px 0;
        }}
        .cc-fav-rank {{
          font-size: 11px;
          font-weight: 700;
          color: #858B8B;
          width: 16px;
          text-align: right;
          flex-shrink: 0;
        }}
        .cc-fav-body {{ flex: 1; min-width: 0; }}
        .cc-fav-name {{
          font-size: 13px;
          font-weight: 600;
          color: #2E3333;
          display: block;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }}
        .cc-fav-bar-bg {{
          height: 3px;
          background: #E8EAEB;
          border-radius: 2px;
          margin-top: 4px;
        }}
        .cc-fav-bar {{
          height: 100%;
          background: #00CCBC;
          border-radius: 2px;
        }}
        .cc-fav-cnt {{
          font-size: 12px;
          font-weight: 600;
          color: #858B8B;
          flex-shrink: 0;
        }}
        .cc-data-right {{ }}
        .cc-timeline {{ }}
        .cc-tl-item {{
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 5px 0;
          position: relative;
        }}
        .cc-tl-dot {{
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: #00CCBC;
          flex-shrink: 0;
        }}
        .cc-tl-date {{
          font-size: 12px;
          color: #858B8B;
          width: 56px;
          flex-shrink: 0;
          font-variant-numeric: tabular-nums;
        }}
        .cc-tl-rest {{
          font-size: 13px;
          color: #2E3333;
          font-weight: 500;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }}
        .cc-ord-insight {{
          font-size: 13px;
          line-height: 1.6;
          color: #585E5E;
          margin: 16px 0 0 0;
          padding-top: 12px;
          border-top: 1px solid #E8EAEB;
        }}
      </style>"""
