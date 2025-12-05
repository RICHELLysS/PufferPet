"""
tools/cleanup_assets.py - V7 Asset Cleanup Script

Performs the following operations:
1. Migrate assets/deep_sea/ray -> assets/ray
2. Delete entire assets/deep_sea folder
3. Delete creature folders not in the keep list
4. Create standard placeholder files for retained pets
"""

import os
import shutil
from pathlib import Path

# Keep list - folders to retain
KEEP_FOLDERS = {'puffer', 'jelly', 'crab', 'starfish', 'ray', 'blindbox', 'environment', 'fonts'}

# Pet list - folders that need placeholder files
PET_FOLDERS = ['puffer', 'jelly', 'crab', 'starfish', 'ray']

# Standard placeholder files
# Note: default_icon uses [pet_id]_default_icon.png naming convention
PLACEHOLDER_FILES = [
    'baby_idle.png',
    'baby_action.png', 
    'adult_idle.png',
    'adult_action.png',
    'adult_angry.png',
    # default_icon is now [pet_id]_default_icon.png, handled separately
]

def main():
    assets_dir = Path('assets')
    deep_sea_dir = assets_dir / 'deep_sea'
    
    print("=" * 50)
    print("  PufferPet V7 Asset Cleanup Script")
    print("=" * 50)
    print()
    
    # Statistics
    moved = []
    deleted = []
    created = []
    
    # 1. Migrate ray
    print("[1] Migrating ray...")
    ray_src = deep_sea_dir / 'ray'
    ray_dst = assets_dir / 'ray'
    
    if ray_src.exists():
        if ray_dst.exists():
            print(f"    ⚠️  Target exists: {ray_dst}")
            # Merge contents
            for item in ray_src.iterdir():
                dst_item = ray_dst / item.name
                if not dst_item.exists():
                    shutil.move(str(item), str(dst_item))
                    moved.append(f"{item} -> {dst_item}")
            shutil.rmtree(ray_src)
        else:
            shutil.move(str(ray_src), str(ray_dst))
            moved.append(f"{ray_src} -> {ray_dst}")
        print(f"    ✅ Migrated: {ray_src} -> {ray_dst}")
    else:
        print(f"    ⏭️  Source not found: {ray_src}")
    
    print()
    
    # 2. Delete deep_sea folder
    print("[2] Deleting deep_sea folder...")
    if deep_sea_dir.exists():
        # List items to be deleted
        for item in deep_sea_dir.iterdir():
            print(f"    🗑️  Deleting: {item}")
            deleted.append(str(item))
        shutil.rmtree(deep_sea_dir)
        deleted.append(str(deep_sea_dir))
        print(f"    ✅ Deleted: {deep_sea_dir}")
    else:
        print(f"    ⏭️  Not found: {deep_sea_dir}")
    
    print()
    
    # 3. Delete folders not in keep list
    print("[3] Cleaning up extra creature folders...")
    if assets_dir.exists():
        for item in assets_dir.iterdir():
            if item.is_dir() and item.name not in KEEP_FOLDERS:
                print(f"    🗑️  Deleting: {item}")
                shutil.rmtree(item)
                deleted.append(str(item))
    print("    ✅ Cleanup complete")
    
    print()
    
    # 4. Create standard placeholder files
    print("[4] Creating standard placeholder files...")
    for pet in PET_FOLDERS:
        pet_dir = assets_dir / pet
        
        # Ensure folder exists
        if not pet_dir.exists():
            pet_dir.mkdir(parents=True)
            print(f"    📁 Created folder: {pet_dir}")
        
        # Create placeholder files
        for filename in PLACEHOLDER_FILES:
            filepath = pet_dir / filename
            if not filepath.exists():
                filepath.touch()  # Create empty file
                created.append(str(filepath))
                print(f"    📄 Created: {filepath}")
        
        # Create pet-specific default_icon with new naming convention
        default_icon_path = pet_dir / f"{pet}_default_icon.png"
        if not default_icon_path.exists():
            default_icon_path.touch()
            created.append(str(default_icon_path))
            print(f"    📄 Created: {default_icon_path}")
    
    print()
    
    # 5. Report results
    print("=" * 50)
    print("  Cleanup Results Summary")
    print("=" * 50)
    print(f"  Files/folders moved: {len(moved)}")
    print(f"  Files/folders deleted: {len(deleted)}")
    print(f"  Placeholders created: {len(created)}")
    print()
    
    # Display final directory structure
    print("[Final Directory Structure]")
    if assets_dir.exists():
        for item in sorted(assets_dir.iterdir()):
            if item.is_dir():
                file_count = len(list(item.iterdir()))
                print(f"  📁 {item.name}/ ({file_count} files)")
    
    print()
    print("✅ Cleanup complete!")

if __name__ == "__main__":
    main()
