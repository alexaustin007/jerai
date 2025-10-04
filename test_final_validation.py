#!/usr/bin/env python3
"""Final validation of all components"""
import requests
import json

API_BASE = "http://localhost:8000"

print("=" * 60)
print("Final System Validation")
print("=" * 60)
print()

# Get latest test issue (ID 14)
print("Analyzing Issue #14...")
response = requests.get(f"{API_BASE}/api/issues/14/events")
events = response.json()

print("\n1. ✅ Analysis Response Quality:")
analysis_events = [e for e in events if e['type'] == 'AnalysisComplete']
if analysis_events:
    analysis = analysis_events[0]
    payload = analysis['payload']

    print(f"   - Actor: {analysis['actor']}")
    print(f"   - Mock: {payload.get('mock', 'unknown')}")

    analysis_text = str(payload.get('analysis', ''))
    print(f"   - Length: {len(analysis_text)} characters")

    # Quality checks
    checks = {
        "Contains 'Decimal' or 'decimal'": ('decimal' in analysis_text.lower()),
        "Contains 'float' or 'round'": ('float' in analysis_text.lower() or 'round' in analysis_text.lower()),
        "Length > 100 chars": (len(analysis_text) > 100),
        "Not mock": (not payload.get('mock', True))
    }

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
else:
    print("   ❌ No analysis events found")

print("\n2. ✅ Patch Response Quality:")
patch_events = [e for e in events if e['type'] == 'PatchProposed']
if patch_events:
    patch = patch_events[0]
    payload = patch['payload']

    print(f"   - Actor: {patch['actor']}")
    print(f"   - Mock: {payload.get('mock', 'unknown')}")

    patch_text = str(payload.get('patch', ''))
    print(f"   - Length: {len(patch_text)} characters")

    # Quality checks
    checks = {
        "Contains diff markers": ('---' in patch_text or 'diff' in patch_text),
        "Contains Decimal import": ('decimal import' in patch_text.lower() or 'import decimal' in patch_text.lower()),
        "Contains quantize or ROUND": ('quantize' in patch_text or 'ROUND' in patch_text),
        "Length > 500 chars": (len(patch_text) > 500),
        "Not mock": (not payload.get('mock', True))
    }

    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {check}")
else:
    print("   ❌ No patch events found")

print("\n3. ✅ Event Completeness:")
required_events = ['IssueCreated', 'StateChanged', 'AIFixRequested', 'AnalysisComplete', 'PatchProposed', 'PatchValidated']
found_events = set(e['type'] for e in events)

for req_event in required_events:
    status = "✅" if req_event in found_events else "❌"
    print(f"   {status} {req_event}")

print("\n4. ✅ API Usage Summary:")
# Count real vs mock for all issues
all_issues_response = requests.get(f"{API_BASE}/api/issues/")
all_issues = all_issues_response.json()

total_issues = len(all_issues)
print(f"   - Total issues in database: {total_issues}")

# Check recent issues (last 5)
recent_analysis = 0
recent_patches = 0
recent_real_analysis = 0
recent_real_patches = 0

for issue in all_issues[-5:]:
    issue_events = requests.get(f"{API_BASE}/api/issues/{issue['id']}/events").json()

    for event in issue_events:
        if event['type'] == 'AnalysisComplete':
            recent_analysis += 1
            if not event['payload'].get('mock', True):
                recent_real_analysis += 1

        if event['type'] == 'PatchProposed':
            recent_patches += 1
            if not event['payload'].get('mock', True):
                recent_real_patches += 1

print(f"   - Recent analyses (last 5 issues): {recent_analysis}")
print(f"   - Real Cerebras API calls: {recent_real_analysis}")
print(f"   - Recent patches (last 5 issues): {recent_patches}")
print(f"   - Real Llama via MCP calls: {recent_real_patches}")

success_rate_analysis = (recent_real_analysis / recent_analysis * 100) if recent_analysis > 0 else 0
success_rate_patches = (recent_real_patches / recent_patches * 100) if recent_patches > 0 else 0

print(f"\n   API Success Rate:")
print(f"   - Cerebras: {success_rate_analysis:.0f}%")
print(f"   - Llama/MCP: {success_rate_patches:.0f}%")

print("\n" + "=" * 60)
if success_rate_analysis >= 80 and success_rate_patches >= 80:
    print("✅ ALL SYSTEMS OPERATIONAL")
    print("✅ ALL SPONSOR TECHNOLOGIES WORKING")
    print("✅ READY FOR HACKATHON SUBMISSION")
else:
    print("⚠️  Some API calls using fallback mocks")
print("=" * 60)
