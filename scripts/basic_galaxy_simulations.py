import numpy as np
import matplotlib.pyplot as plt

# Parameters
N_galaxies = 200  # number of galaxies
field_size = 100  # size of the field in arbitrary units
random_seed = 42

np.random.seed(random_seed)

# Galaxy positions
x = np.random.uniform(0, field_size, N_galaxies)
y = np.random.uniform(0, field_size, N_galaxies)

# Base ellipticities (axis ratio)
ellipticity = np.full(N_galaxies, 0.6)

# Random orientations (uniform between 0 and pi)
theta_random = np.random.uniform(0, np.pi, N_galaxies)

def apply_intrinsic_alignment(theta, strength=0.0, preferred_angle=0.0):
    """
    Blend random orientations with alignment toward preferred_angle.
    strength = 0: random, strength = 1: fully aligned.
    """
    return (1 - strength) * theta + strength * preferred_angle

def apply_lensing_shear(theta, shear_angle=0.0, shear_strength=0.0):
    """
    Approximate: shear rotates all orientations by a fixed amount.
    (For simplicity; in reality, lensing also affects ellipticity.)
    """
    return theta + shear_strength * np.cos(theta - shear_angle)

IA_strength = 0.6  # 0 = random, 1 = perfectly aligned
preferred_angle = np.pi / 4  # 45 degrees

theta_IA = apply_intrinsic_alignment(theta_random, IA_strength, preferred_angle)

# Example: apply some lensing shear
shear_strength = 0.3
shear_angle = np.pi / 2  # 90 degrees

theta_IA_shear = apply_lensing_shear(theta_IA, shear_angle, shear_strength)

# For visualization, plot ellipses
def plot_galaxies(x, y, ellipticity, theta, title="Galaxy Field"):
    fig, ax = plt.subplots(figsize=(8,8))
    ax.set_aspect('equal')
    ax.set_xlim(0, field_size)
    ax.set_ylim(0, field_size)

    for xi, yi, e, t in zip(x, y, ellipticity, theta):
        width = 1.0
        height = width * e
        ellipse = plt.matplotlib.patches.Ellipse(
            (xi, yi),
            width=width,
            height=height,
            angle=np.degrees(t),
            edgecolor='blue',
            facecolor='blue',
            alpha=0.6
        )
        ax.add_patch(ellipse)

    ax.set_title(title)
    plt.show()

# Plotting
plot_galaxies(x, y, ellipticity, theta_random, title="Random Orientations")
plot_galaxies(x, y, ellipticity, theta_IA, title="With Intrinsic Alignment")
plot_galaxies(x, y, ellipticity, theta_IA_shear, title="With IA + Lensing Shear")
