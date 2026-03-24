"""
Summarizer Agent - Enriches research outputs with AI-generated summaries and titles
"""
import os
import re
import logging
from typing import List, Dict, Any, Optional

try:
    from anthropic import Anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

import sys
sys.path.append('..')
from config import GOOGLE_EMAIL, ANTHROPIC_API_KEY, MAX_SUMMARY_LENGTH_FEATURED, MAX_SUMMARY_LENGTH_LISTED
from .tracker_reader import ResearchOutput

logger = logging.getLogger(__name__)


class SummarizerAgent:
    """
    Enriches ResearchOutput objects with AI-generated summaries and
    action-oriented title rewrites for featured items.
    """

    TITLE_REWRITE_PROMPT = """You are writing titles for a research newsletter at Deliveroo's Research & Insights team.

Rewrite this project title into an action-oriented headline that tells the reader what they should know or do.

Original title: {title}
Description: {description}

Rules:
- Focus on the finding or required action, NOT the research activity
- Good: "French consumers prefer evening delivery slots" or "Partner churn drops 15% with new onboarding"
- Bad: "We did research in France" or "Partner NPS Study"
- Keep it under 12 words
- Do not use quotation marks in your response
- Return ONLY the rewritten title, nothing else"""

    SUMMARY_PROMPT = """You are summarising research for a quarterly newsletter at Deliveroo's Research & Insights team.

Project: {title}
Description: {description}

Source content (excerpt):
{content}

Write a concise 2-3 sentence summary that:
1. Leads with the key finding or business impact
2. Is written for senior stakeholders who need to act on insights
3. Avoids jargon and focuses on what matters

Keep the summary under {max_length} characters. Do not include the project title."""

    def __init__(self, use_ai: bool = True):
        self.use_ai = use_ai and HAS_ANTHROPIC
        self.client = None

        if self.use_ai and ANTHROPIC_API_KEY:
            self.client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def enrich_outputs(
        self,
        outputs: List[ResearchOutput],
        content_map: Optional[Dict[str, str]] = None,
    ) -> List[ResearchOutput]:
        """
        Enrich research outputs with rewritten titles and expanded summaries.

        Args:
            outputs: List of ResearchOutput objects from the tracker
            content_map: Optional dict mapping link URLs to fetched document content

        Returns:
            The same list with enriched_summary and rewritten_title populated
        """
        content_map = content_map or {}

        for output in outputs:
            try:
                source_content = self._get_source_content(output, content_map)
                output.source_content = source_content

                if output.is_featured:
                    output.rewritten_title = self._rewrite_title(output)
                    output.enriched_summary = self._generate_summary(
                        output, source_content, MAX_SUMMARY_LENGTH_FEATURED
                    )
                else:
                    output.enriched_summary = output.description

            except Exception as e:
                logger.warning("Failed to enrich '%s': %s", output.title, e)
                output.enriched_summary = output.description

        return outputs

    def _get_source_content(
        self, output: ResearchOutput, content_map: Dict[str, str]
    ) -> str:
        """Extract source content from the content map using output links."""
        for link in output.output_links:
            content = content_map.get(link, "")
            if content:
                return self._clean_content(content)
        return ""

    def _clean_content(self, content: str) -> str:
        """Normalise whitespace and truncate for summarisation."""
        if not content:
            return ""
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r' {2,}', ' ', content)
        if len(content) > 5000:
            content = content[:5000] + "..."
        return content.strip()

    def _rewrite_title(self, output: ResearchOutput) -> str:
        """Rewrite a project title to be action-oriented."""
        if not self.client:
            return output.title

        try:
            prompt = self.TITLE_REWRITE_PROMPT.format(
                title=output.title,
                description=output.description,
            )
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=60,
                messages=[{"role": "user", "content": prompt}],
            )
            rewritten = message.content[0].text.strip().strip('"\'')
            return rewritten
        except Exception as e:
            logger.warning("Title rewrite failed for '%s': %s", output.title, e)
            return output.title

    def _generate_summary(
        self, output: ResearchOutput, source_content: str, max_length: int
    ) -> str:
        """Generate an enriched summary using AI or fall back to description."""
        if not self.client:
            return output.description

        content_excerpt = source_content[:3000] if source_content else "No source document available."

        try:
            prompt = self.SUMMARY_PROMPT.format(
                title=output.title,
                description=output.description,
                content=content_excerpt,
                max_length=max_length,
            )
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=250,
                messages=[{"role": "user", "content": prompt}],
            )
            return message.content[0].text.strip()
        except Exception as e:
            logger.warning("Summary generation failed for '%s': %s", output.title, e)
            return output.description
