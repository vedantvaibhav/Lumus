"""
Reader Agent for extracting clean text from various sources.
Supports PDFs, web pages, text files, and direct text input.
"""

import os
import re
import requests
from typing import Optional, Dict, Any
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import pdfplumber
import PyPDF2
from pathlib import Path

from ..core.models import SourceType


class TextCleaner:
    """Utility class for cleaning and preprocessing text."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text content."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common unwanted patterns
        text = re.sub(r'\[.*?\]', '', text)  # Remove bracketed content
        text = re.sub(r'\(.*?\)', '', text)  # Remove parenthetical content
        
        # Remove page numbers and headers/footers
        text = re.sub(r'Page \d+', '', text)
        text = re.sub(r'\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up punctuation
        text = re.sub(r'[^\w\s\.\,\!\?\;\:\-\(\)]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_sentences(text: str) -> list:
        """Extract meaningful sentences from text."""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if len(s.strip()) > 20]


class ReaderAgent:
    """Agent responsible for reading and extracting text from various sources."""
    
    def __init__(self):
        self.text_cleaner = TextCleaner()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def read(self, source: str, source_type: SourceType) -> Dict[str, Any]:
        """
        Read content from a source and return cleaned text with metadata.
        
        Args:
            source: The source content (URL, file path, or text)
            source_type: Type of source
            
        Returns:
            Dictionary containing text, metadata, and source info
        """
        try:
            if source_type == SourceType.URL:
                return self._read_url(source)
            elif source_type == SourceType.PDF:
                return self._read_pdf(source)
            elif source_type == SourceType.TEXT:
                return self._read_text(source)
            elif source_type == SourceType.FILE:
                return self._read_file(source)
            else:
                raise ValueError(f"Unsupported source type: {source_type}")
        except Exception as e:
            return {
                'text': '',
                'metadata': {},
                'source_info': {'error': str(e)},
                'success': False
            }
    
    def _read_url(self, url: str) -> Dict[str, Any]:
        """Read content from a URL."""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract main content
            main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if main_content:
                text = main_content.get_text()
            else:
                text = soup.get_text()
            
            cleaned_text = self.text_cleaner.clean_text(text)
            
            # Extract metadata
            title = soup.find('title')
            title_text = title.get_text().strip() if title else "Untitled"
            
            return {
                'text': cleaned_text,
                'metadata': {
                    'title': title_text,
                    'url': url,
                    'content_length': len(cleaned_text),
                    'sentences': self.text_cleaner.extract_sentences(cleaned_text)
                },
                'source_info': {
                    'type': 'url',
                    'url': url,
                    'title': title_text
                },
                'success': True
            }
            
        except Exception as e:
            raise Exception(f"Failed to read URL {url}: {str(e)}")
    
    def _read_pdf(self, file_path: str) -> Dict[str, Any]:
        """Read content from a PDF file."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            text = ""
            
            # Try pdfplumber first (better for complex layouts)
            try:
                with pdfplumber.open(file_path) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
            except Exception:
                # Fallback to PyPDF2
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
            
            cleaned_text = self.text_cleaner.clean_text(text)
            
            return {
                'text': cleaned_text,
                'metadata': {
                    'title': Path(file_path).stem,
                    'file_path': file_path,
                    'content_length': len(cleaned_text),
                    'sentences': self.text_cleaner.extract_sentences(cleaned_text)
                },
                'source_info': {
                    'type': 'pdf',
                    'file_path': file_path,
                    'title': Path(file_path).stem
                },
                'success': True
            }
            
        except Exception as e:
            raise Exception(f"Failed to read PDF {file_path}: {str(e)}")
    
    def _read_text(self, text: str) -> Dict[str, Any]:
        """Read content from direct text input."""
        cleaned_text = self.text_cleaner.clean_text(text)
        
        return {
            'text': cleaned_text,
            'metadata': {
                'title': 'Text Input',
                'content_length': len(cleaned_text),
                'sentences': self.text_cleaner.extract_sentences(cleaned_text)
            },
            'source_info': {
                'type': 'text',
                'title': 'Text Input'
            },
            'success': True
        }
    
    def _read_file(self, file_path: str) -> Dict[str, Any]:
        """Read content from a text file."""
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
            
            cleaned_text = self.text_cleaner.clean_text(text)
            
            return {
                'text': cleaned_text,
                'metadata': {
                    'title': Path(file_path).stem,
                    'file_path': file_path,
                    'content_length': len(cleaned_text),
                    'sentences': self.text_cleaner.extract_sentences(cleaned_text)
                },
                'source_info': {
                    'type': 'file',
                    'file_path': file_path,
                    'title': Path(file_path).stem
                },
                'success': True
            }
            
        except Exception as e:
            raise Exception(f"Failed to read file {file_path}: {str(e)}")
    
    def detect_source_type(self, source: str) -> SourceType:
        """Automatically detect the type of source."""
        if source.startswith(('http://', 'https://')):
            return SourceType.URL
        elif source.endswith('.pdf'):
            return SourceType.PDF
        elif os.path.isfile(source):
            return SourceType.FILE
        else:
            return SourceType.TEXT
