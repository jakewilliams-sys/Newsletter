---
shaping: true
---

# R&I Newsletter — Shaping

## Source

> Meeting: Simon / Jake — Newsletter (March 9, 2026)
>
> Key decisions: Move from auto-scanning Drive to a human-curated tracker approach.
> Quarterly newsletter, Q1 covering Dec 2025 – Mar 2026, published early April.
> Interactive HTML as primary output, PDF as secondary.
> Featured/listed content split by priority.
> "Meet the Customer" section using continuous discovery interviews.
> Deadline: April 3, 2026.

> Follow-up chat: Customer Corner workflow validated.
> Pipeline: Marvin (interview themes/quotes) → Askable (contact lookup) → Snowflake (order history).
> Participant: Maria Jula selected as first customer profile.
> Design of initial output deemed "very unsatisfactory and very generic AI-based" — full redesign required.

---

## Problem

The R&I team produces quarterly research that needs to reach a broad audience across Deliveroo — from senior stakeholders wanting key takeaways to anyone who would find the insights useful. There is no current vehicle for this. The initial automated build produced a generic, corporate-looking output that fails to engage readers or convey the quality of the team's work. The newsletter needs to feel modern, interactive, and memorable — a "wow" experience that people want to explore, not a bland document they scroll past.

## Outcome

A quarterly newsletter that:
- Feels like a modern web app, not a static document
- Makes readers want to explore and discover insights
- Integrates research summaries and a "Meet the Customer" profile seamlessly
- Is accessible via a shared link (no downloads)
- Represents the R&I team's work with the quality it deserves

---

## Requirements (R)

| ID | Requirement | Status |
|----|-------------|--------|
| R0 | Replace generic AI design with something distinctive, sleek, polished — a "wow" reaction | Core goal |
| R1 | Quarterly cadence — this issue covers Dec 2025 through Mar 2026, published early April | Must-have |
| R2 | Content sourced from Google Sheets tracker (priority, title, key insight, links, end date) | Must-have |
| R3 | "Meet the Customer" section integrated seamlessly — data from Marvin → Askable → Snowflake | Must-have |
| R4 | App-like navigation with transitions between views/sections, not a scrollable long page | Must-have |
| R5 | Works for broad audience: senior stakeholders (key takeaways) and any stakeholder (detail) | Must-have |
| R6 | 6–7 research pieces per issue; featured (P1) prominent, listed (P2) lighter | Must-have |
| R7 | Interactive HTML as primary output, shared via link (no downloads); PDF as secondary | Must-have |
| R8 | Teal accent for brand identity (headlines, opening); otherwise full creative freedom | Must-have |
| R9 | Built section by section with deliberate design choices per section | Must-have |

---

## Design Direction

