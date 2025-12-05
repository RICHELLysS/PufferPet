"""
🌊 Deep Dive Placeholder Generator 🌊
=====================================
Beware, ye who venture into the abyss...
This script conjures placeholder images for the deep dive screensaver mode.

Creates:
- assets/environment/seabed.png - A haunting deep blue gradient background
- Optional sleep images for pets (if needed)

Warning: These are but shadows of the true deep sea horrors that await...
"""

import os
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
    import struct
    import zlib
    
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


def create_seabed_background():
    """
    Creates the seabed background image for deep dive mode.
    
    From the twilight zone to the hadal depths...
    A gradient that captures the essence of the crushing deep.
    """
    # Create assets/environment directory if it doesn't exist
    env_dir = Path("assets/environment")
    env_dir.mkdir(parents=True, exist_ok=True)
    
    # Deep blue gradient colors
    # Top: Lighter deep blue (twilight zone)
    # Bottom: Near-black deep blue (abyssal zone)
    top_color = (0, 50, 100)      # Dark blue surface
    bottom_color = (0, 10, 30)    # Near-black abyss
    
    # Create a smaller gradient that will be scaled up
    # Using 192x108 (1/10 scale) for faster generation
    width, height = 192, 108
    
    print(f"🌊 Conjuring the seabed from the depths... ({width}x{height})")
    
    png_data = create_gradient_image(width, height, top_color, bottom_color)
    
    seabed_path = env_dir / "seabed.png"
    with open(seabed_path, 'wb') as f:
        f.write(png_data)
    
    print(f"✅ Created: {seabed_path}")
    print(f"   Size: {len(png_data)} bytes")
    return seabed_path


def create_sleep_placeholder(pet_id: str, color: tuple):
    """
    Creates a sleep placeholder image for a pet.
    
    Even the creatures of the deep must rest...
    This creates a simple colored square with 'zzz' effect (darker shade).
    
    Args:
        pet_id: The pet identifier
        color: RGB tuple for the pet's color
    """
    pet_dir = Path(f"assets/{pet_id}")
    if not pet_dir.exists():
        print(f"⚠️ Pet directory not found: {pet_dir}")
        return None
    
    # Create a darker version of the color for "sleeping"
    sleep_color = (
        max(0, color[0] - 30),
        max(0, color[1] - 30),
        max(0, color[2] - 30)
    )
    
    # Create a simple 64x64 solid color image
    width, height = 64, 64
    
    import struct
    import zlib
    
    def create_solid_png(w: int, h: int, rgb: tuple) -> bytes:
        """Create a solid color PNG."""
        def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
            chunk_len = struct.pack('>I', len(data))
            chunk_crc = struct.pack('>I', zlib.crc32(chunk_type + data) & 0xffffffff)
            return chunk_len + chunk_type + data + chunk_crc
        
        signature = b'\x89PNG\r\n\x1a\n'
        ihdr_data = struct.pack('>IIBBBBB', w, h, 8, 2, 0, 0, 0)
        ihdr = png_chunk(b'IHDR', ihdr_data)
        
        raw_data = b''
        for _ in range(h):
            raw_data += b'\x00'
            for _ in range(w):
                raw_data += bytes([rgb[0], rgb[1], rgb[2]])
        
        compressed = zlib.compress(raw_data, 9)
        idat = png_chunk(b'IDAT', compressed)
        iend = png_chunk(b'IEND', b'')
        
        return signature + ihdr + idat + iend
    
    png_data = create_solid_png(width, height, sleep_color)
    
    sleep_path = pet_dir / "sleep_idle.png"
    with open(sleep_path, 'wb') as f:
        f.write(png_data)
    
    print(f"😴 Created sleep image: {sleep_path}")
    return sleep_path


def main():
    """
    Main entry point for the deep dive placeholder generator.
    
    "In the deep, no one can hear you scream... 
     but they can see your beautiful gradient backgrounds."
    """
    print("=" * 60)
    print("🦑 DEEP DIVE PLACEHOLDER GENERATOR 🦑")
    print("   Summoning images from the crushing depths...")
    print("=" * 60)
    print()
    
    # Create the seabed background
    create_seabed_background()
    
    print()
    print("=" * 60)
    print("✨ Deep dive placeholders created successfully!")
    print("   The abyss awaits your exploration...")
    print("=" * 60)


if __name__ == "__main__":
    main()
