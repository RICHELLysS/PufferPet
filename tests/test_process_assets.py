"""
WARNING: Testing the Cursed Artisan's Workshop
===============================================
These tests ensure the sprite processing tools work correctly.
The spirits must be properly summoned and transformed...

Tests cover:
- Background removal (rembg and fallback)
- Halloween transformation (grayscale + colorize + opacity)
- Sprite sheet slicing
- Row ignoring logic

NOTE: This test module is skipped because tools/process_assets.py has been removed in V6.
"""

import os
import sys
import tempfile
import shutil
import pytest
from PIL import Image

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Skip entire module if process_assets doesn't exist
pytest.importorskip("tools.process_assets", reason="tools/process_assets.py has been removed in V6")

from tools.process_assets import AssetProcessor


class TestAssetProcessor:
    """Test suite for the cursed AssetProcessor."""
    
    @pytest.fixture
    def processor(self):
        """Create a fresh AssetProcessor instance."""
        return AssetProcessor()
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for test outputs."""
        temp = tempfile.mkdtemp()
        yield temp
        shutil.rmtree(temp)
    
    @pytest.fixture
    def simple_image(self):
        """Create a simple test image with white background and colored center."""
        img = Image.new('RGBA', (100, 100), (255, 255, 255, 255))
        # Draw a red square in the center
        for x in range(25, 75):
            for y in range(25, 75):
                img.putpixel((x, y), (255, 0, 0, 255))
        return img
    
    @pytest.fixture
    def sprite_sheet(self):
        """Create a simple 2x2 sprite sheet for testing."""
        # 200x200 image with 4 quadrants of different colors
        img = Image.new('RGBA', (200, 200), (255, 255, 255, 255))
        
        # Top-left: Red
        for x in range(100):
            for y in range(100):
                img.putpixel((x, y), (255, 0, 0, 255))
        
        # Top-right: Green
        for x in range(100, 200):
            for y in range(100):
                img.putpixel((x, y), (0, 255, 0, 255))
        
        # Bottom-left: Blue
        for x in range(100):
            for y in range(100, 200):
                img.putpixel((x, y), (0, 0, 255, 255))
        
        # Bottom-right: Yellow
        for x in range(100, 200):
            for y in range(100, 200):
                img.putpixel((x, y), (255, 255, 0, 255))
        
        return img


class TestBackgroundRemoval(TestAssetProcessor):
    """Tests for background removal functionality - Requirements 32.2-32.4."""
    
    def test_color_tolerance_remove_white_background(self, processor, simple_image):
        """Test that white background is removed using color tolerance method."""
        # Force use of color tolerance method
        processor.use_rembg = False
        
        result = processor.remove_background(simple_image)
        
        # Check that result is RGBA
        assert result.mode == 'RGBA'
        
        # Check that corner (background) is transparent
        corner_pixel = result.getpixel((0, 0))
        assert corner_pixel[3] == 0, "Background should be transparent"
        
        # Check that center (red square) is still visible
        center_pixel = result.getpixel((50, 50))
        assert center_pixel[3] == 255, "Foreground should be opaque"
        assert center_pixel[0] == 255, "Red channel should be preserved"
    
    def test_color_tolerance_preserves_non_background_colors(self, processor):
        """Test that colors different from background are preserved."""
        processor.use_rembg = False
        
        # Create image with blue background and various colored pixels
        img = Image.new('RGBA', (50, 50), (0, 0, 255, 255))  # Blue background
        img.putpixel((25, 25), (255, 0, 0, 255))  # Red pixel
        img.putpixel((26, 25), (0, 255, 0, 255))  # Green pixel
        
        result = processor.remove_background(img)
        
        # Background should be transparent
        assert result.getpixel((0, 0))[3] == 0
        
        # Red and green pixels should be preserved
        assert result.getpixel((25, 25))[3] == 255
        assert result.getpixel((26, 25))[3] == 255
    
    def test_remove_background_converts_to_rgba(self, processor):
        """Test that non-RGBA images are converted."""
        processor.use_rembg = False
        
        # Create RGB image (no alpha)
        img = Image.new('RGB', (50, 50), (255, 255, 255))
        
        result = processor.remove_background(img)
        
        assert result.mode == 'RGBA'


class TestHalloweenify(TestAssetProcessor):
    """Tests for Halloween transformation - Requirements 33.1-33.4."""
    
    def test_halloweenify_returns_rgba(self, processor, simple_image):
        """Test that halloweenify returns RGBA image."""
        result = processor.halloweenify(simple_image)
        assert result.mode == 'RGBA'
    
    def test_halloweenify_preserves_transparency(self, processor):
        """Test that transparent areas remain transparent."""
        # Create image with transparent background
        img = Image.new('RGBA', (50, 50), (0, 0, 0, 0))
        # Add opaque red square
        for x in range(10, 40):
            for y in range(10, 40):
                img.putpixel((x, y), (255, 0, 0, 255))
        
        result = processor.halloweenify(img)
        
        # Corner should still be transparent
        assert result.getpixel((0, 0))[3] == 0
        
        # Center should have reduced opacity (70%)
        center_alpha = result.getpixel((25, 25))[3]
        expected_alpha = int(255 * 0.7)
        assert abs(center_alpha - expected_alpha) <= 5, f"Expected ~{expected_alpha}, got {center_alpha}"
    
    def test_halloweenify_applies_ghost_color(self, processor, simple_image):
        """Test that ghost colors (green or purple) are applied."""
        # Run multiple times to check both colors can be applied
        colors_seen = set()
        
        for _ in range(20):
            result = processor.halloweenify(simple_image)
            # Check center pixel color
            pixel = result.getpixel((50, 50))
            # Ghost colors are green (0, 255, 0) or purple (170, 0, 255)
            # After colorization, we should see these hues
            if pixel[1] > pixel[0] and pixel[1] > pixel[2]:
                colors_seen.add('green')
            elif pixel[2] > pixel[0] and pixel[2] > pixel[1]:
                colors_seen.add('purple')
        
        # Should see at least one of the ghost colors
        assert len(colors_seen) >= 1, "Should apply ghost colors"
    
    def test_halloweenify_reduces_opacity(self, processor):
        """Test that opacity is reduced to 70%."""
        # Create fully opaque image
        img = Image.new('RGBA', (50, 50), (255, 0, 0, 255))
        
        result = processor.halloweenify(img)
        
        # Check that alpha is approximately 70% of 255
        expected_alpha = int(255 * 0.7)
        actual_alpha = result.getpixel((25, 25))[3]
        
        assert abs(actual_alpha - expected_alpha) <= 5, \
            f"Expected alpha ~{expected_alpha}, got {actual_alpha}"


class TestProcessSheet(TestAssetProcessor):
    """Tests for sprite sheet slicing - Requirements 32.5-32.8."""
    
    def test_process_sheet_creates_correct_number_of_files(self, processor, sprite_sheet, temp_dir):
        """Test that correct number of frames are generated."""
        # Save sprite sheet to temp file
        input_path = os.path.join(temp_dir, "baby_idle.png")
        sprite_sheet.save(input_path)
        
        # Process as 2x2 grid with 2 actions
        processor.process_sheet(
            input_path,
            rows=2, cols=2,
            row_actions=["idle", "swim"]
        )
        
        # Should create 4 normal frames + 4 halloween frames = 8 files
        files = os.listdir(temp_dir)
        png_files = [f for f in files if f.endswith('.png') and f != "baby_idle.png"]
        
        # 2 rows * 2 cols = 4 frames, each with normal + halloween = 8
        assert len(png_files) == 8, f"Expected 8 files, got {len(png_files)}: {png_files}"
    
    def test_process_sheet_correct_naming(self, processor, sprite_sheet, temp_dir):
        """Test that output files have correct naming format."""
        input_path = os.path.join(temp_dir, "baby_idle.png")
        sprite_sheet.save(input_path)
        
        processor.process_sheet(
            input_path,
            rows=2, cols=2,
            row_actions=["idle", "swim"]
        )
        
        files = os.listdir(temp_dir)
        
        # Check for expected file names
        expected_files = [
            "baby_idle_0.png", "baby_idle_1.png",
            "baby_swim_0.png", "baby_swim_1.png",
            "baby_halloween_idle_0.png", "baby_halloween_idle_1.png",
            "baby_halloween_swim_0.png", "baby_halloween_swim_1.png"
        ]
        
        for expected in expected_files:
            assert expected in files, f"Missing expected file: {expected}"
    
    def test_process_sheet_ignores_extra_rows(self, processor, sprite_sheet, temp_dir):
        """Test that rows beyond row_actions length are ignored - Requirement 32.6."""
        input_path = os.path.join(temp_dir, "adult_idle.png")
        sprite_sheet.save(input_path)
        
        # Only define 1 action for 2-row sprite sheet
        processor.process_sheet(
            input_path,
            rows=2, cols=2,
            row_actions=["idle"]  # Only first row
        )
        
        files = os.listdir(temp_dir)
        png_files = [f for f in files if f.endswith('.png') and f != "adult_idle.png"]
        
        # Should only create files for first row: 2 normal + 2 halloween = 4
        assert len(png_files) == 4, f"Expected 4 files (row 2 ignored), got {len(png_files)}"
        
        # Verify no "swim" files were created (second row action)
        swim_files = [f for f in png_files if 'swim' in f]
        assert len(swim_files) == 0, "Second row should be ignored"
    
    def test_process_sheet_single_image(self, processor, temp_dir):
        """Test processing single image (not sprite sheet) - Requirement 32.8."""
        # Create single image
        img = Image.new('RGBA', (100, 100), (255, 0, 0, 255))
        input_path = os.path.join(temp_dir, "default_icon.png")
        img.save(input_path)
        
        processor.process_sheet(
            input_path,
            rows=1, cols=1,
            row_actions=["icon"],
            is_single=True
        )
        
        files = os.listdir(temp_dir)
        
        # Should create normal + halloween versions
        assert "default_icon.png" in files  # Original
        assert "default_icon_halloween.png" in files  # Halloween version
    
    def test_process_sheet_handles_missing_file(self, processor, temp_dir, capsys):
        """Test that missing files are handled gracefully."""
        non_existent = os.path.join(temp_dir, "does_not_exist.png")
        
        # Should not raise exception
        processor.process_sheet(
            non_existent,
            rows=2, cols=2,
            row_actions=["idle"]
        )
        
        # Should print warning
        captured = capsys.readouterr()
        assert "not found" in captured.out.lower() or "warning" in captured.out.lower()
    
    def test_process_sheet_frame_dimensions(self, processor, sprite_sheet, temp_dir):
        """Test that sliced frames have correct dimensions."""
        input_path = os.path.join(temp_dir, "baby_idle.png")
        sprite_sheet.save(input_path)  # 200x200 image
        
        processor.process_sheet(
            input_path,
            rows=2, cols=2,
            row_actions=["idle", "swim"]
        )
        
        # Each frame should be 100x100 (200/2 x 200/2)
        frame_path = os.path.join(temp_dir, "baby_idle_0.png")
        frame = Image.open(frame_path)
        
        assert frame.size == (100, 100), f"Expected (100, 100), got {frame.size}"


class TestExtractPrefix(TestAssetProcessor):
    """Tests for prefix extraction from filenames."""
    
    def test_extract_prefix_baby(self, processor):
        """Test extracting 'baby' prefix."""
        assert processor._extract_prefix("baby_idle.png") == "baby"
        assert processor._extract_prefix("/path/to/baby_action.png") == "baby"
    
    def test_extract_prefix_adult(self, processor):
        """Test extracting 'adult' prefix."""
        assert processor._extract_prefix("adult_idle.png") == "adult"
        assert processor._extract_prefix("/path/to/adult_angry.png") == "adult"
    
    def test_extract_prefix_default(self, processor):
        """Test extracting 'default' prefix."""
        assert processor._extract_prefix("default_icon.png") == "default"
    
    def test_extract_prefix_fallback(self, processor):
        """Test fallback to first part before underscore."""
        assert processor._extract_prefix("custom_sprite.png") == "custom"
        assert processor._extract_prefix("test_image_file.png") == "test"