| Decision | Detail |
|----------|--------|
| Aesthetic | Full creative licence. No reference design — brainstorm from scratch. Must feel modern, not corporate. |
| Navigation | App-like with distinct views/sections. Transitions between sections. Not vertical scrolling through a long document. |
| Interactivity | Open to enhancements that improve UX and flow. No features for features' sake. |
| Brand | Teal (#00CCBC) for headlines and opening. Beyond that, creative freedom. |
| Customer Corner | Minimalist. Stats with small graphs showing change. Story told through words. Easy to follow at more-than-a-glance. |
| Build approach | Section by section. Design and content brainstormed per section before building. |
| Hosting | Self-contained HTML file hosted via URL. Python pipeline generates the file; hosting solved separately. |

---

## Design Skills Plan

### Core (use on every section)
- **frontend-design** — Foundational. Distinctive, production-grade interfaces.
- **colorize** — Intentional colour system anchored on teal.
- **animate** — Section transitions, view changes, flow.
- **clarify** — Hierarchy and readability for mixed audience.
- **delight** — "Wow" moments, micro-interactions, personality.

### Per-section
- **distill** — Customer Corner especially. Keep it minimal.
- **critique** — Between iterations on each section.
- **polish** — Final pass before shipping each section.

### As needed
- **adapt** — Responsive design for tablet/phone.
- **bolder/quieter** — Dial up or down if a section feels too safe or too loud.
- **extract** — Reusable patterns once multiple sections exist.
- **audit** — Final accessibility and robustness check.

---

## Architecture

### Pipeline
```
Google Sheets tracker
        ↓
  TrackerReader (parse + validate)
        ↓
  SummarizerAgent (AI title rewrites + summaries for P1)
        ↓
  Marvin → Askable → Snowflake (Customer Corner data)
        ↓
  HTML Generator (app-like interactive newsletter)
        ↓
  Single self-contained HTML file
        ↓
  Host via URL → share link
        ↓
  (Later) PDF Generator (separate static layout)
```

### Content Sections

Three pill-nav sections. Each leads to genuinely distinct content.

| Pill | Content | Purpose |
|------|---------|---------|
| **Headlines** | P1 items (3-4) with enriched summaries, stats, deep dives, source links | The core content and default landing view. Both first impression and primary substance. |
| **More Research** | P2 items (3-4) with lighter treatment | Additional research outputs — scannable, brief. |
| **Meet the Customer** | Customer profile with stats, story | A completely different format — personal, narrative. |

**Structural decisions (resolved):**
- Opening/Landing is absorbed into Headlines — the brand moment is the app shell itself, not a separate welcome page.
- Appendix is replaced by inline source links at the bottom of each research item — links live where the context lives.
- Headlines merges what was previously "Headlines" (card overview) and "Featured Research" (deep content) — these were showing the same P1 items and the split confused the hierarchy.

---

## Important Note

Content (research items, order, volume) will change as the Google Sheet is populated. The design must accommodate variable content gracefully — the focus of this build is the design system and interaction patterns, not the specific content.

---

## Open Decisions

| # | Decision | Status | Notes |
|---|----------|--------|-------|
| D1 | Exact visual direction / aesthetic | ✅ Resolved | oklch teal, Instrument Sans + DM Mono, app shell with pill nav |
| D2 | Navigation mechanics | ✅ Resolved | Three-pill nav: Headlines · More Research · Meet the Customer |
| D3 | Colour palette beyond teal | Open | To be developed via colorize skill |
| D4 | Headlines section layout and interaction model | ✅ Resolved | Two-layer model: overview cards + expanding deep dives. Visual, infographic-style content. Floating page with backdrop overlay. |
| D5 | Customer Corner layout | ✅ Resolved | Direction A — scroll narrative. Single column, data story with scroll-triggered reveals, trend colouring, quotes woven between stats. |
| D6 | Hosting platform | Open | Solve later — architecture supports any static host |
| D7 | PDF layout | Open | Separate design phase after HTML is complete |
| D8 | Section structure and naming | ✅ Resolved | Three sections, appendix replaced by inline links |
| D9 | More Research section layout | ✅ Resolved | Direction C — compact full-width cards with teal accent bar. Same floating page deep dives as Headlines. |

---

## Build Order

Work section by section:

1. ~~**Colour system + overall aesthetic**~~ — ✅ Established (oklch teal, Instrument Sans + DM Mono)
2. ~~**Navigation / app shell**~~ — ✅ Established (pill nav, topbar, full viewport — `chosen_direction.html`)
3. ~~**Section structure + naming**~~ — ✅ Resolved (3 pills: Headlines · More Research · Meet the Customer)
4. ~~**Headlines**~~ — ✅ Built (hero + cards, floating page deep dives, backdrop, click-outside-to-close)
5. ~~**More Research**~~ — ✅ Built (Direction C — compact full-width cards with teal accent, same floating page deep dives)
6. ~~**Meet the Customer**~~ — ✅ Built (story-driven scroll narrative with chapters, evidence blocks, scroll-triggered reveals)
7. ~~**Combine all sections**~~ — ✅ Built (`newsletter_combined.html` — working pill nav, all interactions preserved)
8. **Research deep-dive formatting** — How to present each piece of research ← **Next**
9. **Polish + animate + delight pass** — Final quality across all sections
10. **PDF layout** — Separate static design

---

# Headlines — Section Shaping

## Context

Headlines is the core content section AND the default landing view — the first thing readers see when they open the newsletter. It presents 3-4 P1 research outputs from the quarter.

This section does double duty: it's both the first impression (brand moment, orient the reader) and the primary content (engaging deep dives with data visualizations, key findings, and source links). The chosen direction prototype (`chosen_direction.html`) shows a card-based layout with stat chips — this is the starting visual vocabulary for the overview layer.

**Content source:** The Google Sheet tracker provides metadata and a flavour sentence per item. The real substance comes from the linked source documents (Google Docs/Slides) — full research reports from which key findings, data points, and visualizations are extracted. The newsletter is the highlight reel; the source link takes readers to the full report.

## Requirements (HL)

| ID | Requirement | Status |
|----|-------------|--------|
| HL0 | Present 3-4 P1 research items as the newsletter's primary content — this section must feel like the most important part of the newsletter | Core goal |
| HL1 | Serve two reading speeds within one section: scannable (30s — overview cards with titles and stats) and engaging (2-3 min per item — visual deep dives with data and infographics) | Must-have |
| HL2 | Two-layer model: overview (card grid) and deep dive (expanded card with full content) — card expands in place to maintain spatial continuity | Must-have |
| HL3 | Deep dive content is engaging and visual — infographics, animated data reveals, styled callouts — not text-heavy paragraphs | Must-have |
| HL4 | Each item displays on card: tag/category, action-oriented title, key stat, author | Must-have |
| HL5 | Each deep dive ends with inline links to source documents — "Read the full report →" | Must-have |
| HL6 | Navigate between expanded items with a page-turn-style transition — makes it feel like flipping through a publication, reinforces that you're still in Headlines | Must-have |
| HL7 | Content blocks are flexible per item — stat callouts, charts/visualizations, key findings, pull quotes, narrative lines — mixed and matched based on the source material | Must-have |
| HL8 | Works as the default landing view — first impression, brand moment, quarter context — without being a separate "welcome" page | Must-have |
| HL9 | Integrates with the app shell — pill nav (Headlines active), consistent topbar, transitions to other sections | Must-have |
| HL10 | Key stats/numbers should be visually prominent — they're the hook that draws readers in | Must-have |
| HL11 | Each item curated individually — the best way to present data is determined per project based on what's in the source material | Must-have |

## Resolved Questions

| # | Question | Resolution |
|---|----------|------------|
| HQ1 | Single view or individual item views? | **Both.** Overview shows all items as cards (scan). Clicking a card expands it in place to show the deep dive (read). Other cards fade away; the expanded card fills the content area. |
| HQ2 | How is progressive disclosure handled? | **Card expansion.** The overview IS the scan layer. The expanded card IS the read layer. No expand/collapse toggles — the card itself is the disclosure mechanism. |
| HQ3 | Hero treatment for the first item? | **Open — to be decided during design.** The boss curates headline priority. If there's a clear lead story, the first card could get hero treatment (larger, more visual weight). |
| HQ4 | What happens at the bottom of Headlines? | **Open — to be decided during design.** Likely a soft visual bridge to "More Research" for readers who reach the bottom and want to keep going. |

## Interaction Model

### Overview → Deep Dive
1. Reader clicks a card on the overview
2. Other cards fade out / slide away
3. Selected card expands to fill the content area
4. Deep dive content (infographics, data, narrative, source links) fades in
5. Pill nav stays fixed — "Headlines" remains active throughout

### Deep Dive → Overview
1. Reader clicks close/collapse (or a "back to headlines" link)
2. Deep dive content fades out
3. Card contracts back to its position in the grid
4. Other cards reappear — overview is restored

### Deep Dive → Next Item
1. Reader clicks "Next" (or swipes/navigates right)
2. Current content transitions out with a page-turn-style effect
3. Next item's content transitions in
4. Feels like flipping through a publication — smooth, continuous, still within Headlines
5. Reader can traverse all headline items without returning to the overview

### Content Blocks (per item)

Each deep dive is composed of flexible content blocks, mixed and matched per item:

| Block | Use case | Example |
|-------|----------|---------|
| **Stat callout** | Every item — the headline number | "3.2× higher order frequency" |
| **Chart / visualization** | Quantitative research — trends, comparisons, breakdowns | Awareness over time, retention curves |
| **Key findings** | 3-4 main takeaways, styled as visual callouts not bullet lists | Behavioural insights, preference rankings |
| **Pull quote** | Qualitative insights, standout lines from research | Consumer quotes, interview highlights |
| **Narrative line** | 1-2 sentences framing the data — minimal, not paragraphs | Context for why the finding matters |
| **Source link** | Every item — always at the bottom | "Read the full report →" |

Items are curated individually. A brand tracker might use stat + chart + narrative. A qualitative study might use stat + key findings + pull quote. The visual vocabulary is shared; the composition varies.

## Design Notes (for implementation phase)

- **Animation philosophy:** Card expansion, page-turn transitions, and data reveals (numbers counting up, charts drawing in) are key delight moments. These will be developed during the animate/delight phase once the structure is built.
- **Content creation:** Each item requires individual curation — extracting the right data, choosing the right visualization, writing the narrative framing. This is partly automated (summarizer enrichment) and partly editorial (choosing what to highlight).
- **Responsive:** Expanded cards on mobile become full-screen views. Infographics must work at narrow widths.

---

# Meet the Customer — Section Shaping

## Context

Meet the Customer is a completely different format from the research sections. One customer profile per quarter, drawn from continuous discovery interviews. The data pipeline is Marvin (interview transcripts/quotes) → Askable (contact lookup) → Snowflake (full order history and behavioural data).

This section humanises the data — it puts a real person behind the numbers. But it's not just "here's a random person." Each featured customer connects to a business-relevant theme from the quarter, creating a bridge between the personal and the analytical.

**Data available from Snowflake:** Order frequency, tenure, cuisine preferences, favourite restaurants, Plus membership status, average basket cost, time-of-day patterns, ordering trends over time, and any other order-level data.

**Data available from Marvin:** Full interview transcripts from which quotes, themes, and motivations can be extracted.

**Privacy:** First name only, city-level location, no photo, no surname.

## Requirements (MC)

| ID | Requirement | Status |
|----|-------------|--------|
| MC0 | Present one customer per quarter as a personal, humanising counterpoint to the research sections | Core goal |
| MC1 | Connect the customer to a business-relevant theme — "why are we showing them this?" must be immediately clear | Must-have |
| MC2 | Single-page scroll narrative — no cards, no grid, no expansion. Flows vertically as a story. | Must-have |
| MC3 | Show personal ordering data from Snowflake — frequency, cuisines, basket, time patterns, trends over time | Must-have |
| MC4 | Weave Marvin interview quotes between data blocks — data and voice reinforce each other | Must-have |
| MC5 | Trend colouring for data — green-tinted accents for positive trends, warm amber/coral for declines or shifts | Must-have |
| MC6 | Before/after comparisons — show how behaviour has changed (e.g. 6 months ago vs now) to make every stat a mini-story | Must-have |
| MC7 | Minimalist and spacious — lots of whitespace, one element at a time, clean typography. Not a dashboard. | Must-have |
| MC8 | Scroll-triggered reveals — data blocks fade in as they enter viewport, numbers count up, bars animate | Must-have |
| MC9 | Personal data visualisations — week heatmap (ordering rhythm), cuisine breakdown, frequency sparkline | Must-have |
| MC10 | Closing connection — link this customer back to a relevant headline research piece | Nice-to-have |
| MC11 | Privacy-respecting — first name only, city-level location, no photo, no surname | Must-have |
| MC12 | Visually distinct from research sections — feels like a genuine change of pace when switching to this pill | Must-have |

## Resolved Questions

| # | Question | Resolution |
|---|----------|------------|
| MQ1 | How many customers per issue? | **One.** Single-page experience, no navigation needed. |
| MQ2 | How personal? | **First name, city only.** No photo, no surname. Broad enough to feel real, private enough to be comfortable. |
| MQ3 | What's the narrative structure? | **Humanising + relevant.** Their ordering story and life, but framed around why their behaviour matters to the business this quarter. |
| MQ4 | Editorial magazine piece or minimalist? | **Minimalist.** Data-forward with quotes woven in. Not paragraphs of editorial writing. The data tells the story; the quotes add colour. |
| MQ5 | Scroll animations? | **Yes — subtle scroll-triggered reveals.** Data blocks fade in as they arrive, numbers count up, bars animate. Not flashy transitions — the data "arriving" as you scroll, making the page feel alive. |
| MQ6 | Layout direction? | **Direction A — scroll narrative.** Single column, vertical flow. The most different from the card-based research sections. |

## Content Flow

The page scrolls through these blocks in order:

| Block | Content | Visual Treatment |
|-------|---------|-----------------|
| **Hook** | One sentence connecting this customer to a business theme | Prominent, slightly larger text. Sets the "why" immediately. |
| **Profile strip** | First name, city, tenure, Plus status | Clean data card — name large, identifiers small underneath. |
| **Ordering rhythm** | Week heatmap (Mon–Sun × morning/afternoon/evening) | Grid of cells, darker = more orders. Their personal pattern. |
| **Key stats** | Order frequency, avg basket, top cuisines | One stat per block, each with before/after trend + trend colour. Numbers count up on scroll reveal. |
| **Quote 1** | Interview quote explaining a behaviour | Styled differently from research quotes — more intimate, lighter treatment. |
| **Cuisine breakdown** | Top 3-4 cuisines with proportions | Small horizontal bars or minimal donut. Personal, not analytical. |
| **Frequency sparkline** | 6-month order frequency trend | Tiny line chart, no axes — just the shape. Trend colour applied. |
| **Quote 2** | Another perspective from the interview | Bridges between data sections. |
| **Favourite spots** | Top 3 restaurants with order count | Simple list, maybe with a small repeat-order indicator. |
| **Time-of-day pattern** | When they order most | Radial chart or simple bar for time slots. |
| **Quote 3** | Closing voice — something that sticks | The most memorable or revealing quote. |
| **Connection** | Links to related headline research | Subtle tinted card with arrow link. |

## Design Notes

- **Colour strategy:** Base palette stays the same (teal, ink, surface). Add two trend accents: a green-tinted oklch for positive movement, and a warm amber/coral oklch for declines or notable shifts. These only appear on trend indicators, not as section colours.
- **Typography:** Same Instrument Sans + DM Mono system. Name could be slightly larger/bolder to feel personal. Stats use DM Mono for numbers as in research sections.
- **Whitespace:** More generous than research sections. Each block gets significant breathing room. The page should feel airy, almost sparse.
- **No floating page:** This section is already a single-page experience. No cards to expand, no backdrop needed. Just scroll.
