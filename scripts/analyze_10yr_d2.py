#!/usr/bin/env python3
"""
TFA D2 Analysis of IceCube 10-Year Point Source Data
======================================================

Data: 1.13 million neutrino events (2008-2018)
Source: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/VKL316

TFA Prediction: D2 = 1.45 +/- 0.10 for high-R particles (neutrinos)

Author: Jason King / TFA Framework
Date: December 2025
"""

import numpy as np
import pandas as pd
from scipy.spatial.distance import pdist
import glob
import os

# TFA Prediction
TFA_PREDICTED_D2 = 1.45
TFA_PREDICTED_ERROR = 0.10

def load_all_events(events_dir='events'):
    """Load all events from all seasons."""
    all_events = []

    for csv_file in sorted(glob.glob(os.path.join(events_dir, '*.csv'))):
        season = os.path.basename(csv_file).replace('_exp.csv', '').replace('_exp-1.csv', '')
        print(f"Loading {season}...", end=' ')

        df = pd.read_csv(csv_file, comment='#', sep=r'\s+',
                        names=['MJD', 'log10E', 'AngErr', 'RA', 'Dec', 'Azimuth', 'Zenith'])
        df['season'] = season
        all_events.append(df)
        print(f"{len(df)} events")

    combined = pd.concat(all_events, ignore_index=True)
    print(f"\nTotal: {len(combined):,} events")
    return combined

def prepare_features(df, sample_size=10000):
    """Prepare normalized features for D2 calculation."""
    # Sample if too large (for computational efficiency)
    if len(df) > sample_size:
        df_sample = df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size:,} events for analysis")
    else:
        df_sample = df

    # Features: log10(E), sin(Dec)
    log_e = df_sample['log10E'].values
    sin_dec = np.sin(np.radians(df_sample['Dec'].values))

    # Normalize to [0, 1]
    log_e_norm = (log_e - log_e.min()) / (log_e.max() - log_e.min())
    sin_dec_norm = (sin_dec - sin_dec.min()) / (sin_dec.max() - sin_dec.min())

    return np.column_stack([log_e_norm, sin_dec_norm])

def grassberger_procaccia(features, n_radii=30):
    """Calculate D2 using Grassberger-Procaccia algorithm."""
    N = len(features)
    distances = pdist(features, metric='euclidean')

    d_min = np.percentile(distances[distances > 0], 5)
    d_max = np.percentile(distances, 95)
    r_values = np.logspace(np.log10(d_min), np.log10(d_max), n_radii)

    C_r = []
    for r in r_values:
        count = np.sum(distances < r)
        C_r.append(2.0 * count / (N * (N - 1)))
    C_r = np.array(C_r)

    # Scaling region
    valid = (C_r > 0.01) & (C_r < 0.99)
    if np.sum(valid) < 5:
        return np.nan, np.nan

    log_r = np.log(r_values[valid])
    log_C = np.log(C_r[valid])

    coeffs, cov = np.polyfit(log_r, log_C, 1, cov=True)
    D2 = coeffs[0]
    error = np.sqrt(cov[0, 0])

    return D2, error

def bootstrap_d2(features, n_bootstrap=30):
    """Bootstrap estimation of D2 uncertainty."""
    d2_samples = []
    N = len(features)

    for i in range(n_bootstrap):
        if (i + 1) % 10 == 0:
            print(f"  Bootstrap {i+1}/{n_bootstrap}")
        indices = np.random.choice(N, size=N, replace=True)
        sample = features[indices]
        d2, _ = grassberger_procaccia(sample)
        if not np.isnan(d2):
            d2_samples.append(d2)

    return np.mean(d2_samples), np.std(d2_samples)

def analyze_by_energy(df, bins=[(2, 3), (3, 4), (4, 5), (5, 7)]):
    """Analyze D2 by energy range."""
    results = []

    for e_min, e_max in bins:
        mask = (df['log10E'] >= e_min) & (df['log10E'] < e_max)
        subset = df[mask]

        if len(subset) < 1000:
            print(f"  log10(E) {e_min}-{e_max}: Insufficient events ({len(subset)})")
            continue

        features = prepare_features(subset, sample_size=5000)
        d2, err = grassberger_procaccia(features)

        e_gev_min = 10**e_min
        e_gev_max = 10**e_max
        print(f"  {e_gev_min/1e3:.0f}-{e_gev_max/1e3:.0f} TeV: D2 = {d2:.3f} +/- {err:.3f} (N={len(subset):,})")

        results.append({
            'E_min_TeV': e_gev_min/1e3,
            'E_max_TeV': e_gev_max/1e3,
            'D2': d2,
            'error': err,
            'N': len(subset)
        })

    return results

