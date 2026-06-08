import os

# Set before any ai_debate module is imported so Settings() succeeds without a real .env
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-test-key-for-testing-only")
