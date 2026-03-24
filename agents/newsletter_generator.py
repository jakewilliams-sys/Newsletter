"""
Newsletter Generator Agent - Compiles summaries into a formatted newsletter
"""
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

import sys
sys.path.append('..')
from config import (
    GOOGLE_EMAIL,
    NEWSLETTER_TITLE_FORMAT,
    MAX_DOCUMENTS_PER_CATEGORY,
    OUTPUT_FOLDER_ID,
)
from .scanner import Document


class NewsletterGenerator:
    """
    Agent responsible for generating the formatted newsletter.
    
    Takes categorized and summarized documents and creates a polished
    newsletter document that can be shared with stakeholders.
    """
    
    def __init__(self, mcp_caller=None):
        """
        Initialize the Newsletter Generator.
        
        Args:
            mcp_caller: Function to call MCP tools
        """
        self.mcp_caller = mcp_caller
        self.template_path = Path(__file__).parent.parent / "templates" / "newsletter_template.md"
    
    def set_mcp_caller(self, mcp_caller):
        """Set the MCP caller function."""
        self.mcp_caller = mcp_caller
    
    def generate_newsletter(
        self, 
        documents_by_category: Dict[str, List[Document]],
        month: Optional[str] = None,
        year: Optional[int] = None,
    ) -> str:
        """
        Generate the newsletter content.
        
        Args:
            documents_by_category: Documents organized by category
            month: Month name for the newsletter title
            year: Year for the newsletter title
            
        Returns:
            Formatted newsletter content as string
        """
        if month is None:
            month = datetime.now().strftime("%B")
        if year is None:
            year = datetime.now().year
        
        # Generate title
        title = NEWSLETTER_TITLE_FORMAT.format(month=month, year=year)
        
        # Generate sections
        sections = self._generate_sections(documents_by_category)
        
        # Load and fill template
        newsletter = self._load_template()
        newsletter = newsletter.replace("{month}", month)
        newsletter = newsletter.replace("{year}", str(year))
        newsletter = newsletter.replace("{sections}", sections)
        
        return newsletter
    
    def _load_template(self) -> str:
        """Load the newsletter template."""
        try:
            with open(self.template_path, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Fallback template
            return """# R&I Monthly Newsletter - {month} {year}

## What We've Been Working On

{sections}

---

*This newsletter was automatically generated from R&I team outputs.*
"""
    
    def _generate_sections(self, documents_by_category: Dict[str, List[Document]]) -> str:
        """Generate the document sections of the newsletter."""
        sections = []
        
        # Define category order
        category_order = [
            "Student Research",
            "Partner Insights",
            "Brand & Consumer",
            "Voice of Customer",
            "Product Research",
            "Market Intelligence",
            "Other Research",
        ]
        
        # Add categories in order
        for category in category_order:
            if category in documents_by_category and documents_by_category[category]:
                section = self._generate_category_section(
                    category, 
                    documents_by_category[category]
                )
                sections.append(section)
        
        # Add any remaining categories not in the order list
        for category, docs in documents_by_category.items():
            if category not in category_order and docs:
                section = self._generate_category_section(category, docs)
                sections.append(section)
        
        return "\n\n".join(sections)
    
    def _generate_category_section(
        self, 
        category: str, 
        documents: List[Document]
    ) -> str:
        """Generate a section for a single category."""
        # Limit documents per category
        docs_to_show = documents[:MAX_DOCUMENTS_PER_CATEGORY]
        
        # Sort by modified time (most recent first)
        docs_to_show = sorted(
            docs_to_show, 
            key=lambda d: d.modified_time, 
            reverse=True
        )
        
        lines = [f"### {category}"]
        lines.append("")
        
        for doc in docs_to_show:
            # Format the document entry
            summary = doc.summary or "Research output - see document for details."
            
            # Clean up the summary
            summary = summary.strip()
            if not summary.endswith('.'):
                summary += '.'
            
            lines.append(f"**{doc.name}**")
            lines.append(f"{summary}")
            lines.append(f"[View Document]({doc.link})")
            lines.append("")
        
        # Add note if there are more documents
        if len(documents) > MAX_DOCUMENTS_PER_CATEGORY:
            remaining = len(documents) - MAX_DOCUMENTS_PER_CATEGORY
            lines.append(f"*...and {remaining} more document(s) in this category.*")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_plain_text(
        self, 
        documents_by_category: Dict[str, List[Document]],
        month: Optional[str] = None,
        year: Optional[int] = None,
    ) -> str:
        """
        Generate a plain text version of the newsletter.
        
        Args:
            documents_by_category: Documents organized by category
            month: Month name
            year: Year
            
        Returns:
            Plain text newsletter content
        """
        if month is None:
            month = datetime.now().strftime("%B")
        if year is None:
            year = datetime.now().year
        
        lines = []
        lines.append(f"R&I MONTHLY NEWSLETTER - {month.upper()} {year}")
        lines.append("=" * 50)
        lines.append("")
        lines.append("WHAT WE'VE BEEN WORKING ON")
        lines.append("-" * 30)
        lines.append("")
        
        # Define category order
        category_order = [
            "Student Research",
            "Partner Insights", 
            "Brand & Consumer",
            "Voice of Customer",
            "Product Research",
            "Market Intelligence",
            "Other Research",
        ]
        
        for category in category_order:
            if category in documents_by_category and documents_by_category[category]:
                lines.append(f"{category.upper()}")
                lines.append("")
                
                docs = documents_by_category[category][:MAX_DOCUMENTS_PER_CATEGORY]
                docs = sorted(docs, key=lambda d: d.modified_time, reverse=True)
                
                for doc in docs:
                    summary = doc.summary or "See document for details."
                    lines.append(f"  • {doc.name}")
                    lines.append(f"    {summary}")
                    lines.append(f"    → {doc.link}")
                    lines.append("")
                
                lines.append("")
        
        lines.append("-" * 50)
        lines.append("This newsletter was automatically generated.")
        lines.append("Contact the R&I team for questions or feedback.")
        
        return "\n".join(lines)
    
    async def create_google_doc(
        self, 
        content: str, 
        title: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create a Google Doc with the newsletter content.
        
        Args:
            content: Newsletter content
            title: Document title
            
        Returns:
            Dictionary with document ID and link
        """
        if not self.mcp_caller:
            raise ValueError("MCP caller not set. Use set_mcp_caller() first.")
        
        if title is None:
            month = datetime.now().strftime("%B")
            year = datetime.now().year
            title = NEWSLETTER_TITLE_FORMAT.format(month=month, year=year)
        
        try:
            result = await self.mcp_caller(
                server="user-google_workspace_mcp",
                tool_name="create_doc",
                arguments={
                    "user_google_email": GOOGLE_EMAIL,
                    "title": title,
                    "content": content,
                }
            )
            
            return {
                "success": True,
                "result": result,
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def create_google_doc_sync(self, content: str, title: str) -> Dict[str, Any]:
        """
        Prepare the Google Doc creation request (for sync use).
        
        Args:
            content: Newsletter content
            title: Document title
            
        Returns:
            Dictionary with MCP call parameters
        """
        return {
            "server": "user-google_workspace_mcp",
            "tool_name": "create_doc",
            "arguments": {
                "user_google_email": GOOGLE_EMAIL,
                "title": title,
                "content": content,
            }
        }
    
    def get_newsletter_stats(
        self, 
        documents_by_category: Dict[str, List[Document]]
    ) -> Dict[str, Any]:
        """
        Get statistics about the newsletter content.
        
        Args:
            documents_by_category: Documents organized by category
            
        Returns:
            Dictionary with newsletter statistics
        """
        total_docs = sum(len(docs) for docs in documents_by_category.values())
        categories_with_content = len([c for c, d in documents_by_category.items() if d])
        
        return {
            "total_documents": total_docs,
            "categories_with_content": categories_with_content,
            "documents_per_category": {
                cat: len(docs) for cat, docs in documents_by_category.items()
            },
        }
