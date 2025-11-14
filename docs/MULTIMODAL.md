# Multi-Modal Input Guide

Chalice v3.0 includes comprehensive multi-modal input capabilities, allowing you to work with images, PDFs, documents, diagrams, and more.

## Overview

The multi-modal server provides 5 powerful tools for processing various input types:

1. **Image Analysis** - Analyze images using vision-enabled AI models
2. **PDF Parsing** - Extract text, metadata, and tables from PDF documents
3. **Document Summarization** - Generate intelligent summaries of text documents
4. **Diagram Interpretation** - Analyze diagrams, charts, and visual data
5. **Code from Screenshots** - Extract code from screenshots

## Installation

Multi-modal features require additional dependencies:

```bash
# For PDF parsing
pip install PyPDF2 pdfplumber

# For OCR (optional, for code extraction)
pip install pytesseract Pillow

# For HTTP requests (marketplace)
pip install requests
```

## Image Analysis

Analyze images using GPT-4 Vision or Claude 3 with vision capabilities.

### Usage

```python
from servers.multimodal import analyze_image

# Analyze an image
result = analyze_image(
    image_path="screenshot.png",
    prompt="What does this UI look like? Describe the layout and components.",
    model="gpt-4-vision",
    detail_level="high"
)

if result['success']:
    print(f"Image: {result['image_path']}")
    print(f"Format: {result['image_format']}")
    print(f"Size: {result['size_bytes']} bytes")
    # The image_base64 field contains the encoded image for vision models
```

### Supported Models

- `gpt-4-vision` - GPT-4 with vision capabilities
- `claude-3-opus` - Claude 3 Opus with vision
- `claude-3-sonnet` - Claude 3 Sonnet with vision

### Use Cases

- **UI/UX Analysis**: Analyze interface screenshots
- **Object Detection**: Identify objects in images
- **Scene Understanding**: Describe what's happening in an image
- **Text Extraction**: Extract text from images (OCR)
- **Image Description**: Generate alt text for accessibility

### Example: Analyze a UI Screenshot

```python
result = analyze_image(
    image_path="dashboard.png",
    prompt="""
    Analyze this dashboard UI:
    1. What components are present?
    2. What is the information hierarchy?
    3. Are there any UX issues?
    4. What improvements would you suggest?
    """,
    detail_level="high"
)
```

## PDF Parsing

Extract text, metadata, and structured data from PDF documents.

### Usage

```python
from servers.multimodal import parse_pdf

# Parse entire PDF
result = parse_pdf(
    pdf_path="document.pdf",
    pages="all",
    extract_tables=True
)

if result['success']:
    print(f"Total pages: {result['total_pages']}")
    print(f"Pages extracted: {result['pages_extracted']}")
    print(f"Total characters: {result['total_characters']}")

    # Access metadata
    metadata = result['metadata']
    print(f"Title: {metadata.get('title', 'N/A')}")
    print(f"Author: {metadata.get('author', 'N/A')}")

    # Access extracted text
    for page in result['content']:
        print(f"Page {page['page']}: {page['text'][:100]}...")
```

### Parameters

- `pdf_path`: Path to PDF file (required)
- `pages`: Page range (e.g., "1-5", "all") (default: "all")
- `extract_images`: Extract embedded images (default: False)
- `extract_tables`: Extract tables (default: False)

### Use Cases

- **Document Analysis**: Extract content from reports, papers, books
- **Data Extraction**: Get tables and structured data from PDFs
- **Metadata Extraction**: Get document information
- **Text Conversion**: Convert PDFs to plain text
- **Research**: Process academic papers and technical documents

### Example: Extract Tables from Financial Report

```python
result = parse_pdf(
    pdf_path="annual_report.pdf",
    pages="10-15",  # Financial statements section
    extract_tables=True
)

if 'tables_found' in result:
    print(f"Found {result['tables_found']} tables")
    for page in result['content']:
        if 'tables' in page:
            print(f"Page {page['page']} tables: {page['tables']}")
```

## Document Summarization

