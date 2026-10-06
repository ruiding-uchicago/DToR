#!/usr/bin/env python3
"""
Enhanced Academic Paper Text Cleaner for Large Datasets with Sliding Window

This script processes a large collection of academic papers (1.13M) from raw text files
to a cleaned JSONL format suitable for model training. It includes batch processing,
parallel processing, comprehensive text cleaning, and sliding window tokenization.

Improvements:
- Preserves section headers and structure
- Preserves mathematical notation and equations
- Preserves tables in standardized format
- Preserves important short lines
- Standardizes citations instead of removing them completely
- Pre-tokenization support for direct use with Axolotl
"""

import os
import re
import json
import logging
import argparse
import time
import multiprocessing
import warnings
import shutil
import tempfile
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from pathlib import Path
from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
from html import unescape
import unicodedata
from transformers import AutoTokenizer
import numpy as np
from tqdm import tqdm

# Suppress XML parsing warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("text_cleaning.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EnhancedAcademicTextCleaner:
    """Enhanced class to clean text from academic papers while preserving valuable content."""
    
    def __init__(self):
        # Common XML/HTML tags to remove
        self.xml_patterns = [
            r'</?[a-z-]+[^>]*>',  # XML/HTML tags
            r'<!\[CDATA\[.*?\]\]>',  # CDATA sections
            r'<!--.*?-->',  # Comments
        ]
        
        # Special characters and entities that should be normalized
        self.special_chars = {
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\u2018': "'",  # left single quotation
            '\u2019': "'",  # right single quotation
            '\u201c': '"',  # left double quotation
            '\u201d': '"',  # right double quotation
            '\xa0': ' ',    # non-breaking space
        }
        
        # Patterns for sections to remove entirely (like references, acknowledgments)
        # Reduced to remove fewer sections
        self.unwanted_sections = [
            r'<ref-list.*?</ref-list>',
            r'<ref id=.*?</ref>',
            r'<mixed-citation.*?</mixed-citation>',
            # Keeping more content by removing fewer sections
            # r'<back>.*?</back>',  # Back matter - no longer removing entirely
            r'<pub-id.*?</pub-id>',
            r'References(\s+)?:.*?(\n\n|\Z)',  # Reference sections in plain text
            r'Bibliography(\s+)?:.*?(\n\n|\Z)',
            # Keeping acknowledgments as they can contain valuable information
            # r'Acknowledgements?(\s+)?.*?(\n\n|\Z)',
            # r'Appendix(\s+)?.*?(\n\n|\Z)',  # Keeping appendices
            # r'Funding(\s+)?.*?(\n\n|\Z)',  # Keeping funding info
            # r'Conflict of interest(\s+)?.*?(\n\n|\Z)',  # Keeping COI statements
            # r'Supplementary Material(\s+)?.*?(\n\n|\Z)',  # Keeping supplementary material info
        ]
        
        # Patterns to identify DOIs, URLs, and similar strings
        self.url_doi_patterns = [
            r'https?://\S+',  # URLs - will be standardized instead of removed
            r'doi:[\w\./-]+',  # DOIs with doi: prefix
            r'10\.\d{4}/[\w\.-]+',  # DOI numbers
        ]
        
        # Patterns for citation markers in text
        self.citation_patterns = [
            r'\(\s*[A-Za-z]+(\s+et\s+al\.)?[, ]+\d{4}[a-z]?\s*\)',  # (Author, 2020)
            r'\[\s*\d+\s*\]',  # [1], [23]
            r'\[\s*[A-Za-z]+(\s+et\s+al\.)?[, ]+\d{4}[a-z]?\s*\]',  # [Author, 2020]
            r'\(\s*see\s+[A-Za-z]+(\s+et\s+al\.)?[, ]+\d{4}[a-z]?\s*\)',  # (see Author, 2020)
        ]
        
        # Patterns for IDs, metadata, and formatting artifacts
        self.metadata_patterns = [
            r'<source>.*?</source>',
            r'<document_content>.*?</document_content>',
            r'<document index=".*?">',
            r'</document>',
            r'<documents>',
            r'</documents>',
            r'id=".*?"',
            r'xml:lang=".*?"',
            r'xlink:href=".*?"',
            r'publication-type=".*?"',
            r'pub-id-type=".*?"',
            r'person-group-type=".*?"',
            r'specific-use=".*?"',
            r'content-type=".*?"',
            r'assigning-authority=".*?"',
            r'mimetype=".*?"',
            r'mime-subtype=".*?"',
        ]
        
        # Regular expressions for common artifacts
        self.artifact_patterns = [
            r'\d+</pub-id>',
            r'\d+<\/elocation-id>',
            r'\d+<\/fpage>',
            r'\d+<\/lpage>',
            r'[A-Z]+\d+<\/volume>',
            r'\d{4}<\/year>',
            r'1:CAS:[\w%]+',  # Chemical Abstract Service identifiers
        ]
        
        # Patterns for line breaks and spacing issues
        self.whitespace_patterns = [
            r'\n{3,}',  # Multiple newlines
            r'\s{2,}',  # Multiple spaces
        ]
        
        # Common section header patterns in scientific papers
        self.section_headers = [
            r'^Abstract(\s+)?',
            r'^Introduction(\s+)?',
            r'^Methods(\s+)?',
            r'^Methodology(\s+)?',
            r'^Results(\s+)?',
            r'^Discussion(\s+)?',
            r'^Conclusion(\s+)?',
            r'^\d+\.[\d\.]*\s+[A-Z]',  # Numbered sections like "1. Introduction" or "2.1 Methods"
        ]
        
        # Patterns for mathematical expressions and equations
        self.equation_patterns = [
            r'\$\$.+?\$\$',  # Display math mode in LaTeX/MathJax
            r'\$.+?\$',  # Inline math mode in LaTeX/MathJax
            r'\\begin\{equation\}.+?\\end\{equation\}',  # LaTeX equation environment
            r'\\begin\{align\}.+?\\end\{align\}',  # LaTeX align environment
            r'\\begin\{eqnarray\}.+?\\end\{eqnarray\}',  # LaTeX eqnarray environment
            r'\\begin\{gathered\}.+?\\end\{gathered\}',  # LaTeX gathered environment
            r'\\begin\{array\}.+?\\end\{array\}',  # LaTeX array environment
        ]
        
        # Table marker to use when standardizing tables
        self.table_marker = "TABLE_START\n{}\nTABLE_END"
        
        # Citation marker for standardized citations
        self.citation_marker = "[CITATION]"

    def remove_xml_tags(self, text):
        """Remove XML/HTML tags from text while preserving structure."""
        # Try with BeautifulSoup first for more reliable parsing
        try:
            # Check if content looks like XML
            if re.search(r'<\?xml|<!DOCTYPE|\<[a-zA-Z0-9]+:[a-zA-Z]', text):
                # Use XML parser
                soup = BeautifulSoup(text, 'lxml-xml')
            else:
                # Use HTML parser
                soup = BeautifulSoup(text, 'lxml')
                
            # Extract all table elements before getting text
            tables = []
            for table in soup.find_all(['table']):
                # Convert table to a text representation
                table_text = self.convert_table_to_text(table)
                tables.append(table_text)
            
            # Get text content
            text = soup.get_text(separator=' ')
            
            # Reinsert extracted tables
            for table_idx, table_text in enumerate(tables):
                table_marker = f"[TABLE_{table_idx}]"
                text += f"\n\n{self.table_marker.format(table_text)}\n\n"
                
        except Exception as e:
            logger.debug(f"BeautifulSoup parsing failed, falling back to regex: {e}")
            # Fall back to regex if BeautifulSoup fails
            for pattern in self.xml_patterns:
                text = re.sub(pattern, ' ', text, flags=re.DOTALL)
                
        return text

    def convert_table_to_text(self, table_element):
        """Convert a BeautifulSoup table element to a standardized text format."""
        try:
            rows = []
            
            # Extract headers
            headers = []
            header_row = table_element.find('thead')
            if header_row:
                for th in header_row.find_all(['th']):
                    headers.append(th.get_text().strip())
            
            if headers:
                rows.append(" | ".join(headers))
                rows.append("-" * len(" | ".join(headers)))
            
            # Extract data rows
            for tr in table_element.find_all('tr'):
                cells = []
                for cell in tr.find_all(['td', 'th']):
                    cell_text = cell.get_text().strip()
                    cells.append(cell_text)
                
                if cells and cells != headers:  # Skip if this is the header row we already processed
                    rows.append(" | ".join(cells))
            
            return "\n".join(rows)
        except Exception as e:
            logger.debug(f"Table conversion error: {e}")
            return "Error converting table"

    def remove_unwanted_sections(self, text):
        """Remove unwanted sections like references, acknowledgments, etc."""
        for pattern in self.unwanted_sections:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE | re.DOTALL)
        return text

    def standardize_urls_and_dois(self, text):
        """Standardize URLs and DOIs instead of removing them."""
        # Replace URLs with a standard marker
        text = re.sub(r'https?://\S+', "[URL]", text)
        
        # Replace DOIs with a standard marker
        text = re.sub(r'doi:[\w\./-]+', "[DOI]", text)
        text = re.sub(r'10\.\d{4}/[\w\.-]+', "[DOI]", text)
        
        return text

    def standardize_citations(self, text):
        """Standardize citation markers rather than removing them."""
        for pattern in self.citation_patterns:
            text = re.sub(pattern, self.citation_marker, text)
        return text

    def remove_metadata(self, text):
        """Remove metadata artifacts."""
        for pattern in self.metadata_patterns:
            text = re.sub(pattern, '', text)
        return text

    def remove_artifacts(self, text):
        """Remove common artifacts."""
        for pattern in self.artifact_patterns:
            text = re.sub(pattern, '', text)
        return text

    def normalize_whitespace(self, text):
        """Normalize whitespace in text."""
        for pattern in self.whitespace_patterns:
            text = re.sub(pattern, '\n\n', text)
        text = text.strip()
        return text

    def normalize_characters(self, text):
        """Normalize special characters."""
        # Unescape HTML entities
        text = unescape(text)
        
        # Replace special unicode characters
        for char, replacement in self.special_chars.items():
            text = text.replace(char, replacement)
        
        # Normalize unicode
        text = unicodedata.normalize('NFKC', text)
        
        return text

    def preserve_short_important_lines(self, text, min_length=4):
        """Preserve short but important lines, only removing truly trivial ones."""
        lines = text.split('\n')
        filtered_lines = []
        
        for line in lines:
            line_stripped = line.strip()
            # Keep lines that are long enough
            if len(line_stripped) >= min_length:
                filtered_lines.append(line)
            # Keep short lines that look like they might be important
            elif re.search(r'[A-Za-z0-9]', line_stripped) and not line_stripped in ['', '-', '*', '=']:
                filtered_lines.append(line)
                
        return '\n'.join(filtered_lines)

    def is_mostly_references(self, text, threshold=0.8):
        """Check if text is mostly references (higher threshold to keep more content)."""
        # Count patterns typical of references
        ref_patterns = [
            r'\(\d{4}\)',  # Publication year
            r'et al\.',    # Author list shorthand
            r'pp\.\s*\d+', # Page numbers
            r'vol\.\s*\d+', # Volume
            r'doi:',       # DOI
        ]
        
        ref_count = 0
        for pattern in ref_patterns:
            ref_count += len(re.findall(pattern, text, re.IGNORECASE))
        
        # Estimate based on frequency of patterns
        text_length = len(text)
        if text_length == 0:
            return True
            
        # Higher threshold to keep more content
        return (ref_count / text_length) > threshold
    
    def enhance_section_formatting(self, text):
        """Enhance formatting of section headers to preserve structure."""
        # Add proper spacing after section headers
        for pattern in self.section_headers:
            text = re.sub(pattern, lambda m: m.group(0) + "\n\n" if not m.group(0).endswith("\n\n") else m.group(0), text)
        
        # Additional patterns for unnumbered section headers
        unnumbered_headers = re.compile(r'^([A-Z][a-z]+(\s+[A-Z]?[a-z]+){0,3})$', re.MULTILINE)
        text = re.sub(unnumbered_headers, r'\1\n', text)
        
        return text
    
    def preserve_equations(self, text):
        """Identify and preserve mathematical notation and equations."""
        # For each equation pattern
        for pattern in self.equation_patterns:
            # Find all matches
            equations = re.finditer(pattern, text, re.DOTALL)
            
            # Replace each equation with a standardized format
            offset = 0
            for i, eq_match in enumerate(equations):
                start, end = eq_match.span()
                start += offset
                end += offset
                
                # Get the original equation
                equation = text[start:end]
                
                # Create a marker with the equation
                eq_marker = f"[EQUATION: {equation}]"
                
                # Replace the equation with the marker
                text = text[:start] + eq_marker + text[end:]
                
                # Update offset for subsequent replacements
                offset += len(eq_marker) - len(equation)
        
        return text
    
    def clean_text(self, text):
        """Apply enhanced cleaning steps to text to preserve valuable content."""
        # Check if input is empty or None
        if not text or not text.strip():
            return ""
        
        # Remove unwanted sections first (references, etc.) - now more selective
        text = self.remove_unwanted_sections(text)
        
        # Preserve equations before removing XML tags
        text = self.preserve_equations(text)
        
        # Remove XML/HTML tags while preserving table structure
        text = self.remove_xml_tags(text)
        
        # Check if what remains is mostly references (with higher threshold)
        if self.is_mostly_references(text):
            return ""
            
        # Apply other cleaning steps
        text = self.normalize_characters(text)
        text = self.standardize_urls_and_dois(text)
        text = self.standardize_citations(text)
        text = self.remove_metadata(text)
        text = self.remove_artifacts(text)
        text = self.preserve_short_important_lines(text)
        text = self.enhance_section_formatting(text)
        text = self.normalize_whitespace(text)
        
        return text


