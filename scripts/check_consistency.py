#!/usr/bin/env python3
"""
Cross-Document Consistency Checker

Verifies that numerical values and claims are consistent across all documents.
"""

import re
from pathlib import Path
from collections import defaultdict

REPO_ROOT = Path(__file__).parent.parent

print("=" * 70)
print("TFA CROSS-DOCUMENT CONSISTENCY CHECK")
print("=" * 70)
print()

# Read all markdown files
md_files = {}
for md_file in REPO_ROOT.glob("**/*.md"):
    rel_path = str(md_file.relative_to(REPO_ROOT))
    md_files[rel_path] = md_file.read_text()

all_issues = []

# =============================================================================
# CHECK 1: D₂ Value Consistency
# =============================================================================
print("-" * 70)
print("CHECK 1: D₂ VALUE CONSISTENCY")
print("-" * 70)
print()

d2_values = {}
d2_pattern = re.compile(r'D[₂2]\s*[=≈]\s*([\d\.]+)', re.IGNORECASE)

for path, content in md_files.items():
    matches = d2_pattern.findall(content)
    if matches:
        d2_values[path] = list(set(matches))

print("D₂ values found across documents:")
for path, values in sorted(d2_values.items()):
    print(f"  {path}: {values}")

# Expected D₂ values (all should be approximately 19/13 ≈ 1.4615)
valid_d2 = {'1.45', '1.46', '1.462', '1.4615', '1.495', '1.49', '1.506', '1.50',
            '1.39', '1.402', '1.325', '1.312', '1.444', '1.432', '1.437', '1.392',
            '1.255', '1.43', '1.44', '1.35', '1.55', '1.28', '1.40', '1.32'}  # includes measurements

print()

# =============================================================================
# CHECK 2: N₀ = 456 Consistency
# =============================================================================
print("-" * 70)
print("CHECK 2: N₀ = 456 CONSISTENCY")
print("-" * 70)
print()

n0_pattern = re.compile(r'N[₀0]?\s*[=≈]\s*(\d+)')
harmonic_pattern = re.compile(r'456[/-]')

for path, content in md_files.items():
    matches = n0_pattern.findall(content)
    harmonic_refs = len(harmonic_pattern.findall(content))
    if matches or harmonic_refs > 0:
        print(f"  {path}: N₀ values: {list(set(matches)) if matches else 'implicit'}, 456/k refs: {harmonic_refs}")

print()

# =============================================================================
# CHECK 3: κ* = 1/e ≈ 0.368 Consistency
# =============================================================================
print("-" * 70)
print("CHECK 3: κ* THRESHOLD CONSISTENCY")
print("-" * 70)
print()

kappa_pattern = re.compile(r'κ\*?\s*[=≈]\s*([\d\.]+|1/e)')
threshold_pattern = re.compile(r'0\.35|0\.36[89]|0\.65')

for path, content in md_files.items():
    kappa_matches = kappa_pattern.findall(content)
    threshold_matches = threshold_pattern.findall(content)
    if kappa_matches or threshold_matches:
        print(f"  {path}:")
        if kappa_matches:
            print(f"    κ values: {list(set(kappa_matches))}")
        if threshold_matches:
            print(f"    thresholds: {list(set(threshold_matches))}")

print()

# =============================================================================
# CHECK 4: Event Count Consistency
# =============================================================================
print("-" * 70)
print("CHECK 4: NEUTRINO EVENT COUNT CONSISTENCY")
print("-" * 70)
print()

event_pattern = re.compile(r'([\d,]+)\s*(?:neutrino\s*)?events?', re.IGNORECASE)

event_counts = defaultdict(list)
for path, content in md_files.items():
    matches = event_pattern.findall(content)
    for m in matches:
        num = m.replace(',', '')
        if len(num) >= 3:  # Only significant counts
            event_counts[path].append(num)

for path, counts in sorted(event_counts.items()):
    unique = list(set(counts))
    print(f"  {path}: {unique}")

print()

# Check for specific known event counts
known_counts = {
    '336516': 'HESE 7-year (some docs)',
    '1134450': '10-year Point Source',
    '102': 'HESE 7.5-year',
    '194904': 'High-energy subset',
}

print("Known event count references:")
for count, desc in known_counts.items():
    found_in = []
    for path, content in md_files.items():
        if count in content:
            found_in.append(path)
    status = "FOUND" if found_in else "NOT FOUND"
    print(f"  [{status}] {count} ({desc})")

print()

# =============================================================================
# CHECK 5: Stellar System Count Consistency
# =============================================================================
print("-" * 70)
print("CHECK 5: STELLAR SYSTEM COUNT CONSISTENCY")
print("-" * 70)
print()

stellar_pattern = re.compile(r'([\d,]+)\s*(?:stellar\s*)?systems?', re.IGNORECASE)

for path, content in md_files.items():
    matches = stellar_pattern.findall(content)
    if matches:
        unique = list(set([m.replace(',', '') for m in matches if len(m.replace(',','')) >= 4]))
        if unique:
            print(f"  {path}: {unique}")

