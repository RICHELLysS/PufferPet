"""
tools/cleanup_assets.py - V7 资产清理脚本

执行以下操作：
1. 迁移 assets/deep_sea/ray -> assets/ray
2. 删除 assets/deep_sea 整个文件夹
3. 删除不在保留列表中的生物文件夹
4. 为保留的宠物创建标准占位符文件
"""

import os
import shutil
from pathlib import Path

# 保留列表
KEEP_FOLDERS = {'puffer', 'jelly', 'crab', 'starfish', 'ray', 'blindbox', 'environment', 'fonts'}

# 宠物列表（需要创建占位符的）
PET_FOLDERS = ['puffer', 'jelly', 'crab', 'starfish', 'ray']

# 标准占位符文件
PLACEHOLDER_FILES = [
    'baby_idle.png',
    'baby_action.png', 
    'adult_idle.png',
    'adult_action.png',
    'adult_angry.png',
    'default_icon.png'
]

def main():
    assets_dir = Path('assets')
    deep_sea_dir = assets_dir / 'deep_sea'
    
    print("=" * 50)
    print("  PufferPet V7 资产清理脚本")
    print("=" * 50)
    print()
    
    # 统计
    moved = []
    deleted = []
    created = []
    
    # 1. 迁移鳐鱼 (ray)
    print("[1] 迁移鳐鱼 (ray)...")
    ray_src = deep_sea_dir / 'ray'
    ray_dst = assets_dir / 'ray'
    
    if ray_src.exists():
        if ray_dst.exists():
            print(f"    ⚠️  目标已存在: {ray_dst}")
            # 合并内容
            for item in ray_src.iterdir():
                dst_item = ray_dst / item.name
                if not dst_item.exists():
                    shutil.move(str(item), str(dst_item))
                    moved.append(f"{item} -> {dst_item}")
            shutil.rmtree(ray_src)
        else:
            shutil.move(str(ray_src), str(ray_dst))
            moved.append(f"{ray_src} -> {ray_dst}")
        print(f"    ✅ 已迁移: {ray_src} -> {ray_dst}")
    else:
        print(f"    ⏭️  源不存在: {ray_src}")
    
    print()
    
    # 2. 删除 deep_sea 文件夹
    print("[2] 删除 deep_sea 文件夹...")
    if deep_sea_dir.exists():
        # 列出将被删除的内容
        for item in deep_sea_dir.iterdir():
            print(f"    🗑️  删除: {item}")
            deleted.append(str(item))
        shutil.rmtree(deep_sea_dir)
        deleted.append(str(deep_sea_dir))
        print(f"    ✅ 已删除: {deep_sea_dir}")
    else:
        print(f"    ⏭️  不存在: {deep_sea_dir}")
    
    print()
    
    # 3. 删除不在保留列表中的文件夹
    print("[3] 清理多余生物文件夹...")
    if assets_dir.exists():
        for item in assets_dir.iterdir():
            if item.is_dir() and item.name not in KEEP_FOLDERS:
                print(f"    🗑️  删除: {item}")
                shutil.rmtree(item)
                deleted.append(str(item))
    print("    ✅ 清理完成")
    
    print()
    
    # 4. 创建标准占位符文件
    print("[4] 创建标准占位符文件...")
    for pet in PET_FOLDERS:
        pet_dir = assets_dir / pet
        
        # 确保文件夹存在
        if not pet_dir.exists():
            pet_dir.mkdir(parents=True)
            print(f"    📁 创建文件夹: {pet_dir}")
        
        # 创建占位符文件
        for filename in PLACEHOLDER_FILES:
            filepath = pet_dir / filename
            if not filepath.exists():
                filepath.touch()  # 创建空文件
                created.append(str(filepath))
                print(f"    📄 创建: {filepath}")
    
    print()
    
    # 5. 汇报结果
    print("=" * 50)
    print("  清理结果汇总")
    print("=" * 50)
    print(f"  迁移文件/夹: {len(moved)}")
    print(f"  删除文件/夹: {len(deleted)}")
    print(f"  创建占位符:  {len(created)}")
    print()
    
    # 显示最终目录结构
    print("[最终目录结构]")
    if assets_dir.exists():
        for item in sorted(assets_dir.iterdir()):
            if item.is_dir():
                file_count = len(list(item.iterdir()))
                print(f"  📁 {item.name}/ ({file_count} 个文件)")
    
    print()
    print("✅ 清理完成!")

if __name__ == "__main__":
    main()