def load_tokenizer(tokenizer_path):
    """Load the tokenizer from the specified path."""
    try:
        # Load the tokenizer with increased max length to avoid truncation warnings
        tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path,
            model_max_length=1000000  # Set a very large value to avoid warnings during processing
        )
        logger.info(f"Successfully loaded tokenizer from {tokenizer_path}")
        return tokenizer
    except Exception as e:
        logger.error(f"Error loading tokenizer: {e}")
        raise


def apply_sliding_window(text, tokenizer, window_size, stride):
    """
    Apply a sliding window approach to the text.
    
    Args:
        text: The text to process
        tokenizer: The tokenizer to use for counting tokens
        window_size: The maximum number of tokens per window
        stride: The number of tokens to slide the window by
    
    Returns:
        List of text windows
    """
    # Use truncation to avoid warnings when encoding very long texts
    tokens = tokenizer.encode(text, truncation=False, add_special_tokens=False)
    
    if len(tokens) <= window_size:
        return [text]
    
    windows = []
    
    # Create sliding windows
    for i in range(0, len(tokens) - stride, stride):
        # Calculate end index
        end_idx = min(i + window_size, len(tokens))
        
        # Extract tokens for this window
        window_tokens = tokens[i:end_idx]
        
        # No minimum size threshold - we want all content
        
        # Convert tokens back to text
        window_text = tokenizer.decode(window_tokens, skip_special_tokens=True)
        
        # Clean up the window text
        window_text = window_text.strip()
        
        # Only add if not empty
        if window_text:
            windows.append(window_text)
    
    # Make sure to include the final window if not already included
    if len(tokens) > 0 and tokens[-1] not in tokens[i:end_idx]:
        final_start = max(0, len(tokens) - window_size)
        final_window = tokenizer.decode(tokens[final_start:], skip_special_tokens=True)
        final_window = final_window.strip()
        if final_window and final_window not in windows:
            windows.append(final_window)
    
    return windows