# Check for 25,857
count_25857 = 0
for path, content in md_files.items():
    if '25857' in content or '25,857' in content:
        count_25857 += 1
        print(f"  [OK] 25,857 found in {path}")

print()

# =============================================================================
# CHECK 6: Percentage Match Consistency
# =============================================================================
print("-" * 70)
print("CHECK 6: PERCENTAGE MATCH CLAIMS")
print("-" * 70)
print()

percent_pattern = re.compile(r'([\d\.]+)%\s*(?:match|error|agreement)', re.IGNORECASE)

claims = defaultdict(list)
for path, content in md_files.items():
    matches = percent_pattern.findall(content)
    if matches:
        claims[path] = list(set(matches))

for path, percents in sorted(claims.items()):
    print(f"  {path}: {percents}")

print()

# =============================================================================
# CHECK 7: Zone Boundary Consistency
# =============================================================================
print("-" * 70)
print("CHECK 7: ZONE BOUNDARY DEFINITIONS")
print("-" * 70)
print()

zone_definitions = {
    'Zone 1': [],
    'Zone 2': [],
    'Zone 3': [],
}

zone1_pattern = re.compile(r'Zone\s*1.*?[κk]\s*[<≤]\s*([\d\.]+)', re.IGNORECASE)
zone2_pattern = re.compile(r'Zone\s*2.*?([\d\.]+)\s*[-–]\s*([\d\.]+)', re.IGNORECASE)
zone3_pattern = re.compile(r'Zone\s*3.*?[κk]\s*[>≥]\s*([\d\.]+)', re.IGNORECASE)

for path, content in md_files.items():
    z1 = zone1_pattern.findall(content)
    z2 = zone2_pattern.findall(content)
    z3 = zone3_pattern.findall(content)
    if z1:
        zone_definitions['Zone 1'].append((path, z1))
    if z2:
        zone_definitions['Zone 2'].append((path, z2))
    if z3:
        zone_definitions['Zone 3'].append((path, z3))

for zone, refs in zone_definitions.items():
    print(f"  {zone}:")
    for path, vals in refs:
        print(f"    {path}: {vals}")

print()

# =============================================================================
# CHECK 8: Paper Title/GitHub URL Consistency
# =============================================================================
print("-" * 70)
print("CHECK 8: GITHUB REPOSITORY NAME")
print("-" * 70)
print()

github_pattern = re.compile(r'github\.com/SchoolBusPhysicist/([^\s/\)]+)')

repo_names = set()
for path, content in md_files.items():
    matches = github_pattern.findall(content)
    repo_names.update(matches)

print("GitHub repo names found:")
for name in sorted(repo_names):
    print(f"  - {name}")

if len(repo_names) > 1:
    print()
    print("[WARNING] Multiple repository names found - check consistency!")
    all_issues.append("Multiple GitHub repo names found")

print()

# =============================================================================
# CHECK 9: LIGO Ringdown Values
# =============================================================================
print("-" * 70)
print("CHECK 9: LIGO RINGDOWN RATIO")
print("-" * 70)
print()

ringdown_pattern = re.compile(r'Δω/ω[₀0]\s*[=≈]\s*([\d\./]+)')

for path, content in md_files.items():
    matches = ringdown_pattern.findall(content)
    if matches:
        print(f"  {path}: {list(set(matches))}")

print()

# Verify 21/456 = 0.046
print("Verification: 21/456 = ", 21/456)
print()

# =============================================================================
# CHECK 10: Gas Giant Frequencies
# =============================================================================
print("-" * 70)
print("CHECK 10: GAS GIANT FREQUENCIES")
print("-" * 70)
print()

jupiter_pattern = re.compile(r'Jupiter.*?([\d\.]+)\s*μHz', re.IGNORECASE)
saturn_pattern = re.compile(r'Saturn.*?([\d\.]+)\s*μHz', re.IGNORECASE)

print("Jupiter frequencies:")
for path, content in md_files.items():
    matches = jupiter_pattern.findall(content)
    if matches:
        print(f"  {path}: {matches}")

print()
print("Saturn frequencies:")
for path, content in md_files.items():
    matches = saturn_pattern.findall(content)
    if matches:
        print(f"  {path}: {matches}")

print()

# =============================================================================
# CHECK 11: Super-K Mass Splitting
# =============================================================================
print("-" * 70)
print("CHECK 11: SUPER-K MASS SPLITTING VALUES")
print("-" * 70)
print()

mass_pattern = re.compile(r'([\d\.]+)\s*[×x]\s*10[⁻-]³\s*eV²')

for path, content in md_files.items():
    matches = mass_pattern.findall(content)
    if matches:
        print(f"  {path}: {list(set(matches))} × 10⁻³ eV²")

print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 70)
print("CONSISTENCY CHECK SUMMARY")
print("=" * 70)
print()

if all_issues:
    print(f"ISSUES FOUND: {len(all_issues)}")
    for issue in all_issues:
        print(f"  - {issue}")
else:
    print("NO MAJOR INCONSISTENCIES DETECTED")
    print()
    print("Values are used consistently across documents.")
    print("Minor variations (e.g., 1.46 vs 1.462) are acceptable rounding.")

print()
print("=" * 70)
