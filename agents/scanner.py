"""
Scanner Agent - Scans Google Drive for recent R&I team documents
"""
import json
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

import sys
sys.path.append('..')
from config import (
    GOOGLE_EMAIL,
    INCLUDED_MIME_TYPES,
)

EXCLUSION_PATTERNS = [
    "untitled", "template", "copy of", ".csv", "test", "draft",
    "(responses)", "notes by gemini", "discussion guide", "recruitment",
    "participants", "screener", "brief", "tracker", "user access",
    "call list", "sign-up", "recording",
]

DOCUMENT_CATEGORIES = {
    "Partner Insights": ["partner", "nps", "segmentation", "relationship", "roo voices"],
    "Brand & Consumer": ["brand", "yougov", "tracker", "consumer", "perception", "dinneroo", "immersion"],
    "Voice of Customer": ["voice of", "nps survey", "feedback", "medallia"],
    "Product Research": ["hop", "plus member", "id scanning", "facial recognition", "chopper"],
    "Market Intelligence": ["competitor", "market", "gwi", "retail"],
}


@dataclass
class Document:
    """Represents a Google Drive document."""
    id: str
    name: str
    mime_type: str
    modified_time: str
    link: str
    size: Optional[int] = None
    category: str = "Other"
    summary: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "mime_type": self.mime_type,
            "modified_time": self.modified_time,
            "link": self.link,
            "size": self.size,
            "category": self.category,
            "summary": self.summary,
        }


class ScannerAgent:
    """
    Agent responsible for scanning Google Drive and finding relevant documents.
    
    This agent interfaces with the Google Workspace MCP to search for documents
    modified within a specified date range and categorizes them by research theme.
    """
    
    def __init__(self, mcp_caller=None, days_back: int = 30):
        """
        Initialize the Scanner Agent.
        
        Args:
            mcp_caller: Function to call MCP tools (injected for flexibility)
            days_back: Number of days to look back for documents
        """
        self.mcp_caller = mcp_caller
        self.days_back = days_back
        self.documents: List[Document] = []
        
    def set_mcp_caller(self, mcp_caller):
        """Set the MCP caller function."""
        self.mcp_caller = mcp_caller
        
    async def scan_drive(self) -> List[Document]:
        """
        Scan Google Drive for recent documents.
        
        Returns:
            List of Document objects found in the drive.
        """
        if not self.mcp_caller:
            raise ValueError("MCP caller not set. Use set_mcp_caller() first.")
        
        from datetime import datetime, timedelta
        start = datetime.now() - timedelta(days=self.days_back)
        date_filter = f"modifiedTime > '{start.strftime('%Y-%m-%d')}'"
        
        # Search for documents modified in the date range
        result = await self.mcp_caller(
            server="user-google_workspace_mcp",
            tool_name="search_drive_files",
            arguments={
                "user_google_email": GOOGLE_EMAIL,
                "query": date_filter,
                "page_size": 100,
                "include_items_from_all_drives": True,
                "corpora": "allDrives",
            }
        )
        
        # Parse the result
        self.documents = self._parse_drive_results(result)
        
        # Filter and categorize
        self.documents = self._filter_documents(self.documents)
        self._categorize_documents()
        
        return self.documents
    
    def scan_drive_sync(self, drive_results: str) -> List[Document]:
        """
        Synchronous version that takes pre-fetched drive results.
        
        Args:
            drive_results: Raw string output from search_drive_files MCP call
            
        Returns:
            List of Document objects
        """
        self.documents = self._parse_drive_results(drive_results)
        self.documents = self._filter_documents(self.documents)
        self._categorize_documents()
        return self.documents
    
    def _parse_drive_results(self, results: str) -> List[Document]:
        """Parse the drive search results into Document objects."""
        documents = []
        
        # Parse the formatted string output from MCP
        lines = results.split('\n')
        
        for line in lines:
            if line.startswith('- Name:'):
                doc = self._parse_document_line(line)
                if doc:
                    documents.append(doc)
        
        return documents
    
    def _parse_document_line(self, line: str) -> Optional[Document]:
        """Parse a single document line from MCP output."""
        try:
            # Extract name
            name_match = re.search(r'Name: "([^"]+)"', line)
            if not name_match:
                return None
            name = name_match.group(1)
            
            # Extract ID
            id_match = re.search(r'ID: ([^,\)]+)', line)
            if not id_match:
                return None
            doc_id = id_match.group(1).strip()
            
            # Extract type
            type_match = re.search(r'Type: ([^,\)]+)', line)
            mime_type = type_match.group(1).strip() if type_match else ""
            
            # Extract size
            size_match = re.search(r'Size: (\d+)', line)
            size = int(size_match.group(1)) if size_match else None
            
            # Extract modified time
            modified_match = re.search(r'Modified: ([^,\)]+)', line)
            modified_time = modified_match.group(1).strip() if modified_match else ""
            
            # Extract link
            link_match = re.search(r'Link: ([^\s]+)', line)
            link = link_match.group(1).strip() if link_match else ""
            
            return Document(
                id=doc_id,
                name=name,
                mime_type=mime_type,
                modified_time=modified_time,
                link=link,
                size=size,
            )
        except Exception as e:
            print(f"Error parsing document line: {e}")
            return None
    
    def _filter_documents(self, documents: List[Document]) -> List[Document]:
        """Filter documents based on mime type and exclusion patterns."""
        filtered = []
        
        for doc in documents:
            # Check mime type
            if not any(mime in doc.mime_type for mime in INCLUDED_MIME_TYPES):
                # Skip non-document types (folders, shortcuts, etc.)
                if "folder" in doc.mime_type.lower() or "shortcut" in doc.mime_type.lower():
                    continue
                # Still include if it's a recognized document type
                if "document" not in doc.mime_type.lower() and \
                   "presentation" not in doc.mime_type.lower() and \
                   "spreadsheet" not in doc.mime_type.lower() and \
                   "pdf" not in doc.mime_type.lower():
                    continue
            
            # Check exclusion patterns
            name_lower = doc.name.lower()
            if any(pattern in name_lower for pattern in EXCLUSION_PATTERNS):
                continue
            
            filtered.append(doc)
        
        return filtered
    
    def _categorize_documents(self):
        """Categorize documents based on their names."""
        for doc in self.documents:
            doc.category = self._get_category(doc.name)
    
    def _get_category(self, name: str) -> str:
        """Determine the category for a document based on its name."""
        name_lower = name.lower()
        
        for category, keywords in DOCUMENT_CATEGORIES.items():
            if any(keyword in name_lower for keyword in keywords):
                return category
        
        return "Other Research"
    
    def get_documents_by_category(self) -> Dict[str, List[Document]]:
        """Get documents organized by category."""
        categorized: Dict[str, List[Document]] = {}
        
        for doc in self.documents:
            if doc.category not in categorized:
                categorized[doc.category] = []
            categorized[doc.category].append(doc)
        
        return categorized
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics about the scanned documents."""
        categorized = self.get_documents_by_category()
        
        return {
            "total_documents": len(self.documents),
            "categories": {cat: len(docs) for cat, docs in categorized.items()},
            "date_range_days": self.days_back,
        }
