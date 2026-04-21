"""
Synthetic Data Generators for Compression Benchmarking

Generates controlled synthetic datasets for testing compression pipelines:
- 2D Gaussian blobs (optimal for Hilbert)
- 2D gradient (smooth, good locality)
- 2D noise (no correlation, worst case)
- 1D random walk → 2D grid (intermediate case)

All generators produce bytes suitable for direct compression testing.
"""

import struct
from typing import Tuple
import numpy as np


def generate_2d_gaussian_blobs(
    side: int,
    n_blobs: int = 5,
    sigma: float = 8.0,
    seed: int = 42
) -> bytes:
    """
    Generate 2D Gaussian blobs (highly correlated, optimal for Hilbert).

    Args:
        side: Image side length (side×side pixels)
        n_blobs: Number of Gaussian blobs
        sigma: Standard deviation of each blob
        seed: Random seed for reproducibility

    Returns:
        Bytes representing the image (grayscale, 8-bit)
    """
    rng = np.random.RandomState(seed)
    image = np.zeros((side, side), dtype=np.float32)

    # Generate blob centers and values
    for _ in range(n_blobs):
        cx = rng.uniform(0, side)
        cy = rng.uniform(0, side)
        intensity = rng.uniform(50, 255)

        # Create Gaussian blob
        yy, xx = np.meshgrid(np.arange(side), np.arange(side), indexing='ij')
        dist_sq = (xx - cx) ** 2 + (yy - cy) ** 2
        blob = intensity * np.exp(-dist_sq / (2 * sigma ** 2))
        image += blob

    # Normalize to [0, 255]
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image.tobytes()


def generate_2d_gradient(
    side: int,
    seed: int = 42
) -> bytes:
    """
    Generate 2D linear gradient (smooth transitions, good locality).

    The gradient goes from (0,0)→(255) at top-left to (0,255)→(255) at bottom-right,
    creating smooth transitions that test edge-preserving compression.

    Args:
        side: Image side length (side×side pixels)
        seed: Random seed (unused, kept for API consistency)

    Returns:
        Bytes representing the image (grayscale, 8-bit)
    """
    xx, yy = np.meshgrid(np.linspace(0, 1, side), np.linspace(0, 1, side))
    # Diagonal gradient
    image = (xx + yy) / 2.0 * 255
    image = np.clip(image, 0, 255).astype(np.uint8)
    return image.tobytes()


def generate_2d_noise(
    side: int,
    seed: int = 42
) -> bytes:
    """
    Generate 2D white noise (no correlation, worst case for compression).

    Pure random noise with no spatial structure—compression should fail.
    This is a negative control test.

    Args:
        side: Image side length (side×side pixels)
        seed: Random seed for reproducibility

    Returns:
        Bytes representing the image (grayscale, 8-bit)
    """
    rng = np.random.RandomState(seed)
    image = rng.randint(0, 256, (side, side), dtype=np.uint8)
    return image.tobytes()


def generate_1d_walk(
    length: int,
    grid_side: int = 256,
    seed: int = 42
) -> bytes:
    """
    Generate 1D random walk that maps to 2D grid.

    Creates a random walk sequence that is then converted to 2D coordinates
    via a Hilbert/raster curve. Tests whether Hilbert reordering can
    recover spatial locality from a 1D walk.

    Args:
        length: Total number of points (must be perfect square or will be clipped)
        grid_side: Side length of the 2D grid (default 256 → 65536 points)
        seed: Random seed for reproducibility

    Returns:
        Bytes representing the walk values (grayscale, 8-bit)
    """
    rng = np.random.RandomState(seed)

    # Generate 1D random walk
    # Start at middle of walk space, take random steps
    walk = np.zeros(length, dtype=np.int32)
    walk[0] = 128  # Start value

    for i in range(1, length):
        step = rng.randint(-5, 6)  # Step size ±5
        walk[i] = np.clip(walk[i-1] + step, 0, 255)

    # Convert to bytes
    return walk.astype(np.uint8).tobytes()


def generate_composite_2d(
    side: int,
    components: Tuple[float, ...] = (0.4, 0.3, 0.3),
    seed: int = 42
) -> bytes:
    """
    Generate a composite 2D image mixing blobs, gradient, and noise.

    Args:
        side: Image side length
        components: Tuple of (blob_weight, gradient_weight, noise_weight)
                   Will be normalized to sum to 1.0
        seed: Random seed

    Returns:
        Bytes representing the composite image
    """
    # Normalize weights
    total = sum(components)
    blob_w, grad_w, noise_w = [c / total for c in components]

    # Generate components
    blobs = np.frombuffer(
        generate_2d_gaussian_blobs(side, n_blobs=3, seed=seed),
        dtype=np.uint8
    ).reshape((side, side))

    gradient = np.frombuffer(
        generate_2d_gradient(side, seed=seed),
        dtype=np.uint8
    ).reshape((side, side))

    noise = np.frombuffer(
        generate_2d_noise(side, seed=seed),
        dtype=np.uint8
    ).reshape((side, side))

    # Composite
    composite = (
        blob_w * blobs.astype(np.float32) +
        grad_w * gradient.astype(np.float32) +
        noise_w * noise.astype(np.float32)
    )

    composite = np.clip(composite, 0, 255).astype(np.uint8)
    return composite.tobytes()


if __name__ == "__main__":
    # Quick test: generate and save samples
    import sys
    from pathlib import Path

    # Ensure UTF-8 output on Windows
    sys.stdout.reconfigure(encoding="utf-8")

    output_dir = Path("datasets/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Generate test samples (small size for fast verification)
    print("Generating synthetic test data...")

    side = 128  # Small for testing

    # Blobs
    blobs = generate_2d_gaussian_blobs(side, n_blobs=4)
    (output_dir / "blobs_128x128.bin").write_bytes(blobs)
    print(f"✓ blobs_128x128.bin ({len(blobs)} bytes)")

    # Gradient
    gradient = generate_2d_gradient(side)
    (output_dir / "gradient_128x128.bin").write_bytes(gradient)
    print(f"✓ gradient_128x128.bin ({len(gradient)} bytes)")

    # Noise
    noise = generate_2d_noise(side)
    (output_dir / "noise_128x128.bin").write_bytes(noise)
    print(f"✓ noise_128x128.bin ({len(noise)} bytes)")

    # Random walk
    walk = generate_1d_walk(side * side)
    (output_dir / "walk_128x128.bin").write_bytes(walk)
    print(f"✓ walk_128x128.bin ({len(walk)} bytes)")

    # Composite
    composite = generate_composite_2d(side)
    (output_dir / "composite_128x128.bin").write_bytes(composite)
    print(f"✓ composite_128x128.bin ({len(composite)} bytes)")

    print(f"\nGenerated {side}×{side} test files to {output_dir}")