Generate intelligent summaries of long text documents.

### Usage

```python
from servers.multimodal import summarize_document

# Summarize document
result = summarize_document(
    content="Your long document text here...",
    max_length=200,
    style="paragraph"
)

if result['success']:
    print(f"Original: {result['original_length']} words")
    print(f"Summary: {result['summary']}")
    print(f"Compression: {result['compression_ratio']}")
```

### Parameters

- `content`: Document text to summarize (required)
- `max_length`: Maximum summary length in words (default: 200)
- `style`: Summary style (default: "paragraph")
  - `paragraph`: Concise paragraph summary
  - `bullet_points`: Key points in bullets
  - `executive`: Executive summary format

### Use Cases

- **Long Document Summarization**: Condense reports, articles, papers
- **Key Points Extraction**: Get main ideas from text
- **Executive Summaries**: Create business summaries
- **Content Curation**: Summarize articles for newsletters
- **Research**: Quickly understand long documents

### Example: Summarize Research Paper

```python
# First, extract PDF
pdf_result = parse_pdf(pdf_path="research_paper.pdf")

# Combine all pages
full_text = ' '.join([page['text'] for page in pdf_result['content']])

# Summarize
summary = summarize_document(
    content=full_text,
    max_length=300,
    style="executive"
)

print(summary['summary'])
```

## Diagram Interpretation

Analyze and interpret diagrams, charts, flowcharts, and visual data.

### Usage

```python
from servers.multimodal import interpret_diagram

# Interpret diagram
result = interpret_diagram(
    image_path="architecture_diagram.png",
    diagram_type="architecture",
    extract_text=True
)

if result['success']:
    print(f"Diagram type: {result['diagram_type']}")
    print(f"Analysis prompt: {result['analysis_prompt']}")
    # The image_base64 contains the diagram for vision model analysis
```

### Supported Diagram Types

- `flowchart`: Process flowcharts
- `uml`: UML diagrams (class, sequence, etc.)
- `erd`: Entity-relationship diagrams
- `chart`: Charts and graphs (bar, line, pie)
- `architecture`: System architecture diagrams
- `auto`: Auto-detect diagram type

### Use Cases

- **Architecture Review**: Analyze system design diagrams
- **Process Understanding**: Interpret flowcharts and workflows
- **Data Visualization**: Understand charts and graphs
- **UML Analysis**: Parse UML diagrams
- **Database Schema**: Interpret ERD diagrams

### Example: Analyze Architecture Diagram

```python
result = interpret_diagram(
    image_path="microservices_architecture.png",
    diagram_type="architecture",
    extract_text=True
)

# Use result with vision model to get detailed analysis
# The vision model will receive the diagram and analysis_prompt
```

## Code from Screenshots

Extract code from screenshots using OCR and vision models.

### Usage

```python
from servers.multimodal import extract_code_from_screenshot

# Extract code
result = extract_code_from_screenshot(
    image_path="code_screenshot.png",
    language="python",
    clean_format=True
)

if result['success']:
    if result.get('ocr_available'):
        # OCR was used
        print(f"Extracted code:\n{result['extracted_text']}")
    else:
        # Prepared for vision model
        print(f"Use vision model with: {result['analysis_prompt']}")
```

### Parameters

- `image_path`: Path to screenshot (required)
- `language`: Programming language (default: "auto")
- `clean_format`: Clean and format extracted code (default: True)

### Supported Languages

- Python, JavaScript, TypeScript, Java, C++, C#, Go, Rust, Ruby, PHP, Swift, Kotlin, and more
- Use `"auto"` for automatic language detection

### Use Cases

- **Code Migration**: Extract code from old screenshots
- **Tutorial Processing**: Get code from educational screenshots
- **Documentation**: Extract code examples from images
- **Code Review**: Copy code from screen shares
- **Legacy Systems**: Extract code from system screenshots

### Example: Extract Python Code

