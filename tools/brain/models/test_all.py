#!/usr/bin/env python3
"""Run every wrapper's smoke test. Usage: python3 test_all.py"""
import importlib
import traceback

MODULES = ["pollinations", "groq_provider", "mistral_provider",
           "ai_horde", "local_voice"]

results = {}
for name in MODULES:
    print(f"\n{'=' * 20} {name} {'=' * 20}")
    try:
        mod = importlib.import_module(name)
        mod.main()
        results[name] = "PASS"
    except Exception:
        traceback.print_exc()
        results[name] = "FAIL"

print("\n" + "=" * 50)
for name, status in results.items():
    print(f"{name:20s} {status}")
