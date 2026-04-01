#!/usr/bin/env python3
"""
Generate visualization for Pickett Plot blog post.
Creates a log-log resistivity-porosity crossplot with water saturation isolines.
"""

import logging
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(message)s')

# Set publication-quality defaults
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 10
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.labelsize'] = 11
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['xtick.labelsize'] = 9
plt.rcParams['ytick.labelsize'] = 9
plt.rcParams['legend.fontsize'] = 9
plt.rcParams['axes.grid'] = False

logger.info("Generating Pickett plot...")
logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def pickett_isoline(rt_range, sw, rw=0.03, m=2.0, n=2.0, a=1.0):
    """Calculate porosity for constant Sw isoline."""
    numerator = a * rw
    denominator = rt_range * (sw ** n)
    phi = (numerator / denominator) ** (1.0 / m)
    return np.clip(phi, 0.001, 0.5)

# Generate synthetic well log data with realistic patterns
np.random.seed(42)
n_samples = 250

# Create three zones with different characteristics
# Zone 1: Water-bearing sand (high phi, low Rt, Sw ~ 1.0)
n1 = 80
phi_water = np.random.uniform(0.15, 0.25, n1)
rt_water = 0.03 / (phi_water ** 2.0)  # On water line
rt_water *= np.random.lognormal(0, 0.3, n1)  # Add scatter

# Zone 2: Hydrocarbon pay (moderate phi, high Rt, Sw ~ 0.3-0.5)
n2 = 90
phi_hc = np.random.uniform(0.08, 0.18, n2)
sw_hc = np.random.uniform(0.25, 0.50, n2)
rt_hc = 0.03 / ((phi_hc ** 2.0) * (sw_hc ** 2.0))
rt_hc *= np.random.lognormal(0, 0.2, n2)

# Zone 3: Tight zone (low phi, variable Rt, Sw ~ 0.6-1.0)
n3 = 80
phi_tight = np.random.uniform(0.02, 0.08, n3)
sw_tight = np.random.uniform(0.6, 1.0, n3)
rt_tight = 0.03 / ((phi_tight ** 2.0) * (sw_tight ** 2.0))
rt_tight *= np.random.lognormal(0, 0.35, n3)

# Combine all zones
phi_all = np.concatenate([phi_water, phi_hc, phi_tight])
rt_all = np.concatenate([rt_water, rt_hc, rt_tight])

# Clip to reasonable ranges
rt_all = np.clip(rt_all, 0.1, 1000)
phi_all = np.clip(phi_all, 0.01, 0.35)

# Create figure
fig, ax = plt.subplots(figsize=(8, 8))

# Plot isolines
rt_range = np.logspace(-1, 3, 200)
sw_lines = [1.0, 0.8, 0.6, 0.4, 0.2]

for sw in sw_lines:
    phi_line = pickett_isoline(rt_range, sw)
    
    if sw == 1.0:
        linestyle = '-'
        linewidth = 1.2
        alpha = 1.0
        label = f'Sw = {int(sw*100)}% (water line)'
    elif sw >= 0.5:
        linestyle = '--'
        linewidth = 0.9
        alpha = 0.7
        label = f'Sw = {int(sw*100)}%'
    else:
        linestyle = ':'
        linewidth = 0.9
        alpha = 0.7
        label = f'Sw = {int(sw*100)}%'
    
    ax.plot(
        rt_range,
        phi_line,
        color='black',
        linestyle=linestyle,
        linewidth=linewidth,
        alpha=alpha,
        label=label
    )

# Plot data points
ax.scatter(
    rt_all,
    phi_all,
    color='gray',
    s=12,
    alpha=0.5,
    edgecolors='none',
    label='Log data'
)

# Set log scales
ax.set_xscale('log')
ax.set_yscale('log')

# Set limits
ax.set_xlim(0.1, 1000)
ax.set_ylim(0.01, 0.5)

# Labels
ax.set_xlabel('True Resistivity, Rt (ohm-m)', fontsize=11)
ax.set_ylabel('Porosity, φ (fraction)', fontsize=11)
ax.set_title('Pickett Plot', fontsize=12)

# Legend
ax.legend(loc='lower left', frameon=False, fontsize=9)

# Remove top and right spines
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

# Light grid
ax.grid(True, which='both', linestyle=':', linewidth=0.3, alpha=0.5)

plt.tight_layout()
plt.savefig('pickett_plot.png', dpi=300, bbox_inches='tight')
plt.close()

logger.info("Generated: pickett_plot.png")
logger.info("Plot uses synthetic data for demonstration.\n")


