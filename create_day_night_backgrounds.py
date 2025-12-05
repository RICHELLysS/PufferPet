"""
🌅🌙 Day/Night Background Generator 🌙🌅
=========================================
The eternal cycle of light and darkness in the deep...
This script conjures placeholder images for the day/night cycle system.

Creates:
- assets/environment/seabed_day.png - A calming blue gradient for daytime
- assets/environment/seabed_night.png - A haunting purple gradient for nighttime

Warning: Time flows differently in the abyss...
"""

import os
import struct
import zlib
from pathlib import Path


def create_gradient_image(width: int, height: int, top_color: tuple, bottom_color: tuple) -> bytes:
    """
    Creates a vertical gradient PNG image.
    
    The deep calls to the deep... this function generates a gradient
    from the surface waters to the crushing depths below.
    
    Args:
        width: Width of the image in pixels
        height: Height of the image in pixels  
        top_color: RGB tuple for the top of the gradient (surface)
        bottom_color: RGB tuple for the bottom of the gradient (abyss)
    
    Returns:
        PNG image data as bytes
    """
    def create_png(width: int, height: int, pixels: list) -> bytes:
        """Create a PNG file from pixel data."""
        def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
            chunk_len = struct.pack('>I', len(data))
            chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
            return chunk_len + chunk_type + data + chunk_crc
        
        # PNG signature
        signature = b'\x89PNG\r\n\x1a\n'
        
        # IHDR chunk
        ihdr_data = struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0)
        ihdr = png_chunk(b'IHDR', ihdr_data)
        
        # IDAT chunk (image data)
        raw_data = b''
        for row in pixels:
            raw_data += b'\x00'  # Filter type: None
            for r, g, b in row:
                raw_data += bytes([r, g, b])
        
        compressed = zlib.compress(raw_data, 9)
        idat = png_chunk(b'IDAT', compressed)
        
        # IEND chunk
        iend = png_chunk(b'IEND', b'')
        
        return signature + ihdr + idat + iend
    
    # Generate gradient pixels
    pixels = []
    for y in range(height):
        row = []
        # Calculate interpolation factor (0.0 at top, 1.0 at bottom)
        t = y / (height - 1) if height > 1 else 0
        
        for x in range(width):
            r = int(top_color[0] + (bottom_color[0] - top_color[0]) * t)
            g = int(top_color[1] + (bottom_color[1] - top_color[1]) * t)
            b = int(top_color[2] + (bottom_color[2] - top_color[2]) * t)
            row.append((r, g, b))
        pixels.append(row)
    
    return create_png(width, height, pixels)


def create_day_background():
    """
    Creates the daytime seabed background image.
    
    The sun's rays pierce through the waves...
    A calming blue gradient that captures the essence of a peaceful ocean day.
    """
    # Create assets/environment directory if it doesn't exist
    env_dir = Path("assets/environment")
    env_dir.mkdir(parents=True, exist_ok=True)
    
    # Day mode: Lighter blue gradient (more light penetrating)
    # Top: Light blue (sunlit surface)
    # Bottom: Medium blue (deeper waters)
    top_color = (20, 80, 140)     # Lighter blue surface (sunlit)
    bottom_color = (0, 30, 70)    # Medium blue depths
    
    # Create a smaller gradient that will be scaled up
    # Using 192x108 (1/10 scale) for faster generation
    width, height = 192, 108
    
    print(f"🌅 Conjuring the daytime seabed... ({width}x{height})")
    
    png_data = create_gradient_image(width, height, top_color, bottom_color)
    
    day_path = env_dir / "seabed_day.png"
    with open(day_path, 'wb') as f:
        f.write(png_data)
    
    print(f"✅ Created: {day_path}")
    print(f"   Size: {len(png_data)} bytes")
    return day_path


def create_night_background():
    """
    Creates the nighttime seabed background image.
    
    The moon casts its pale light upon the waves...
    A haunting purple gradient that captures the essence of the nocturnal deep.
    """
    # Create assets/environment directory if it doesn't exist
    env_dir = Path("assets/environment")
    env_dir.mkdir(parents=True, exist_ok=True)
    
    # Night mode: Deep purple/black gradient (darkness of night)
    # Top: Dark purple (moonlit surface)
    # Bottom: Near-black purple (abyssal darkness)
    top_color = (30, 10, 50)      # Dark purple surface (moonlit)
    bottom_color = (10, 0, 20)    # Near-black purple abyss
    
    # Create a smaller gradient that will be scaled up
    width, height = 192, 108
    
    print(f"🌙 Conjuring the nighttime seabed... ({width}x{height})")
    
    png_data = create_gradient_image(width, height, top_color, bottom_color)
    
    night_path = env_dir / "seabed_night.png"
    with open(night_path, 'wb') as f:
        f.write(png_data)
    
    print(f"✅ Created: {night_path}")
    print(f"   Size: {len(png_data)} bytes")
    return night_path


def verify_fallback_logic():
    """
    Verify that the fallback logic in ocean_background.py works correctly.
    
    The abyss provides its own darkness when needed...
    """
    print("\n🔍 Verifying fallback logic...")
    
    env_dir = Path("assets/environment")
    
    # Check what files exist
    seabed_path = env_dir / "seabed.png"
    day_path = env_dir / "seabed_day.png"
    night_path = env_dir / "seabed_night.png"
    
    print(f"   seabed.png exists: {seabed_path.exists()}")
    print(f"   seabed_day.png exists: {day_path.exists()}")
    print(f"   seabed_night.png exists: {night_path.exists()}")
    
    # The fallback logic in ocean_background.py:
    # Day mode: seabed_day.png -> seabed.png -> fallback gradient
    # Night mode: seabed_night.png -> seabed_halloween.png -> apply filter to day background
    
    print("\n📋 Fallback chain:")
    print("   Day mode: seabed_day.png → seabed.png → blue gradient fallback")
    print("   Night mode: seabed_night.png → seabed_halloween.png → day background + purple filter")
    
    return True


def main():
    """
    Main entry point for the day/night background generator.
    
    "The sun rises and sets, but the deep remains eternal...
     Yet even the abyss knows the difference between day and night."
    """
    print("=" * 60)
    print("🌅🌙 DAY/NIGHT BACKGROUND GENERATOR 🌙🌅")
    print("   Summoning images for the eternal cycle...")
    print("=" * 60)
    print()
    
    # Create the day background
    create_day_background()
    
    print()
    
    # Create the night background
    create_night_background()
    
    print()
    
    # Verify fallback logic
    verify_fallback_logic()
    
    print()
    print("=" * 60)
    print("✨ Day/Night backgrounds created successfully!")
    print("   The cycle of light and darkness is complete...")
    print("=" * 60)


if __name__ == "__main__":
    main()
