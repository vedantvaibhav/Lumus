#!/usr/bin/env python3
"""
Check available Google Gemini models
"""

import os
import google.generativeai as genai

def check_models():
    """Check available models."""
    api_key = "AIzaSyALHcpX6Bfw8-qWgbBpz3bxgF8G8Yg0tvA"
    genai.configure(api_key=api_key)
    
    print("🔍 Checking available Google Gemini models...")
    
    try:
        models = genai.list_models()
        print("Available models:")
        for model in models:
            if 'generateContent' in model.supported_generation_methods:
                print(f"✅ {model.name}")
            else:
                print(f"❌ {model.name} (no generateContent)")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_models()