```python
result = extract_code_from_screenshot(
    image_path="python_function.png",
    language="python",
    clean_format=True
)

if result['ocr_available']:
    code = result['extracted_text']
    # Clean up and format the code
    print(code)
else:
    # Use vision model for better accuracy
    # Pass result['image_base64'] and result['analysis_prompt'] to vision model
    pass
```

## Combining Multi-Modal Tools

You can combine multiple tools for powerful workflows:

### Example: Analyze Technical Documentation

```python
from servers.multimodal import parse_pdf, analyze_image, summarize_document

# 1. Extract PDF content
pdf_result = parse_pdf(
    pdf_path="technical_guide.pdf",
    extract_images=True
)

# 2. Summarize each section
summaries = []
for page in pdf_result['content']:
    summary = summarize_document(
        content=page['text'],
        max_length=100,
        style="bullet_points"
    )
    summaries.append(summary['summary'])

# 3. Analyze embedded diagrams
# (In a real workflow, you'd extract and save the images first)
diagrams = []
for image_path in extracted_diagram_paths:
    diagram = interpret_diagram(
        image_path=image_path,
        diagram_type="auto"
    )
    diagrams.append(diagram)

# 4. Combine into comprehensive analysis
print("Document Summary:")
for i, summary in enumerate(summaries):
    print(f"\nSection {i+1}:\n{summary}")

print("\nDiagrams Found:")
for diagram in diagrams:
    print(f"- {diagram['diagram_type']}: {diagram['analysis_prompt']}")
```

## Best Practices

### Image Analysis

1. **Use High Resolution**: Higher resolution images provide better analysis
2. **Choose Right Model**: GPT-4 Vision for general use, Claude 3 for detailed analysis
3. **Be Specific**: Provide clear, specific prompts
4. **Set Detail Level**: Use "high" for complex images, "low" for simple ones

### PDF Parsing

1. **Page Ranges**: Extract only needed pages for better performance
2. **Check Library**: Both PyPDF2 and pdfplumber supported, pdfplumber has more features
3. **Handle Errors**: Some PDFs may be encrypted or corrupted
4. **Extract Tables**: Use pdfplumber for table extraction

### Document Summarization

1. **Chunk Long Documents**: Break very long documents into sections
2. **Choose Style**: Use appropriate style for your use case
3. **Adjust Length**: Balance between brevity and completeness
4. **Combine with PDF**: Great for summarizing extracted PDF content

### Diagram Interpretation

1. **Specify Type**: Specify diagram type when known for better prompts
2. **High Quality**: Use clear, high-resolution diagram images
3. **Extract Text**: Enable text extraction for hybrid diagrams
4. **Use Vision Models**: Best results with GPT-4 Vision or Claude 3

### Code Extraction

1. **Install OCR**: Install pytesseract for offline extraction
2. **Clean Screenshots**: Use clear, high-contrast screenshots
3. **Specify Language**: Helps with syntax preservation
4. **Vision Models**: Use for best accuracy and formatting

## Error Handling

All tools return a consistent error format:

```python
result = analyze_image(image_path="invalid.png", prompt="Analyze")

if not result['success']:
    print(f"Error: {result['error']}")
else:
    # Process successful result
    pass
```

## Performance Tips

1. **Cache Results**: Cache processed images and PDFs to avoid re-processing
2. **Batch Processing**: Process multiple items in parallel when possible
3. **Optimize Images**: Resize large images before analysis
4. **Page Limits**: Only extract needed PDF pages
5. **Use Appropriate Tools**: Choose the right tool for the job

## Security Considerations

1. **Validate Inputs**: Always validate file paths and types
2. **Sanitize Output**: Clean extracted text before use
3. **Check File Sizes**: Limit file sizes to prevent DoS
4. **Hash Verification**: Verify file integrity when downloading
5. **Sandbox Execution**: All processing happens in controlled environments

## Future Enhancements

Coming in future releases:

- Audio transcription and analysis
- Video frame extraction and analysis
- 3D model interpretation
- Mathematical equation extraction
- Handwriting recognition
- Multi-language OCR
- Advanced table structure detection
- Semantic document understanding

---

For more examples, see `examples/multimodal_usage.py`
