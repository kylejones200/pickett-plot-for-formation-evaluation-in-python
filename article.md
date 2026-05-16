# Pickett Plot for Formation Evaluation in Python

*A log-log crossplot of resistivity and porosity for water saturation estimation*

---

Before a well goes on production, a petrophysicist must answer one fundamental question: is the pore space filled with hydrocarbons or water? A reservoir with 20% porosity is exciting. The same reservoir with 95% water saturation is a water well.

The Pickett plot is a graphical method for estimating water saturation across a log interval. Resistivity plotted against porosity on log-log axes reveals the Archie equation visually, without iterative calculations.

## The Archie Equation

Archie's law relates formation resistivity to water saturation:

```
Rt = (a · Rw) / (φ^m · Sw^n)
```

Parameters:
- `Rt`: true formation resistivity, measured by the resistivity log
- `Rw`: formation water resistivity, from nearby water-bearing zones or catalogs
- `φ`: porosity, from density or neutron log
- `Sw`: water saturation, what we want
- `a`: tortuosity factor, typically 1.0 for carbonates, 0.62 for sandstones
- `m`: cementation exponent, typically 2.0
- `n`: saturation exponent, typically 2.0

Rearranging for porosity at constant Sw gives a straight line on log-log axes. That is the isosaturation line.

## Why a Crossplot?

On a log-log plot of Rt vs porosity, the Archie equation defines a family of parallel lines, one per water saturation value. Data points that plot above the Sw = 1.0 line (the water line) have higher resistivity than a fully water-saturated rock of that porosity. They contain hydrocarbons. How far above the water line tells you the saturation, without solving the equation.

## Implementation

```python
import numpy as np
import matplotlib.pyplot as plt

rw = 0.03    # formation water resistivity (ohm·m)
m = 2.0      # cementation exponent
n = 2.0      # saturation exponent
a = 1.0      # tortuosity

def pickett_isoline(rt_range, sw, rw=0.03, m=2.0, n=2.0, a=1.0):
    phi = (a * rw / (rt_range * sw**n)) ** (1.0 / m)
    return np.clip(phi, 0.001, 0.5)

rt_range = np.logspace(-1, 3, 300)
sw_values = [1.0, 0.8, 0.6, 0.4, 0.2]

fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xscale('log')
ax.set_yscale('log')

for sw in sw_values:
    phi_line = pickett_isoline(rt_range, sw, rw, m, n, a)
    mask = (phi_line > 0.01) & (phi_line < 0.45)
    ax.plot(rt_range[mask], phi_line[mask], 'k-', linewidth=0.8, alpha=0.6)
    ax.text(rt_range[mask][-1], phi_line[mask][-1], f"Sw = {int(sw*100)}%", fontsize=8)

ax.set_xlabel("Rt (ohm·m)")
ax.set_ylabel("Porosity (fraction)")
```

## Plotting Well Log Data

Data points come from LAS files or processed log CSVs. Each row is a depth sample with measured resistivity and computed porosity:

```python
np.random.seed(42)

phi_pay = np.random.uniform(0.12, 0.22, 80)
rt_pay = (a * rw / (phi_pay**m * 0.25**n)) * np.random.lognormal(0, 0.3, 80)

phi_trans = np.random.uniform(0.08, 0.18, 60)
rt_trans = (a * rw / (phi_trans**m * 0.55**n)) * np.random.lognormal(0, 0.25, 60)

phi_water = np.random.uniform(0.05, 0.20, 80)
rt_water = (a * rw / (phi_water**m * 1.0**n)) * np.random.lognormal(0, 0.2, 80)

ax.scatter(rt_pay, phi_pay, s=10, label='Pay zone', zorder=5)
ax.scatter(rt_trans, phi_trans, s=10, marker='s', label='Transition', zorder=5)
ax.scatter(rt_water, phi_water, s=10, marker='^', label='Water', zorder=5)
ax.legend()
```

## Reading the Plot

**Water zone:** points align along the Sw = 100% isoline. This is a direct check on your assumed Rw. If the water-bearing data does not follow the Sw = 1 line for your chosen Rw, adjust Rw before interpreting the rest.

**Pay zone:** points fall above and to the right of the Sw = 100% line, toward lower saturation isolines. Points near Sw = 20-40% represent commercial hydrocarbons.

**Transition zone:** points scatter between the water line and the pay zone. Mixed saturation, often capillary-controlled.

**Water line slope:** on log-log axes, the slope of the Sw = 1 line equals -m. If the water-bearing data defines a slope of -1.8 rather than -2.0, m needs updating for this formation before computing Sw.

## Estimating Rw Graphically

The Pickett plot also lets you estimate Rw without a catalog. Identify water-bearing zones from the SP log or nearby well control. At full water saturation (Sw = 1) and unit porosity (φ = 1), the Archie equation reduces to:

```
Rt = a · Rw
```

For a = 1, the resistivity at unit porosity along the water line equals Rw. Fit the slope of the water-bearing trend first to get m, then extrapolate that line to φ = 1 to read off Rw. The two-parameter graphical solution is one reason petrophysicists have used this plot for sixty years.

---

The Pickett plot earns its place even when software can solve Archie iteratively. It shows the entire dataset at once. Outliers, interpretation errors, and zone transitions are visible in ways that a column of computed Sw values are not. Run it as quality control before trusting any log-derived saturation.

Three things to check every time:
- **Water line slope:** should equal -m. If it does not, update m before computing Sw across the interval.
- **Scatter on the water line:** high scatter points to variable Rw (mixed salinity) or porosity calculation error.
- **Points near Sw = 0.2:** those are your pay candidates. Anything above Sw = 0.5 that is not labeled pay deserves a second look.
