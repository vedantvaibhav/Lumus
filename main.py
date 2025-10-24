#!/usr/bin/env python3
"""
Main entry point for the Self-Quiz Generator Agent.
"""

import sys
import os

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.cli import cli

if __name__ == '__main__':
    cli()
