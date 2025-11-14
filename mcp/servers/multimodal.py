"""
MCP Server for Multi-Modal Input Processing
Handles images, PDFs, documents, diagrams, and more
"""
import base64
import io
import json
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from mcp.client import MCPServer, MCPTool


class ImageAnalysisTool(MCPTool):
    """Analyze images using vision-enabled AI models"""

    def __init__(self):
        super().__init__(
            "analyze_image",
            "Analyze images using GPT-4 Vision or Claude 3 Opus with vision capabilities"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to the image file"
                },
                "prompt": {
                    "type": "string",
                    "description": "Analysis prompt or question about the image"
                },
                "model": {
                    "type": "string",
                    "description": "Vision model to use (gpt-4-vision, claude-3-opus, claude-3-sonnet)",
                    "default": "gpt-4-vision"
                },
                "detail_level": {
                    "type": "string",
                    "description": "Level of detail (low, medium, high)",
                    "default": "high"
                }
            },
            "required": ["image_path", "prompt"]
        }

    def execute(
        self,
        image_path: str,
        prompt: str,
        model: str = "gpt-4-vision",
        detail_level: str = "high"
    ) -> Dict[str, Any]:
        """
        Analyze an image using vision-enabled AI models

        Supports:
        - Object detection and recognition
        - Text extraction (OCR)
        - Scene understanding
        - Image description
        - Question answering about images
        """
        try:
            # Validate image path
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}"
                }

            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            # Determine image format
            ext = Path(image_path).suffix.lower()
            mime_types = {
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(ext, 'image/jpeg')

            # Encode to base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            return {
                "success": True,
                "image_path": image_path,
                "image_format": mime_type,
                "image_base64": image_base64,
                "prompt": prompt,
                "model": model,
                "detail_level": detail_level,
                "size_bytes": len(image_data),
                "message": "Image encoded successfully. Ready for vision model analysis.",
                "note": "This tool prepares the image. The actual vision model inference happens in the AI provider."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class PDFParseTool(MCPTool):
    """Extract text and metadata from PDF documents"""

    def __init__(self):
        super().__init__(
            "parse_pdf",
            "Extract text, metadata, and structure from PDF files"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "pdf_path": {
                    "type": "string",
                    "description": "Path to the PDF file"
                },
                "pages": {
                    "type": "string",
                    "description": "Page range (e.g., '1-5', 'all')",
                    "default": "all"
                },
                "extract_images": {
                    "type": "boolean",
                    "description": "Extract embedded images",
                    "default": False
                },
                "extract_tables": {
                    "type": "boolean",
                    "description": "Extract tables",
                    "default": False
                }
            },
            "required": ["pdf_path"]
        }

    def execute(
        self,
        pdf_path: str,
        pages: str = "all",
        extract_images: bool = False,
        extract_tables: bool = False
    ) -> Dict[str, Any]:
        """
        Parse PDF documents and extract content

        Features:
        - Text extraction by page
        - Metadata extraction
        - Table detection and extraction
        - Image extraction
        - Document structure analysis
        """
        try:
            # Validate PDF path
            if not os.path.exists(pdf_path):
                return {
                    "success": False,
                    "error": f"PDF file not found: {pdf_path}"
                }

            # Check if PyPDF2 or pdfplumber is available
            try:
                import PyPDF2
                pdf_library = "PyPDF2"
            except ImportError:
                try:
                    import pdfplumber
                    pdf_library = "pdfplumber"
                except ImportError:
                    return {
                        "success": False,
                        "error": "No PDF library found. Install PyPDF2 or pdfplumber: pip install PyPDF2 pdfplumber",
                        "install_command": "pip install PyPDF2 pdfplumber"
                    }

            # Extract using PyPDF2
            if pdf_library == "PyPDF2":
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)

                    # Extract metadata
                    metadata = pdf_reader.metadata or {}

                    # Determine pages to extract
                    total_pages = len(pdf_reader.pages)
                    if pages == "all":
                        page_range = range(total_pages)
                    else:
                        # Parse page range (e.g., "1-5")
                        if '-' in pages:
                            start, end = pages.split('-')
                            page_range = range(int(start) - 1, min(int(end), total_pages))
                        else:
                            page_range = [int(pages) - 1]

                    # Extract text from pages
                    extracted_text = []
                    for page_num in page_range:
                        page = pdf_reader.pages[page_num]
                        text = page.extract_text()
                        extracted_text.append({
                            "page": page_num + 1,
                            "text": text,
                            "char_count": len(text)
                        })

                    return {
                        "success": True,
                        "pdf_path": pdf_path,
                        "library": pdf_library,
                        "total_pages": total_pages,
                        "pages_extracted": len(extracted_text),
                        "metadata": {
                            "title": metadata.get('/Title', 'N/A'),
                            "author": metadata.get('/Author', 'N/A'),
                            "subject": metadata.get('/Subject', 'N/A'),
                            "creator": metadata.get('/Creator', 'N/A'),
                            "producer": metadata.get('/Producer', 'N/A'),
                            "creation_date": metadata.get('/CreationDate', 'N/A')
                        },
                        "content": extracted_text,
                        "total_characters": sum(p['char_count'] for p in extracted_text)
                    }

            # Extract using pdfplumber (more advanced features)
            elif pdf_library == "pdfplumber":
                import pdfplumber

                with pdfplumber.open(pdf_path) as pdf:
                    total_pages = len(pdf.pages)

                    # Determine pages to extract
                    if pages == "all":
                        page_range = range(total_pages)
                    else:
                        if '-' in pages:
                            start, end = pages.split('-')
                            page_range = range(int(start) - 1, min(int(end), total_pages))
                        else:
                            page_range = [int(pages) - 1]

                    # Extract content
                    extracted_content = []
                    tables_extracted = []

                    for page_num in page_range:
                        page = pdf.pages[page_num]

                        page_data = {
                            "page": page_num + 1,
                            "text": page.extract_text() or "",
                            "char_count": len(page.extract_text() or "")
                        }

                        # Extract tables if requested
                        if extract_tables:
                            tables = page.extract_tables()
                            if tables:
                                page_data["tables"] = tables
                                tables_extracted.extend(tables)

                        extracted_content.append(page_data)

                    result = {
                        "success": True,
                        "pdf_path": pdf_path,
                        "library": pdf_library,
                        "total_pages": total_pages,
                        "pages_extracted": len(extracted_content),
                        "metadata": pdf.metadata or {},
                        "content": extracted_content,
                        "total_characters": sum(p['char_count'] for p in extracted_content)
                    }

                    if extract_tables and tables_extracted:
                        result["tables_found"] = len(tables_extracted)

                    return result

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "pdf_path": pdf_path
            }


