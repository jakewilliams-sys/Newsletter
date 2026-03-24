"""
R&I Newsletter Automation Agents (v2 - Tracker-Driven)
"""
from .tracker_reader import TrackerReader, ResearchOutput
from .summarizer import SummarizerAgent
from .html_generator import HTMLNewsletterGenerator
from .pdf_exporter import PDFExporter
from .customer_corner import CustomerCorner, CustomerProfile

# Legacy imports kept for backward compatibility
from .scanner import ScannerAgent

__all__ = [
    "TrackerReader",
    "ResearchOutput",
    "SummarizerAgent",
    "HTMLNewsletterGenerator",
    "PDFExporter",
    "CustomerCorner",
    "CustomerProfile",
    "ScannerAgent",
]
