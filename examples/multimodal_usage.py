"""
Chalice Multi-Modal Input Examples
Demonstrates image analysis, PDF parsing, document summarization, diagram interpretation, and code extraction
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# Example 1: Image Analysis
def example_image_analysis():
    """Analyze images using vision-enabled AI models"""
    from servers.multimodal import analyze_image

    print("=== Image Analysis ===\n")

    # Example image analysis
    result = analyze_image(
        image_path="example_ui.png",
        prompt="Describe the UI components and layout of this dashboard.",
        model="gpt-4-vision",
        detail_level="high"
    )

    if result['success']:
        print(f"✓ Image analyzed: {result['image_path']}")
        print(f"  Format: {result['image_format']}")
        print(f"  Size: {result['size_bytes']:,} bytes")
        print(f"  Model: {result['model']}")
        print(f"  Detail: {result['detail_level']}")
        print(f"  Prompt: {result['prompt']}")
        print("\nThe image is now ready for vision model analysis.")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")


# Example 2: PDF Parsing
def example_pdf_parsing():
    """Extract text and metadata from PDF documents"""
    from servers.multimodal import parse_pdf

    print("\n=== PDF Parsing ===\n")

    # Parse PDF
    result = parse_pdf(
        pdf_path="sample_document.pdf",
        pages="1-3",
        extract_tables=True
    )

    if result['success']:
        print(f"✓ PDF parsed: {result['pdf_path']}")
        print(f"  Library: {result['library']}")
        print(f"  Total pages: {result['total_pages']}")
        print(f"  Pages extracted: {result['pages_extracted']}")
        print(f"  Total characters: {result['total_characters']:,}")

        # Show metadata
        print("\nMetadata:")
        metadata = result.get('metadata', {})
        for key, value in metadata.items():
            if value and value != 'N/A':
                print(f"  {key}: {value}")

        # Show first page excerpt
        if result['content']:
            first_page = result['content'][0]
            print(f"\nFirst page excerpt:")
            print(f"  {first_page['text'][:200]}...")

        # Show tables if found
        if 'tables_found' in result:
            print(f"\n✓ Found {result['tables_found']} tables")
    else:
        print(f"✗ Error: {result.get('error', 'Unknown error')}")
        if 'install_command' in result:
            print(f"  Install: {result['install_command']}")


# Example 3: Document Summarization
def example_document_summarization():
    """Generate summaries of text documents"""
    from servers.multimodal import summarize_document

    print("\n=== Document Summarization ===\n")

    # Sample document
    sample_text = """
    Artificial Intelligence (AI) has revolutionized numerous industries over the past decade.
    From healthcare to finance, AI technologies are being deployed to solve complex problems
    and improve efficiency. Machine learning, a subset of AI, enables systems to learn from
    data without being explicitly programmed. Deep learning, using neural networks with
    multiple layers, has achieved remarkable results in image recognition, natural language
    processing, and game playing. However, AI also raises important ethical considerations
    around privacy, bias, and the future of work. As AI continues to advance, it's crucial
    that we develop these technologies responsibly and ensure they benefit humanity as a whole.
    """

    # Summarize with different styles
    for style in ["paragraph", "bullet_points", "executive"]:
        result = summarize_document(
            content=sample_text,
            max_length=50,
            style=style
        )

        if result['success']:
            print(f"✓ {style.replace('_', ' ').title()} Summary:")
            print(f"  Original: {result['original_length']} words")
            print(f"  Compression: {result['compression_ratio']}")
            print(f"  Summary: {result['summary'][:100]}...")
            print()


# Example 4: Diagram Interpretation
def example_diagram_interpretation():
    """Analyze diagrams and charts"""
    from servers.multimodal import interpret_diagram

    print("=== Diagram Interpretation ===\n")

    diagram_types = ["flowchart", "architecture", "uml", "erd"]

    for diagram_type in diagram_types:
        result = interpret_diagram(
            image_path=f"example_{diagram_type}.png",
            diagram_type=diagram_type,
            extract_text=True
        )

        if result['success']:
            print(f"✓ {diagram_type.upper()} Diagram:")
            print(f"  Path: {result['image_path']}")
            print(f"  Size: {result['size_bytes']:,} bytes")
            print(f"  Analysis prompt: {result['analysis_prompt'][:80]}...")
            print()
        else:
            print(f"✗ {diagram_type}: {result.get('error', 'File not found')}")
            print()


# Example 5: Code from Screenshots
def example_code_extraction():
    """Extract code from screenshots"""
    from servers.multimodal import extract_code_from_screenshot

    print("=== Code Extraction ===\n")

    languages = ["python", "javascript", "java", "auto"]

    for language in languages:
        result = extract_code_from_screenshot(
            image_path="code_example.png",
            language=language,
            clean_format=True
        )

        if result['success']:
            print(f"✓ {language.capitalize()} Code Extraction:")
            print(f"  OCR available: {result['ocr_available']}")

            if result.get('ocr_available'):
                print(f"  Extracted: {result['extracted_text'][:100]}...")
            else:
                print(f"  Analysis prompt: {result['analysis_prompt'][:80]}...")
                print(f"  Install OCR: {result.get('install_ocr', 'N/A')}")
            print()
        else:
            print(f"✗ {language}: {result.get('error', 'Unknown error')}")
            print()


# Example 6: Combined Workflow - PDF to Summary
def example_pdf_to_summary():
    """Complete workflow: Parse PDF and generate summary"""
    from servers.multimodal import parse_pdf, summarize_document

    print("=== PDF to Summary Workflow ===\n")

    # Step 1: Parse PDF
    print("Step 1: Parsing PDF...")
    pdf_result = parse_pdf(pdf_path="sample_document.pdf", pages="all")

    if not pdf_result['success']:
        print(f"✗ PDF parsing failed: {pdf_result.get('error')}")
        return

    print(f"✓ Extracted {pdf_result['pages_extracted']} pages")

    # Step 2: Combine all pages
    print("\nStep 2: Combining content...")
    all_text = ' '.join([page['text'] for page in pdf_result['content']])
    print(f"✓ Combined {len(all_text)} characters")

    # Step 3: Summarize
    print("\nStep 3: Generating summary...")
    summary_result = summarize_document(
        content=all_text,
        max_length=200,
        style="executive"
    )

    if summary_result['success']:
        print(f"✓ Summary generated:")
        print(f"  Compression: {summary_result['compression_ratio']}")
        print(f"\nSummary:\n{summary_result['summary']}")
    else:
        print(f"✗ Summarization failed: {summary_result.get('error')}")


# Example 7: Image Analysis with Vision Model Integration
def example_vision_model_workflow():
    """How to integrate with vision models"""
    from servers.multimodal import analyze_image
    import base64

    print("=== Vision Model Integration ===\n")

    # Prepare image for vision model
    result = analyze_image(
        image_path="screenshot.png",
        prompt="Analyze this UI screenshot and suggest improvements.",
        model="gpt-4-vision"
    )

    if result['success']:
        print("✓ Image prepared for vision model")
        print(f"  Image path: {result['image_path']}")
        print(f"  Format: {result['image_format']}")
        print(f"  Prompt: {result['prompt']}")

        # In a real implementation, you would send this to the vision model:
        # image_data = result['image_base64']
        # response = vision_model.analyze(image_data, result['prompt'])

        print("\nTo use with a vision model:")
        print("  1. Get image_base64 from result")
        print("  2. Send to vision model API with prompt")
        print("  3. Process model's response")
        print(f"\nImage ready for {result['model']}")


# Example 8: Error Handling
def example_error_handling():
    """Proper error handling with multi-modal tools"""
    from servers.multimodal import parse_pdf, analyze_image

    print("\n=== Error Handling ===\n")

    # Try to parse non-existent PDF
    print("1. Handling missing file:")
    result = parse_pdf(pdf_path="nonexistent.pdf")
    if not result['success']:
        print(f"   ✗ Expected error: {result['error']}")

    # Try to analyze invalid image
    print("\n2. Handling invalid image:")
    result = analyze_image(image_path="nonexistent.png", prompt="Test")
    if not result['success']:
        print(f"   ✗ Expected error: {result['error']}")

    # Try without required dependencies
    print("\n3. Handling missing dependencies:")
    result = parse_pdf(pdf_path="test.pdf")
    if not result['success'] and 'install_command' in result:
        print(f"   ✗ Missing dependency: {result['error']}")
        print(f"   ℹ Install with: {result['install_command']}")

    print("\n✓ Error handling demonstrated")


def main():
    """Run all examples"""
    print("Chalice Multi-Modal Input Examples")
    print("=" * 60)

    try:
        example_image_analysis()
        example_pdf_parsing()
        example_document_summarization()
        example_diagram_interpretation()
        example_code_extraction()
        example_pdf_to_summary()
        example_vision_model_workflow()
        example_error_handling()

        print("\n" + "=" * 60)
        print("✓ All examples completed!")
        print("\nNote: Many examples expect files that may not exist.")
        print("      Create sample files or update paths to test fully.")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