def identify_section_boundaries(text):
    """
    Identify probable section boundaries in the text.
    Returns a list of indices where sections likely begin.
    """
    section_patterns = [
        r'\n\s*#+\s+[A-Z]',  # Markdown headings
        r'\n\s*[A-Z][a-z]+\s+\d+(\.\d+)*\s*\n',  # Section number format: "Section 1.2"
        r'\n\s*\d+(\.\d+)*\s+[A-Z][a-z]+',  # Number first format: "1.2 Methods"
        r'\n\s*[A-Z][A-Z\s]+\n',  # ALL CAPS section headers
        r'\n\s*[A-Z][a-z]+(\s+[A-z][a-z]+){0,3}:\s*\n'  # Title with colon: "Results:"
    ]
    
    boundaries = [0]  # Text always starts with a boundary
    
    for pattern in section_patterns:
        for match in re.finditer(pattern, text):
            boundaries.append(match.start())
    
    # Sort and deduplicate
    boundaries = sorted(set(boundaries))
    
    return boundaries


def smart_sliding_window(text, tokenizer, window_size, stride):
    """
    Apply a smarter sliding window that tries to respect section boundaries.
    
    Args:
        text: The text to process
        tokenizer: The tokenizer for counting tokens
        window_size: Maximum tokens per window
        stride: Number of tokens to slide by
    
    Returns:
        List of text windows
    """
    # Use truncation=False to avoid warnings for long texts
    tokens = tokenizer.encode(text, truncation=False, add_special_tokens=False)
    
    if len(tokens) <= window_size:
        return [text]
    
    # Try to identify section boundaries
    section_boundaries = identify_section_boundaries(text)
    
    # If we couldn't identify sections, fall back to regular sliding window
    if len(section_boundaries) <= 1:
        return apply_sliding_window(text, tokenizer, window_size, stride)
    
    windows = []
    current_text = ""
    current_tokens = []
    
    # Process the text section by section
    for i in range(len(section_boundaries)):
        start_idx = section_boundaries[i]
        end_idx = section_boundaries[i+1] if i+1 < len(section_boundaries) else len(text)
        
        section_text = text[start_idx:end_idx]
        section_tokens = tokenizer.encode(section_text, truncation=False, add_special_tokens=False)
        
        # If adding this section would exceed window_size
        if len(current_tokens) + len(section_tokens) > window_size:
            # If we have accumulated some text, save it as a window
            if current_text:
                windows.append(current_text)
                
            # If this single section is too large, use sliding window on it
            if len(section_tokens) > window_size:
                section_windows = apply_sliding_window(section_text, tokenizer, window_size, stride)
                windows.extend(section_windows)
                current_text = ""
                current_tokens = []
            else:
                # Start a new window with this section
                current_text = section_text
                current_tokens = section_tokens
        else:
            # Add this section to the current window
            current_text += section_text
            current_tokens.extend(section_tokens)
    
    # Don't forget the last window
    if current_text:
        windows.append(current_text)
    
    return windows


