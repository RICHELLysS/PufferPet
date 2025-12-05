# V6 稳定版需求文档

## 简介

PufferPet V6 是一个精简、稳定的桌面宠物应用。核心玩法是"休眠-复活-成长"三阶段生命周期。移除所有复杂的奇遇概率、自动切片脚本和20只上限逻辑，专注于稳定性和核心体验。

## 术语表

- **PufferPet应用**: 桌面宠物应用程序主系统
- **宠物状态 (state)**: 宠物当前生命阶段 (0=休眠, 1=幼年, 2=成年)
- **任务进度 (tasks_progress)**: 当前周期内完成的任务数量
- **休眠滤镜**: 灰度 + 60%透明度的视觉效果
- **昼夜模式**: 根据时间自动切换的主题模式

## 需求

### 需求 1: 三阶段生命周期

**用户故事:** 作为用户，我希望宠物有清晰的成长阶段，以便获得培养的成就感。

#### 验收标准

1. WHEN 宠物状态为0（休眠）THEN PufferPet应用 SHALL 将宠物固定在屏幕底部
2. WHEN 宠物状态为0 THEN PufferPet应用 SHALL 对 baby_idle 图像应用休眠滤镜（灰度+60%透明度）
3. WHEN 宠物状态为0 THEN PufferPet应用 SHALL 禁止拖拽和普通点击交互
4. WHEN 用户右键点击休眠宠物 THEN PufferPet应用 SHALL 显示任务设置窗口
5. WHEN 用户完成1个任务且状态为0 THEN PufferPet应用 SHALL 将状态切换为1（幼年）
6. WHEN 宠物状态为1 THEN PufferPet应用 SHALL 移除滤镜并播放 baby_idle 动画
7. WHEN 宠物状态为1 THEN PufferPet应用 SHALL 允许自由游动和拖拽交互
8. WHEN 用户累计完成3个任务且状态为1 THEN PufferPet应用 SHALL 将状态切换为2（成年）
9. WHEN 宠物状态为2 THEN PufferPet应用 SHALL 加载 adult_idle 图像

### 需求 2: 任务与周期系统

**用户故事:** 作为用户，我希望通过完成任务来唤醒和培养宠物。

#### 验收标准

1. WHEN 任务窗口显示 THEN 窗口 SHALL 显示当前进度（格式：X/3）
2. WHEN 用户勾选任务 THEN PufferPet应用 SHALL 增加 tasks_progress 计数
3. WHEN tasks_progress 从0变为1 THEN PufferPet应用 SHALL 触发宠物从休眠到幼年的进化
4. WHEN tasks_progress 达到3 THEN PufferPet应用 SHALL 触发宠物从幼年到成年的进化
5. WHEN 用户设置周期重置 THEN PufferPet应用 SHALL 将 tasks_progress 重置为0并将状态重置为0

### 需求 3: 资产管理与容错

**用户故事:** 作为用户，我希望应用在任何情况下都不会崩溃。

#### 验收标准

1. WHEN 加载宠物图像 THEN PufferPet应用 SHALL 首先尝试加载 .gif 文件
2. WHEN .gif 不存在 THEN PufferPet应用 SHALL 尝试加载序列帧 _0.png
3. WHEN 序列帧不存在 THEN PufferPet应用 SHALL 尝试加载单张 .png
4. WHEN 所有图像都不存在 THEN PufferPet应用 SHALL 绘制带宠物名称的彩色椭圆占位符
5. WHEN 发生任何异常 THEN PufferPet应用 SHALL 捕获异常并继续运行

### 需求 4: 昼夜模式（保留功能）

**用户故事:** 作为用户，我希望应用能根据时间自动切换视觉主题。

#### 验收标准

1. WHEN 系统时间在06:00-18:00 THEN PufferPet应用 SHALL 使用白天主题
2. WHEN 系统时间在18:00-06:00 THEN PufferPet应用 SHALL 使用黑夜主题
3. WHEN 黑夜主题激活 THEN 背景 SHALL 应用深色滤镜效果