class DocumentSummarizeTool(MCPTool):
    """Generate summaries of documents"""

    def __init__(self):
        super().__init__(
            "summarize_document",
            "Generate intelligent summaries of text documents"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Document content to summarize"
                },
                "max_length": {
                    "type": "integer",
                    "description": "Maximum summary length in words",
                    "default": 200
                },
                "style": {
                    "type": "string",
                    "description": "Summary style (bullet_points, paragraph, executive)",
                    "default": "paragraph"
                }
            },
            "required": ["content"]
        }

    def execute(
        self,
        content: str,
        max_length: int = 200,
        style: str = "paragraph"
    ) -> Dict[str, Any]:
        """
        Summarize document content

        Styles:
        - bullet_points: Key points in bullets
        - paragraph: Concise paragraph summary
        - executive: Executive summary format
        """
        try:
            # Basic statistics
            words = content.split()
            sentences = content.split('.')

            # Simple extractive summarization (first N sentences)
            # In production, this would use a proper summarization model
            summary_sentences = min(5, len(sentences))
            basic_summary = '. '.join(sentences[:summary_sentences]).strip()

            return {
                "success": True,
                "original_length": len(words),
                "original_sentences": len(sentences),
                "summary_style": style,
                "summary": basic_summary,
                "compression_ratio": f"{len(basic_summary.split()) / len(words) * 100:.1f}%",
                "note": "This is a basic extractive summary. For AI-powered summarization, the content should be sent to the language model."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class DiagramInterpreterTool(MCPTool):
    """Interpret diagrams, charts, and visual data"""

    def __init__(self):
        super().__init__(
            "interpret_diagram",
            "Analyze and interpret diagrams, charts, flowcharts, and visual data"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to diagram image"
                },
                "diagram_type": {
                    "type": "string",
                    "description": "Type of diagram (flowchart, uml, erd, chart, architecture)",
                    "default": "auto"
                },
                "extract_text": {
                    "type": "boolean",
                    "description": "Extract text from diagram",
                    "default": True
                }
            },
            "required": ["image_path"]
        }

    def execute(
        self,
        image_path: str,
        diagram_type: str = "auto",
        extract_text: bool = True
    ) -> Dict[str, Any]:
        """
        Interpret technical diagrams and charts

        Supports:
        - Flowcharts
        - UML diagrams
        - Entity-relationship diagrams
        - Architecture diagrams
        - Charts and graphs
        """
        try:
            # Validate image
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Diagram file not found: {image_path}"
                }

            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Prepare for vision model analysis
            return {
                "success": True,
                "image_path": image_path,
                "diagram_type": diagram_type,
                "image_base64": image_base64,
                "size_bytes": len(image_data),
                "extract_text": extract_text,
                "message": "Diagram prepared for vision model analysis",
                "analysis_prompt": f"Analyze this {diagram_type} diagram and describe its structure, components, and relationships.",
                "note": "The actual diagram interpretation requires a vision-enabled AI model."
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class CodeFromScreenshotTool(MCPTool):
    """Extract code from screenshots"""

    def __init__(self):
        super().__init__(
            "extract_code_from_screenshot",
            "Extract and format code from screenshot images"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "image_path": {
                    "type": "string",
                    "description": "Path to screenshot containing code"
                },
                "language": {
                    "type": "string",
                    "description": "Programming language (auto-detect if not specified)",
                    "default": "auto"
                },
                "clean_format": {
                    "type": "boolean",
                    "description": "Clean and format extracted code",
                    "default": True
                }
            },
            "required": ["image_path"]
        }

    def execute(
        self,
        image_path: str,
        language: str = "auto",
        clean_format: bool = True
    ) -> Dict[str, Any]:
        """
        Extract code from screenshots using OCR and vision models

        Features:
        - Code detection and extraction
        - Language auto-detection
        - Syntax preservation
        - Formatting cleanup
        """
        try:
            # Validate image
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Screenshot file not found: {image_path}"
                }

            # Read and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()

            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # Check for pytesseract (OCR)
            ocr_available = False
            try:
                import pytesseract
                from PIL import Image
                ocr_available = True

                # Attempt basic OCR
                img = Image.open(image_path)
                extracted_text = pytesseract.image_to_string(img)

                return {
                    "success": True,
                    "image_path": image_path,
                    "language": language,
                    "ocr_available": True,
                    "extracted_text": extracted_text,
                    "clean_format": clean_format,
                    "image_base64": image_base64,
                    "message": "Code extracted using OCR. For better results, use vision-enabled AI model.",
                    "note": "OCR may not preserve formatting. Vision models provide better code extraction."
                }
            except ImportError:
                # Return prepared data for vision model
                return {
                    "success": True,
                    "image_path": image_path,
                    "language": language,
                    "ocr_available": False,
                    "image_base64": image_base64,
                    "clean_format": clean_format,
                    "message": "Image prepared for vision model code extraction",
                    "analysis_prompt": f"Extract the {language} code from this screenshot, preserving syntax and formatting.",
                    "install_ocr": "pip install pytesseract Pillow",
                    "note": "For best results, use GPT-4 Vision or Claude 3 with vision capabilities."
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class MultiModalServer(MCPServer):
    """MCP Server for Multi-Modal Input Processing"""

    def __init__(self):
        super().__init__(
            "multimodal",
            "Multi-modal input processing including images, PDFs, documents, and diagrams"
        )

        # Register tools
        self.register_tool(ImageAnalysisTool())
        self.register_tool(PDFParseTool())
        self.register_tool(DocumentSummarizeTool())
        self.register_tool(DiagramInterpreterTool())
        self.register_tool(CodeFromScreenshotTool())


def get_multimodal_server() -> MultiModalServer:
    """Get the multi-modal MCP server instance"""
    return MultiModalServer()
