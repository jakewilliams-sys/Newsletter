"""
Tracker Reader Agent - Ingests research outputs from the Google Sheets tracker
"""
import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

import sys
sys.path.append('..')
from config import (
    GOOGLE_EMAIL,
    TRACKER_SPREADSHEET_ID,
    TRACKER_RANGE,
)

logger = logging.getLogger(__name__)


@dataclass
class ResearchOutput:
    """A single research output submitted via the tracker."""
    submitter: str
    priority: int
    title: str
    description: str
    output_links: List[str] = field(default_factory=list)
    project_end_date: str = ""
    rewritten_title: str = ""
    enriched_summary: str = ""
    source_content: str = ""
    validation_warnings: List[str] = field(default_factory=list)

    @property
    def is_featured(self) -> bool:
        return self.priority == 1

    @property
    def display_title(self) -> str:
        return self.rewritten_title or self.title

    @property
    def display_summary(self) -> str:
        return self.enriched_summary or self.description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "submitter": self.submitter,
            "priority": self.priority,
            "title": self.title,
            "description": self.description,
            "output_links": self.output_links,
            "project_end_date": self.project_end_date,
            "rewritten_title": self.rewritten_title,
            "enriched_summary": self.enriched_summary,
            "validation_warnings": self.validation_warnings,
        }


class TrackerReader:
    """
    Reads and validates research output submissions from the Google Sheets tracker.

    Parses rows into ResearchOutput objects, applies validation rules from the
    data contract, and splits outputs into featured vs listed categories.
    """

    HEADER_FIELDS = [
        "submitted by",
        "priority",
        "project title",
        "key insight",
        "link to output",
        "project end date",
    ]

    def __init__(self):
        self.outputs: List[ResearchOutput] = []
        self.validation_log: List[str] = []
        self._raw_rows: List[List[str]] = []

    def read_from_mcp_result(self, mcp_result: str) -> List[ResearchOutput]:
        """
        Parse the string output from read_sheet_values MCP call.

        Args:
            mcp_result: Raw string from MCP tool

        Returns:
            List of validated ResearchOutput objects
        """
        rows = self._parse_mcp_output(mcp_result)
        return self._process_rows(rows)

    def read_from_rows(self, rows: List[List[str]]) -> List[ResearchOutput]:
        """
        Process pre-parsed rows (header + data rows).

        Args:
            rows: 2D list where first row is headers

        Returns:
            List of validated ResearchOutput objects
        """
        return self._process_rows(rows)

    def _parse_mcp_output(self, result: str) -> List[List[str]]:
        """Parse the formatted string output from read_sheet_values."""
        rows = []
        for line in result.strip().split('\n'):
            match = re.search(r"Row\s+\d+:\s*\[(.+)\]", line)
            if match:
                raw = match.group(1)
                cells = [
                    c.strip().strip("'\"")
                    for c in re.split(r"',\s*'|\"?,\s*\"?", raw)
                ]
                rows.append(cells)
        return rows

    def _process_rows(self, rows: List[List[str]]) -> List[ResearchOutput]:
        """Validate and convert rows to ResearchOutput objects."""
        self.outputs = []
        self.validation_log = []
        self._raw_rows = rows

        if not rows:
            self.validation_log.append("ERROR: No rows found in tracker sheet")
            return []

        header = [h.strip().lower() for h in rows[0]]
        col_map = self._map_columns(header)

        for i, row in enumerate(rows[1:], start=2):
            output = self._parse_row(row, col_map, row_num=i)
            if output:
                self.outputs.append(output)

        logger.info(
            "Parsed %d outputs (%d featured, %d listed) with %d warnings",
            len(self.outputs),
            len(self.get_featured()),
            len(self.get_listed()),
            len(self.validation_log),
        )
        return self.outputs

    def _map_columns(self, header: List[str]) -> Dict[str, int]:
        """Map header names to column indices."""
        col_map = {}
        for i, h in enumerate(header):
            if "submitted" in h or "name" in h or "by" in h:
                col_map["submitter"] = i
            elif "priority" in h:
                col_map["priority"] = i
            elif "title" in h and "project" in h:
                col_map["title"] = i
            elif "title" in h:
                col_map.setdefault("title", i)
            elif "description" in h or "brief" in h or "summary" in h or "insight" in h:
                col_map["description"] = i
            elif "link" in h or "output" in h or "url" in h:
                col_map["links"] = i
            elif "end date" in h or "date" in h:
                col_map["end_date"] = i
        return col_map

    def _parse_row(
        self, row: List[str], col_map: Dict[str, int], row_num: int
    ) -> Optional[ResearchOutput]:
        """Parse and validate a single tracker row."""
        warnings: List[str] = []

        def get_cell(key: str, default: str = "") -> str:
            idx = col_map.get(key)
            if idx is not None and idx < len(row):
                return row[idx].strip()
            return default

        title = get_cell("title")
        if not title:
            self.validation_log.append(f"Row {row_num}: Skipped — missing project title")
            return None

        submitter = get_cell("submitter")
        if not submitter:
            self.validation_log.append(f"Row {row_num}: Missing submitter name")
            submitter = "Unknown"

        priority_str = get_cell("priority", "2")
        try:
            priority = int(priority_str)
            if priority not in (1, 2):
                warnings.append(f"Invalid priority '{priority_str}', defaulted to 2")
                priority = 2
        except ValueError:
            warnings.append(f"Non-numeric priority '{priority_str}', defaulted to 2")
            priority = 2

        description = get_cell("description")
        if not description:
            warnings.append("Missing description — placeholder added")
            description = f"Research output: {title}"

        links_raw = get_cell("links")
        output_links = self._parse_links(links_raw, warnings, row_num)

        project_end_date = get_cell("end_date")

        if warnings:
            for w in warnings:
                self.validation_log.append(f"Row {row_num} ({title}): {w}")

        return ResearchOutput(
            submitter=submitter,
            priority=priority,
            title=title,
            description=description,
            output_links=output_links,
            project_end_date=project_end_date,
            validation_warnings=warnings,
        )

    def _parse_links(
        self, raw: str, warnings: List[str], row_num: int
    ) -> List[str]:
        """Parse comma-separated links and validate URL format."""
        if not raw:
            return []
        links = []
        for part in re.split(r'[,\s]+', raw):
            part = part.strip()
            if not part:
                continue
            if re.match(r'https?://', part):
                links.append(part)
            else:
                warnings.append(f"Invalid URL skipped: {part[:50]}")
        return links

    def get_featured(self) -> List[ResearchOutput]:
        """Return priority-1 outputs."""
        return [o for o in self.outputs if o.is_featured]

    def get_listed(self) -> List[ResearchOutput]:
        """Return priority-2 (and other) outputs."""
        return [o for o in self.outputs if not o.is_featured]

    def get_validation_report(self) -> str:
        """Return a human-readable validation report."""
        if not self.validation_log:
            return "All rows passed validation."
        lines = ["Tracker Validation Report", "=" * 40]
        for entry in self.validation_log:
            lines.append(f"  - {entry}")
        lines.append(f"\nTotal: {len(self.outputs)} valid outputs, {len(self.validation_log)} warnings")
        return "\n".join(lines)

    def get_stats(self) -> Dict[str, Any]:
        """Return summary statistics."""
        return {
            "total_outputs": len(self.outputs),
            "featured_count": len(self.get_featured()),
            "listed_count": len(self.get_listed()),
            "validation_warnings": len(self.validation_log),
        }