def pretokenize_window(text, tokenizer):
    """
    Pre-tokenize a window of text for Axolotl format.
    
    Args:
        text: Text window to tokenize
        tokenizer: HuggingFace tokenizer to use
    
    Returns:
        Dict with keys: input_ids, attention_mask, and labels
    """
    # Encode the text with BOS/EOS tokens
    tokenized = tokenizer(text, add_special_tokens=True, truncation=False)
    
    # Create the input_ids, attention_mask, and labels
    input_ids = tokenized['input_ids']
    attention_mask = tokenized['attention_mask']
    
    # For pretraining, labels are the same as input_ids
    # (no masking needed as we want to train on all tokens)
    labels = input_ids.copy()
    
    return {
        "input_ids": input_ids,
        "attention_mask": attention_mask,
        "labels": labels
    }


def sanitize_for_json(text):
    """
    Clean and sanitize text to ensure it's valid for JSON encoding.
    Enhanced to handle equation markers and table structures.
    """
    if not text:
        return ""
    
    # Handle control characters that can break JSON
    for i in range(32):
        if i not in [9, 10, 13]:  # tab, newline, carriage return are ok
            text = text.replace(chr(i), "")
    
    # Handle unicode surrogate pairs that can cause JSON encoding issues
    text = ''.join(c for c in text if not (0xD800 <= ord(c) <= 0xDFFF))
    
    # Replace other potentially problematic characters
    replacements = {
        '\\': '\\\\',  # Backslash
        '\b': '',      # Backspace
        '\f': '',      # Form feed
        # Don't replace quotes or we'll break the equation markers
        # '"': '\\"',    # Double quote
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Now escape quotes that aren't part of equation markers or table structures
    # This is a simplistic approach; a more robust solution would use proper parsing
    safe_text = ""
    i = 0
    while i < len(text):
        # Check if we're at the start of an equation marker
        if i+9 < len(text) and text[i:i+9] == "[EQUATION":
            # Find the end of the equation marker
            end_idx = text.find("]", i)
            if end_idx != -1:
                # Add the entire marker without escaping internal quotes
                safe_text += text[i:end_idx+1]
                i = end_idx + 1
                continue
                
        # Check if we're at the start of a table marker
        elif i+11 < len(text) and text[i:i+11] == "TABLE_START":
            # Find the end of the table marker
            end_idx = text.find("TABLE_END", i)
            if end_idx != -1:
                # Add the entire table without escaping internal quotes
                safe_text += text[i:end_idx+9]  # +9 to include "TABLE_END"
                i = end_idx + 9
                continue
                
        # Regular character - escape quotes if needed
        if text[i] == '"':
            safe_text += '\\"'
        else:
            safe_text += text[i]
        i += 1
    
    return safe_text


def process_file(file_path, cleaner, tokenizer=None, window_size=None, stride=None, use_smart_window=False, pretokenize=False):
    """
    Process a single file and return the cleaned text.
    
    Args:
        file_path: Path to the file to process
        cleaner: Instance of the EnhancedAcademicTextCleaner
        tokenizer: Optional tokenizer for sliding window
        window_size: Size of the sliding window in tokens
        stride: Stride for sliding window
        use_smart_window: Whether to use section-aware sliding window
        pretokenize: Whether to pre-tokenize the output for Axolotl
    
    Returns:
        List of cleaned text windows and any error message
    """
    try:
        # Try UTF-8 first
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        try:
            # Fall back to latin-1
            with open(file_path, 'r', encoding='latin-1') as f:
                content = f.read()
        except Exception as e:
            return None, f"Error reading {file_path}: {e}"

    # Clean the text
    cleaned_text = cleaner.clean_text(content)
    
    # Skip empty results
    if not cleaned_text.strip():
        return None, f"Cleaning resulted in empty text: {file_path}"
    
    # If no sliding window is requested, return the whole text
    if tokenizer is None or window_size is None:
        if pretokenize and tokenizer:
            # Pre-tokenize the full text
            tokenized = pretokenize_window(cleaned_text, tokenizer)
            return [tokenized], None
        else:
            return [sanitize_for_json(cleaned_text)], None
    
    # Apply sliding window
    if use_smart_window:
        windows = smart_sliding_window(cleaned_text, tokenizer, window_size, stride)
    else:
        windows = apply_sliding_window(cleaned_text, tokenizer, window_size, stride)
    
    if pretokenize:
        # Pre-tokenize each window
        tokenized_windows = [pretokenize_window(window, tokenizer) for window in windows]
        return tokenized_windows, None
    else:
        # Just sanitize the text windows
        sanitized_windows = [sanitize_for_json(window) for window in windows]
        return sanitized_windows, None


def process_batch(file_paths, batch_output_file, cleaner, batch_id, tokenizer=None, window_size=None, stride=None, use_smart_window=False, pretokenize=False):
    """
    Process a batch of files and write results to a batch-specific output file.
    
    Args:
        file_paths: List of file paths to process
        batch_output_file: Path to output JSONL file for this batch
        cleaner: Instance of EnhancedAcademicTextCleaner
        batch_id: ID of this batch
        tokenizer: Optional tokenizer for sliding window
        window_size: Size of the sliding window in tokens
        stride: Stride for sliding window
        use_smart_window: Whether to use section-aware sliding window
        pretokenize: Whether to pre-tokenize the output for Axolotl
    """
    batch_start_time = time.time()
    results = []
    processed_files = 0
    processed_windows = 0
    skipped = 0
    
    for file_path in file_paths:
        # Process file and get the windows
        windows, error = process_file(
            file_path, 
            cleaner, 
            tokenizer=tokenizer, 
            window_size=window_size, 
            stride=stride,
            use_smart_window=use_smart_window,
            pretokenize=pretokenize
        )
        
        if windows:
            for window in windows:
                if pretokenize or (isinstance(window, str) and window.strip()):  # Only add non-empty windows
                    if pretokenize:
                        results.append(window)  # Window is already a dict with input_ids, etc.
                    else:
                        results.append({"text": window})
            
            processed_files += 1
            processed_windows += len(windows)
        else:
            skipped += 1
    
    # Write results to the batch-specific output file
    with open(batch_output_file, 'w', encoding='utf-8') as outfile:
        for result in results:
            try:
                # Verify the JSON is valid before writing
                json_str = json.dumps(result, ensure_ascii=False)
                # Test parse it to make sure it's valid
                json.loads(json_str)
                outfile.write(json_str + '\n')
            except Exception as e:
                logger.warning(f"Skipped invalid JSON entry in batch {batch_id}: {str(e)[:100]}")
    
    batch_end_time = time.time()
    batch_duration = batch_end_time - batch_start_time
    
    return {
        'batch_id': batch_id,
        'processed_files': processed_files,
        'processed_windows': processed_windows,
        'skipped': skipped,
        'duration': batch_duration,
        'batch_file': batch_output_file
    }


def combine_batch_files(batch_results, output_path):
    """
    Safely combine all batch files into a single output file.
    
    Args:
        batch_results: List of batch processing results
        output_path: Path to the final output file
    """
    logger.info(f"Combining batch files into {output_path}")
    
    with open(output_path, 'w', encoding='utf-8') as outfile:
        for result in sorted(batch_results, key=lambda x: x['batch_id']):
            batch_file = result['batch_file']
            if os.path.exists(batch_file):
                try:
                    with open(batch_file, 'r', encoding='utf-8') as infile:
                        # Read and validate each line before writing
                        for line_num, line in enumerate(infile, 1):
                            try:
                                # Verify it's valid JSON
                                json.loads(line.strip())
                                outfile.write(line)
                            except json.JSONDecodeError as e:
                                logger.warning(f"Skipped invalid JSON in {batch_file}, line {line_num}: {str(e)[:100]}")
                except Exception as e:
                    logger.error(f"Error processing batch file {batch_file}: {e}")
                
                # Remove the batch file after successful processing
                os.unlink(batch_file)
    
    logger.info(f"Combined file created at {output_path}")


def parallel_process_directory(
    input_dir, 
    output_dir, 
    output_file, 
    batch_size=1000, 
    num_workers=None,
    tokenizer_path=None,
    window_size=None,
    stride=None,
    use_smart_window=False,
    test_mode=False,
    pretokenize=False
):
    """
    Process a directory of files in parallel batches.
    
    Args:
        input_dir: Directory containing input files
        output_dir: Directory to save output
        output_file: Path to the output JSONL file
        batch_size: Number of files to process in each batch
        num_workers: Number of parallel workers (defaults to CPU count)
        tokenizer_path: Path to the tokenizer
        window_size: Size of the sliding window in tokens
        stride: Stride for sliding window
        use_smart_window: Whether to use section-aware sliding window
        test_mode: Whether to run in test mode (process only 100 files)
        pretokenize: Whether to pre-tokenize the output for Axolotl
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Create temp directory for batch files
    temp_dir = os.path.join(output_dir, f"temp_batches_{int(time.time())}")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Determine number of workers
    if num_workers is None:
        num_workers = max(1, multiprocessing.cpu_count() - 1)  # Leave one CPU free for system processes
    
    # Create a shared cleaner instance
    cleaner = EnhancedAcademicTextCleaner()
    
    # Load tokenizer if sliding window is requested or pre-tokenization
    tokenizer = None
    if tokenizer_path and (window_size or pretokenize):
        tokenizer = load_tokenizer(tokenizer_path)
        if window_size:
            logger.info(f"Using sliding window with window size {window_size} and stride {stride}")
            if use_smart_window:
                logger.info("Using smart section-aware sliding window")
        if pretokenize:
            logger.info("Pre-tokenizing output for direct use with Axolotl")
    
    # Find all paragraph files
    all_files = []
    root_dir = Path(input_dir)
    
    logger.info(f"Scanning directory for files...")
    for subfolder in root_dir.iterdir():
        if subfolder.is_dir():
            paragraph_file = subfolder / 'paragraphs_whole.txt'
            if paragraph_file.exists():
                all_files.append(paragraph_file)
    
    total_files = len(all_files)
    logger.info(f"Found {total_files} files to process")
    
    # Add this block to limit files in test mode
    if test_mode:
        all_files = all_files[:100]  # Process only 100 files
        logger.info(f"Test mode: Limited to processing only {len(all_files)} files")
    
    # Split files into batches
    batches = []
    for i in range(0, len(all_files), batch_size):
        batches.append(all_files[i:i + batch_size])
    
    logger.info(f"Processing {len(batches)} batches with {num_workers} workers")
    
    # Process batches in parallel
    start_time = time.time()
    batch_results = []
    
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = []
        for batch_id, batch in enumerate(batches):
            # Create a unique batch output file
            batch_output_file = os.path.join(temp_dir, f"batch_{batch_id}.jsonl")
            
            future = executor.submit(
                process_batch, 
                batch, 
                batch_output_file,
                cleaner, 
                batch_id,
                tokenizer,
                window_size,
                stride,
                use_smart_window,
                pretokenize
            )
            futures.append(future)
        
        # Track progress
        completed_batches = 0
        total_processed_files = 0
        total_processed_windows = 0
        total_skipped = 0
        
        for future in tqdm(futures, desc="Processing batches", unit="batch"):
            try:
                result = future.result()
                batch_results.append(result)
                
                completed_batches += 1
                total_processed_files += result['processed_files']
                total_processed_windows += result['processed_windows']
                total_skipped += result['skipped']
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
    
    # Combine batch files into final output
    output_path = os.path.join(output_dir, output_file)
    try:
        combine_batch_files(batch_results, output_path)
        
        # Delete temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        logger.error(f"Error combining batch files: {e}")
        logger.info(f"Batch files remain in {temp_dir} for manual recovery")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    logger.info(f"Processing complete!")
    logger.info(f"Total files processed: {total_processed_files}")
    logger.info(f"Total windows created: {total_processed_windows}")
    logger.info(f"Total files skipped: {total_skipped}")
    logger.info(f"Total time: {total_time/60:.1f} minutes")
    logger.info(f"Output saved to: {output_path}")
    
    if pretokenize:
        logger.info(f"Data was pre-tokenized for direct use with Axolotl (empty 'type:' field)")


if __name__ == "__main__":
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Enhanced academic paper text processing with content preservation.')
    parser.add_argument('--input-dir', type=str, default='./succeed_DOI_full_text',
                        help='Directory containing the input text files')
    parser.add_argument('--output-dir', type=str, default='formatted_data',
                        help='Directory to save the output JSONL file')
    parser.add_argument('--output-file', type=str, default='text_clean_1.13M_raw.jsonl',
                        help='Filename for the output JSONL file')
    parser.add_argument('--batch-size', type=int, default=5000,
                        help='Number of files to process in each batch')
    parser.add_argument('--workers', type=int, default=None,
                        help='Number of parallel workers')
    parser.add_argument('--test-mode', action='store_true',
                        help='Run in test mode with just 100 files')
    parser.add_argument('--tokenizer-path', type=str, default=None,
                        help='Path to the tokenizer (required for sliding window)')
    parser.add_argument('--window-size', type=int, default=8192,
                        help='Size of the sliding window in tokens (default: 8192)')
    parser.add_argument('--stride', type=int, default=4096,
                        help='Stride for sliding window (tokens to overlap) (default: 4096)')
    parser.add_argument('--smart-window', action='store_true',
                        help='Use section-aware smart sliding window')
    parser.add_argument('--max-workers', type=int, default=None,
                        help='Maximum number of parallel workers (defaults to CPU count - 1)')
    parser.add_argument('--quiet', action='store_true',
                        help='Suppress warnings and non-critical messages')
    parser.add_argument('--validate-json', action='store_true',
                        help='Validate JSON entries before adding them to output')
    parser.add_argument('--pretokenize', action='store_true',
                        help='Pre-tokenize output for direct use with Axolotl (requires tokenizer-path)')
    
    args = parser.parse_args()
    
    # Set window parameters
    window_size = args.window_size
    stride = args.stride
    
    # Configure logging based on quiet flag
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
        # Also suppress transformers warnings
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
    
    # Require tokenizer path if sliding window is enabled or pre-tokenization
    if (window_size and not args.tokenizer_path) or (args.pretokenize and not args.tokenizer_path):
        parser.error("--tokenizer-path is required when using sliding window or pre-tokenization")
    
    # Generate appropriate filename if using sliding window or pre-tokenization
    if window_size and stride:
        # Extract base filename without extension
        base_name = os.path.splitext(args.output_file)[0]
        args.output_file = f"{base_name}_win{window_size}_stride{stride}"
        if args.pretokenize:
            args.output_file += "_pretokenized"
        args.output_file += ".jsonl"
        logger.info(f"Using sliding window with size {window_size} and stride {stride}")
        if args.pretokenize:
            logger.info(f"Pre-tokenizing output for direct use with Axolotl")
        logger.info(f"Output file set to: {args.output_file}")
    
    if args.test_mode:
        logger.info("Running in TEST MODE with small batch")
        args.batch_size = 100
        args.output_file = f"test_clean_output"
        if window_size:
            args.output_file += f"_win{window_size}_stride{stride}"
        if args.pretokenize:
            args.output_file += "_pretokenized"
        args.output_file += ".jsonl"
    
    try:
        parallel_process_directory(
            args.input_dir,
            args.output_dir,
            args.output_file,
            batch_size=args.batch_size,
            num_workers=args.max_workers if args.max_workers else args.workers,
            tokenizer_path=args.tokenizer_path,
            window_size=args.window_size,
            stride=args.stride,
            use_smart_window=args.smart_window,
            test_mode=args.test_mode,
            pretokenize=args.pretokenize
        )
    except KeyboardInterrupt:
        logger.warning("\nProcessing interrupted by user. Partial results may have been saved.")
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        raise
