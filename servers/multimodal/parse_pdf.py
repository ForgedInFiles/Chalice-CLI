"""
Extract text, metadata, and structure from PDF files

This tool is part of the multimodal MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def parse_pdf(
    pdf_path: str,
    pages: str = "all",
    extract_images: bool = False,
    extract_tables: bool = False
) -> Dict[str, Any]:
    """
    Extract text, metadata, and structure from PDF files

    Parameters:
        pdf_path: Path to the PDF file
        pages: Page range (e.g., '1-5', 'all')
        extract_images: Extract embedded images
        extract_tables: Extract tables

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {k: v for k, v in locals().items() if v is not None and k != 'kwargs'}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="multimodal",
        tool_name="parse_pdf",
        **params
    )
