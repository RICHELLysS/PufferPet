"""
创建万圣节主题占位符图像

此脚本为关键宠物创建万圣节主题和愤怒状态的占位符图像。
这些图像是可选的 - 如果不存在，系统会使用幽灵滤镜回退机制。

WARNING: Summoning the spirits of Halloween...
"""
import os
from PIL import Image, ImageDraw, ImageFilter

# 万圣节主题颜色
HALLOWEEN_COLORS = {
    'puffer': (255, 140, 0),      # 南瓜橙
    'jelly': (148, 0, 211),       # 幽灵紫
    'starfish': (255, 69, 0),     # 血红色
    'crab': (139, 0, 0),          # 暗红色
}

# 愤怒状态颜色（更深、更暗的颜色）
ANGRY_COLORS = {
    'puffer': (200, 50, 50),      # 愤怒红
    'jelly': (100, 0, 150),       # 暗紫色
    'starfish': (180, 30, 30),    # 深红色
    'crab': (100, 0, 0),          # 极暗红
}


def create_halloween_placeholder(pet_id: str, size: tuple = (100, 100)) -> Image.Image:
    """创建万圣节主题占位符图像"""
    color = HALLOWEEN_COLORS.get(pet_id, (255, 140, 0))
    
    # 创建基础图像
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制带有万圣节风格的形状
    # 主体
    draw.ellipse([10, 10, size[0]-10, size[1]-10], fill=color + (200,))
    
    # 添加"幽灵"眼睛
    eye_color = (0, 255, 0, 255)  # 绿色发光眼睛
    draw.ellipse([25, 30, 40, 45], fill=eye_color)
    draw.ellipse([60, 30, 75, 45], fill=eye_color)
    
    # 添加嘴巴（锯齿状）
    mouth_points = [(30, 60), (40, 70), (50, 60), (60, 70), (70, 60)]
    draw.line(mouth_points, fill=(0, 0, 0, 255), width=3)
    
    return img


def create_angry_placeholder(pet_id: str, size: tuple = (100, 100)) -> Image.Image:
    """创建愤怒状态占位符图像"""
    color = ANGRY_COLORS.get(pet_id, (200, 50, 50))
    
    # 创建基础图像
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制愤怒的形状
    # 主体（略微变形表示愤怒）
    draw.ellipse([5, 15, size[0]-5, size[1]-5], fill=color + (230,))
    
    # 愤怒的眼睛（斜线眉毛）
    eye_color = (255, 0, 0, 255)  # 红色愤怒眼睛
    draw.ellipse([25, 35, 40, 50], fill=eye_color)
    draw.ellipse([60, 35, 75, 50], fill=eye_color)
    
    # 愤怒的眉毛
    draw.line([(20, 25), (45, 35)], fill=(0, 0, 0, 255), width=3)
    draw.line([(80, 25), (55, 35)], fill=(0, 0, 0, 255), width=3)
    
    # 愤怒的嘴巴
    draw.arc([30, 55, 70, 80], 0, 180, fill=(0, 0, 0, 255), width=3)
    
    return img


def main():
    """主函数 - 创建所有占位符图像"""
    print("🎃 开始创建万圣节主题占位符图像...")
    
    # 关键宠物列表（只为几个关键宠物创建）
    key_pets = ['puffer', 'jelly']
    
    for pet_id in key_pets:
        pet_dir = f"assets/{pet_id}"
        
        # 确保目录存在
        if not os.path.exists(pet_dir):
            print(f"⚠️ 目录不存在: {pet_dir}")
            continue
        
        # 创建万圣节图像
        halloween_path = os.path.join(pet_dir, "halloween_idle.png")
        if not os.path.exists(halloween_path):
            halloween_img = create_halloween_placeholder(pet_id)
            halloween_img.save(halloween_path)
            print(f"✅ 创建万圣节图像: {halloween_path}")
        else:
            print(f"⏭️ 万圣节图像已存在: {halloween_path}")
        
        # 创建愤怒图像
        angry_path = os.path.join(pet_dir, "angry_idle.png")
        if not os.path.exists(angry_path):
            angry_img = create_angry_placeholder(pet_id)
            angry_img.save(angry_path)
            print(f"✅ 创建愤怒图像: {angry_path}")
        else:
            print(f"⏭️ 愤怒图像已存在: {angry_path}")
    
    print("\n🎃 万圣节主题图像创建完成！")
    print("注意：这些是占位符图像。如果图像不存在，系统会使用幽灵滤镜回退机制。")


if __name__ == "__main__":
    main()
