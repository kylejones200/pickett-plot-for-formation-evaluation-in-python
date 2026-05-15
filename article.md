# Pickett Plot for Formation Evaluation in Python

*A log-log crossplot of resistivity and porosity for water saturation estimation*

---

Before a well can be put on production, a petrophysicist must answer a fundamental question: is the pore space filled with hydrocarbons or water? A reservoir with 20% porosity is exciting. A reservoir with 20% porosity and 95% water saturation is a water well.

The Pickett plot is a graphical method for estimating water saturation across a log interval. By plotting resistivity against porosity on log-log axes, it reveals the Archie equation visually — no iterative calculations required.

## The Archie Equation

Archie's law relates formation resistivity to water saturation:

```
Rt = (a · Rw) / (φ^m · Sw^n)
```

Where:
- `Rt` — true formation resistivity (measured by the resistivity log)
- `Rw` — formation water resistivity (estimated from nearby water-bearing zones or catalogs)
- `φ` — porosity (from density or neutron log)
- `Sw` — water saturation (what we want)
- `a` — tortuosity factor (typically 1.0 for carbonates, 0.62 for sandstones)
- `m` — cementation exponent (typically 2.0)
- `n` — saturation exponent (typically 2.0)

Rearranging for porosity at a constant Sw gives a straight line on log-log axes — the isosaturation line.

## Why a Crossplot?

On a standard Rt vs φ plot (both on log scales), the Archie equation defines a family of parallel lines — one for each water saturation value. Data points that plot above the Sw=1.0 line (the water line) have resistivity higher than a fully water-saturated rock of that porosity — they contain hydrocarbons.

This is the Pickett plot: the position of a data point relative to the water line tells you its water saturation immediately, without solving the Archie equation numerically.

## Implementation in Python

```python
import numpy as np
import matplotlib.pyplot as plt

# Archie parameters
rw = 0.03    # formation water resistivity (ohm·m)
m = 2.0      # cementation exponent
n = 2.0      # saturation exponent
a = 1.0      # tortuosity

def pickett_isoline(rt_range, sw, rw=0.03, m=2.0, n=2.0, a=1.0):
    """Porosity along a constant-Sw isoline."""
    phi = (a * rw / (rt_range * sw**n)) ** (1.0 / m)
    return np.clip(phi, 0.001, 0.5)

# Draw water saturation isolines
rt_range = np.logspace(-1, 3, 300)  # 0.1 to 1000 ohm·m
sw_values = [1.0, 0.8, 0.6, 0.4, 0.2]

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xscale('log')
ax.set_yscale('log')

for sw in sw_values:
    phi_line = pickett_isoline(rt_range, sw, rw, m, n, a)
    mask = (phi_line > 0.01) & (phi_line < 0.45)
    label = f"Sw = {int(sw*100)}%"
    ax.plot(rt_range[mask], phi_line[mask], 'k-', linewidth=0.8, alpha=0.6)
    ax.text(rt_range[mask][-1], phi_line[mask][-1], label, fontsize=8)

ax.set_xlabel("Rt (ohm·m)")
ax.set_ylabel("Porosity (fraction)")
ax.set_title("Pickett Plot")
```

## Plotting Well Log Data

The data comes from a LAS file or processed log CSV. Each row is a depth sample with measured resistivity and computed porosity:

```python
# Synthetic well log data — three zones
np.random.seed(42)

# Pay zone: high Rt, moderate porosity
phi_pay = np.random.uniform(0.12, 0.22, 80)
rt_pay = (a * rw / (phi_pay**m * 0.25**n)) * np.random.lognormal(0, 0.3, 80)

# Transition zone: moderate Rt
phi_trans = np.random.uniform(0.08, 0.18, 60)
rt_trans = (a * rw / (phi_trans**m * 0.55**n)) * np.random.lognormal(0, 0.25, 60)

# Water zone: low Rt following the Sw=1 line
phi_water = np.random.uniform(0.05, 0.20, 80)
rt_water = (a * rw / (phi_water**m * 1.0**n)) * np.random.lognormal(0, 0.2, 80)

# Plot on the Pickett crossplot
ax.scatter(rt_pay, phi_pay, c='black', s=10, label='Pay zone', zorder=5)
ax.scatter(rt_trans, phi_trans, c='gray', s=10, marker='s', label='Transition', zorder=5)
ax.scatter(rt_water, phi_water, c='lightgray', s=10, marker='^', label='Water', zorder=5)
ax.legend()
```

## Reading the Plot

**Water zone:** data points align along the Sw = 100% isoline. This gives you a direct read of Rw from the intercept — it is a quality-control check on your assumed formation water resistivity.

**Pay zone:** data points plot above and to the right of the Sw = 100% line, toward lower saturation isolines. Points near Sw = 20-40% represent commercial hydrocarbons.

**Transition zone:** data points scatter between the water line and the pay zone — mixed saturation, often capillary-controlled.

**Slope of the water line:** on log-log axes, the slope of the Sw=1 line equals `-m` (the cementation exponent). If your data's water-bearing points define a line with slope −1.8 instead of −2.0, consider updating m for this specific formation.

## Estimating Rw Graphically

A powerful use of the Pickett plot: estimate Rw without a water catalog. Identify the water-bearing zone from the SP log or nearby well control. The Archie equation at full water saturation (Sw = 1) and unit porosity (φ = 1) simplifies to:

```
Rt = a · Rw / (1^m · 1^n) = a · Rw
```

So for `a = 1`, the resistivity of a 100% porous, fully water-saturated rock equals Rw. Extrapolate the Sw = 1 isoline to φ = 1 on the x-axis — the resistivity at that intercept is your formation water resistivity. You are reading Rw off the graph, not computing it.

In practice, you fit the slope of the water-bearing data trend first (giving you m), then extrapolate that line to φ = 1 to read Rw. The two-parameter graphical solution is one reason petrophysicists have used the Pickett plot for sixty years.

## Key Takeaways

The Pickett plot earns its place in a modern workflow even when you have software to solve Archie iteratively. It shows the whole dataset at once — outliers, interpretation errors, and zone transitions are visible immediately in ways that a column of computed Sw values are not. Use it as QC before trusting any log-derived saturation.

Three things to always check on a Pickett plot:
- **Water line slope**: should equal -m. If it doesn't, m needs to be updated for this formation.
- **Scatter on the water line**: high scatter means Rw is variable (mixed water salinity) or the porosity calculation has error.
- **Points above Sw = 0.2**: these are your pay intervals. Anything above Sw = 0.5 that is not labeled as pay is worth a second look.