def analyze_by_declination(df, bins=[(-90, -30), (-30, 0), (0, 30), (30, 90)]):
    """Analyze D2 by declination band."""
    results = []

    for dec_min, dec_max in bins:
        mask = (df['Dec'] >= dec_min) & (df['Dec'] < dec_max)
        subset = df[mask]

        if len(subset) < 1000:
            print(f"  Dec {dec_min} to {dec_max}: Insufficient events ({len(subset)})")
            continue

        features = prepare_features(subset, sample_size=5000)
        d2, err = grassberger_procaccia(features)

        print(f"  Dec [{dec_min}, {dec_max}]: D2 = {d2:.3f} +/- {err:.3f} (N={len(subset):,})")

        results.append({
            'Dec_min': dec_min,
            'Dec_max': dec_max,
            'D2': d2,
            'error': err,
            'N': len(subset)
        })

    return results

def main():
    print("=" * 70)
    print("TFA D2 ANALYSIS: IceCube 10-Year Point Source Data")
    print("=" * 70)
    print()

    # Load data
    df = load_all_events()

    print(f"\nEnergy range: 10^{df['log10E'].min():.1f} - 10^{df['log10E'].max():.1f} GeV")
    print(f"             ({10**df['log10E'].min()/1e3:.1f} TeV - {10**df['log10E'].max()/1e3:.0f} TeV)")
    print(f"Declination: {df['Dec'].min():.1f} to {df['Dec'].max():.1f} deg")
    print()

    # Primary D2 analysis
    print("-" * 70)
    print("PRIMARY D2 CALCULATION (50k sample)")
    print("-" * 70)

    features = prepare_features(df, sample_size=50000)
    D2, fit_error = grassberger_procaccia(features)
    print(f"\nDirect fit: D2 = {D2:.3f} +/- {fit_error:.3f}")

    # Bootstrap
    print("\nRunning bootstrap (100 iterations)...")
    d2_mean, d2_std = bootstrap_d2(features, n_bootstrap=100)
    print(f"Bootstrap:  D2 = {d2_mean:.3f} +/- {d2_std:.3f}")

    # Comparison
    print()
    print("-" * 70)
    print("COMPARISON WITH TFA PREDICTION")
    print("-" * 70)
    print()
    print(f"  TFA Predicted: D2 = {TFA_PREDICTED_D2:.2f} +/- {TFA_PREDICTED_ERROR:.2f}")
    print(f"  Measured:       D2 = {d2_mean:.3f} +/- {d2_std:.3f}")

    difference = abs(d2_mean - TFA_PREDICTED_D2)
    combined_error = np.sqrt(d2_std**2 + TFA_PREDICTED_ERROR**2)
    sigma = difference / combined_error

    print()
    print(f"  Difference: {difference:.3f}")
    print(f"  Combined uncertainty: {combined_error:.3f}")
    print(f"  Deviation: {sigma:.2f} sigma")
    print()

    if sigma < 1:
        print("  STATUS: EXCELLENT AGREEMENT (< 1 sigma)")
    elif sigma < 2:
        print("  STATUS: GOOD AGREEMENT (< 2 sigma)")
    elif sigma < 3:
        print("  STATUS: MARGINAL (2-3 sigma)")
    else:
        print("  STATUS: SIGNIFICANT DEVIATION (> 3 sigma)")

    # Energy stratification
    print()
    print("-" * 70)
    print("ENERGY STRATIFIED ANALYSIS")
    print("-" * 70)
    energy_results = analyze_by_energy(df)

    # Declination bands
    print()
    print("-" * 70)
    print("DECLINATION BAND ANALYSIS")
    print("-" * 70)
    dec_results = analyze_by_declination(df)

    # Summary
    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print()
    print(f"Data: IceCube 10-year point source ({len(df):,} events)")
    print(f"Method: Grassberger-Procaccia correlation dimension")
    print(f"Features: [log10(E), sin(Dec)] normalized to [0,1]")
    print()
    print(f"RESULT: D2 = {d2_mean:.2f} +/- {d2_std:.2f}")
    print(f"TFA:   D2 = {TFA_PREDICTED_D2:.2f} +/- {TFA_PREDICTED_ERROR:.2f}")
    print()
    print(f"Agreement: {sigma:.2f} sigma")

    return {
        'measured_d2': d2_mean,
        'measured_error': d2_std,
        'predicted_d2': TFA_PREDICTED_D2,
        'sigma': sigma,
        'n_events': len(df),
        'energy_results': energy_results,
        'dec_results': dec_results
    }

if __name__ == '__main__':
    results = main()
