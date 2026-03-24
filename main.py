"""
R&I Newsletter Automation System (v2 - Tracker-Driven)

Orchestrates the pipeline: Google Sheet tracker -> enrichment -> interactive HTML -> PDF.

Usage:
    # Full pipeline via Cursor with MCP:
    python main.py

    # Test with sample data:
    python main.py --test

    # Custom output directory:
    python main.py --output ./my_output
"""
import argparse
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, str(Path(__file__).parent))

from config import (
    GOOGLE_EMAIL,
    TRACKER_SPREADSHEET_ID,
    TRACKER_RANGE,
    NEWSLETTER_TITLE,
    NEWSLETTER_QUARTER,
    NEWSLETTER_YEAR,
    OUTPUT_DIR,
    CUSTOMER_CORNER_ENABLED,
)
from agents.tracker_reader import TrackerReader, ResearchOutput
from agents.summarizer import SummarizerAgent
from agents.html_generator import HTMLNewsletterGenerator
from agents.pdf_exporter import PDFExporter
from agents.customer_corner import CustomerCorner, CustomerProfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("newsletter")


class NewsletterOrchestrator:
    """
    Coordinates the full newsletter pipeline:

    1. Read tracker sheet (via MCP result or test data)
    2. Fetch and enrich linked documents (optional)
    3. Summarise / title-rewrite featured items
    4. Build interactive HTML newsletter
    5. Export PDF
    6. Optionally upload to Drive
    """

    def __init__(self, output_dir: Optional[str] = None):
        self.output_dir = output_dir or OUTPUT_DIR
        self.reader = TrackerReader()
        self.summarizer = SummarizerAgent(use_ai=True)
        self.html_gen = HTMLNewsletterGenerator()
        self.pdf_exporter = PDFExporter()
        self.customer_corner = CustomerCorner()

        self.outputs: List[ResearchOutput] = []
        self.html_content: str = ""
        self.static_html: str = ""

    def run(
        self,
        sheet_data: str,
        content_map: Optional[Dict[str, str]] = None,
        customer_profile: Optional[CustomerProfile] = None,
    ) -> Dict[str, str]:
        """
        Execute the full pipeline.

        Args:
            sheet_data: Raw string from read_sheet_values MCP call
            content_map: Optional dict mapping doc URLs to fetched content
            customer_profile: Optional customer data for Customer Corner

        Returns:
            Dict with paths to generated artifacts
        """
        logger.info("=" * 60)
        logger.info("R&I NEWSLETTER PIPELINE — %s %s", NEWSLETTER_QUARTER, NEWSLETTER_YEAR)
        logger.info("=" * 60)

        # Step 1: Ingest tracker
        logger.info("Step 1: Reading tracker submissions...")
        self.outputs = self.reader.read_from_mcp_result(sheet_data)
        stats = self.reader.get_stats()
        logger.info(
            "  %d outputs (%d featured, %d listed)",
            stats["total_outputs"],
            stats["featured_count"],
            stats["listed_count"],
        )

        validation_report = self.reader.get_validation_report()
        if self.reader.validation_log:
            logger.warning("  Validation issues:\n%s", validation_report)

        # Step 2: Enrich with summaries + title rewrites
        logger.info("Step 2: Enriching outputs...")
        self.outputs = self.summarizer.enrich_outputs(self.outputs, content_map)
        featured = self.reader.get_featured()
        listed = self.reader.get_listed()
        logger.info(
            "  Enriched %d featured items, %d listed items",
            len(featured),
            len(listed),
        )

        # Step 3: Customer corner
        customer_html = ""
        if CUSTOMER_CORNER_ENABLED and customer_profile:
            logger.info("Step 3: Rendering Customer Corner...")
            customer_html = self.customer_corner.render(customer_profile)
        else:
            logger.info("Step 3: Customer Corner skipped (no profile provided)")

        # Step 4: Generate HTML
        logger.info("Step 4: Generating HTML newsletter...")
        self.html_content = self.html_gen.generate(
            featured, listed, customer_html, static=False
        )
        self.static_html = self.html_gen.generate(
            featured, listed, customer_html, static=True
        )

        # Step 5: Save outputs
        logger.info("Step 5: Saving outputs...")
        os.makedirs(self.output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d")

        html_path = os.path.join(self.output_dir, f"newsletter_{timestamp}.html")
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(self.html_content)
        logger.info("  HTML saved: %s", html_path)

        # Step 6: Export PDF
        logger.info("Step 6: Exporting PDF...")
        pdf_path = os.path.join(self.output_dir, f"newsletter_{timestamp}.pdf")
        actual_pdf_path = self.pdf_exporter.export(self.static_html, pdf_path)
        logger.info("  PDF saved: %s", actual_pdf_path)

        logger.info("=" * 60)
        logger.info("NEWSLETTER GENERATION COMPLETE")
        logger.info("=" * 60)

        return {
            "html": html_path,
            "pdf": actual_pdf_path,
            "stats": stats,
            "validation": validation_report,
        }


SAMPLE_SHEET_DATA = """Successfully read 8 rows from range 'Submissions!A1:F10':
Row  1: ['Submitted By', 'Priority', 'Project Title', 'Key Insight', 'Link to Output(s)', 'Project End Date']
Row  2: ['Jake Williams', '1', 'Student Immersion Research', 'Deep-dive into student ordering behaviour revealing key drivers of adoption and frequency among 18-24 year olds', 'https://docs.google.com/document/d/example1', 'March 2026']
Row  3: ['Simon Jones', '2', 'Partner NPS Segmentation Analysis', 'Segmentation of partner satisfaction scores identifying three distinct partner archetypes with different needs', 'https://docs.google.com/presentation/d/example2', 'February 2026']
Row  4: ['Holly Ohanian', '1', 'YouGov Brand Tracker Q1 2026', 'Quarterly brand health metrics showing Deliveroo awareness growth in key demographics versus competitors', 'https://docs.google.com/document/d/example3', 'March 2026']
Row  5: ['Andrea Aggio', '1', 'Plus Membership Deep-Dive', 'Plus members order 3.2x more frequently and show 40% higher retention — growth opportunity in student segment', 'https://docs.google.com/presentation/d/example4', 'January 2026']
Row  6: ['Molly McCormick', '2', 'Medallia VoC Monthly Digest', 'Customer satisfaction stable at 4.2/5 with delivery speed complaints down 12% month-on-month', 'https://docs.google.com/document/d/example5', 'February 2026']
Row  7: ['Bea Jones', '2', 'Competitor Landscape February 2026', 'Just Eat gaining share in suburban areas while Uber Eats focuses on grocery vertical expansion', 'https://docs.google.com/document/d/example6', 'February 2026']
Row  8: ['Sannah Siddique', '1', 'French Market Consumer Preferences', 'French consumers strongly prefer evening delivery slots and prioritise restaurant quality over speed', 'https://docs.google.com/document/d/example7', 'March 2026']
"""


def run_test_mode(output_dir: str) -> Dict:
    """Run with sample data to validate the pipeline."""
    logger.info("Running in TEST MODE with sample data...")

    sample_profile = CustomerProfile(
        name="Maria J.",
        location="London, SE5",
        age=30,
        customer_since="Feb 2017",
        plus_plan="Plus Silver",
        total_orders=46,
        headline="Long-term Plus subscriber who values convenience, broad restaurant selection, and credits — but wants Deliveroo to raise the bar on delivery quality and customer support.",
        interview_theme="Deliveroo Plus & CX Quality",
        interview_summary="Maria is a loyal Plus Silver member who's been ordering for almost a decade. She uses Deliveroo for everything from grocery top-ups to late-night treats and social occasions. Her main frustrations? Cold food arrivals, checkout defaulting to substitutes instead of cancellations, and customer support closing cases without proper review.",
        quote="I'd pay more for my membership if I knew support would actually have my back when things go wrong.",
        quote_context="On whether improved support reliability would increase willingness to pay",
        top_restaurants=[
            ("Creams - Ealing", 5),
            ("Kin - Foley Street", 3),
            ("L'oro Di Napoli", 2),
            ("Santa Maria Pizzeria - Ealing", 2),
            ("Oowee Vegan - Brixton", 2),
        ],
        peak_time="Evenings (6–9pm)",
        recent_orders=[
            ("11 Mar", "Kin - Foley Street"),
            ("8 Mar", "Kin - Foley Street"),
            ("5 Mar", "Sainsbury's - Elephant & Castle"),
            ("4 Mar", "Acai Girls - Victoria"),
            ("3 Mar", "German Doner Kebab"),
        ],
        ordering_insight="Maria's ordering has surged recently — 5 orders in March alone after a quieter winter. Her current favourite, Kin on Foley Street, has become a twice-a-week habit.",
    )

    orchestrator = NewsletterOrchestrator(output_dir=output_dir)
    return orchestrator.run(
        sheet_data=SAMPLE_SHEET_DATA,
        customer_profile=sample_profile,
    )


def run_live_mode(sheet_data: str, output_dir: str) -> Dict:
    """Run with live MCP sheet data."""
    orchestrator = NewsletterOrchestrator(output_dir=output_dir)
    return orchestrator.run(sheet_data=sheet_data)


def parse_args():
    parser = argparse.ArgumentParser(description="R&I Newsletter Automation System")
    parser.add_argument("--test", action="store_true", help="Run with sample data")
    parser.add_argument("--output", type=str, default=None, help="Output directory")
    return parser.parse_args()


def main():
    args = parse_args()
    output_dir = args.output or OUTPUT_DIR

    if args.test:
        result = run_test_mode(output_dir)
        print(f"\nHTML: {result['html']}")
        print(f"PDF:  {result['pdf']}")
    else:
        print("R&I Newsletter Automation System (v2)")
        print("-" * 40)
        print()
        print("This system runs via Cursor with MCP integration.")
        print("The pipeline:")
        print("  1. Read the tracker spreadsheet via read_sheet_values")
        print("  2. Enrich featured outputs with AI summaries")
        print("  3. Generate interactive HTML newsletter")
        print("  4. Export PDF for distribution")
        print()
        print("To test with sample data: python main.py --test")


if __name__ == "__main__":
    main()
