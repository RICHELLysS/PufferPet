# Implementation Plan

## V9 Asset Integration Tasks

- [x] 1. 重构 PetLoader 资源加载系统



  - [x] 1.1 创建 PetLoader 类，实现路径构建方法 `get_frame_path(pet_id, action, frame_index)`


    - 路径格式: `assets/{pet_id}/{action}/{pet_id}_{action}_{index}.png`
    - _Requirements: 1.1_

  - [x] 1.2 实现 `load_action_frames(pet_id, action)` 方法加载4帧序列
    - 加载 `_0.png` 到 `_3.png`
    - 失败时回退到 V7 几何占位符
    - _Requirements: 1.1, 1.9_
  - [x] 1.3 实现 `get_action_for_state(stage, is_moving)` 状态到动作映射
    - Stage 0 → baby_sleep
    - Stage 1 → baby_swim
    - Stage 2 + moving → swim
    - Stage 2 + idle → sleep
    - _Requirements: 1.2, 1.3, 1.4, 1.5_
  - [x] 1.4 Write property test for path construction


    - **Property 1: Path Construction Correctness**
    - **Validates: Requirements 1.1**
  - [x] 1.5 Write property test for stage to action mapping



    - **Property 2: Stage to Action Mapping**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5**

- [x] 2. 实现尺寸缩放系统





  - [x] 2.1 更新 `PetRenderer.calculate_size()` 方法


    - 幼年基准: 100px
    - 成年倍率: 1.5x (150px)
    - Ray 种族倍率: 额外 1.5x
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 2.2 实现 `scale_frame(pixmap, target_size)` 方法

    - 将 350x350px 原图缩放到目标尺寸
    - 保持宽高比
    - _Requirements: 2.1_

  - [x] 2.3 更新 `ui_inventory.py` 图标缩放逻辑

    - 将 1500x1500px default_icon 缩放到 64x64px
    - _Requirements: 2.5_

  - [x] 2.4 Write property test for size calculation

    - **Property 3: Size Calculation Correctness**
    - **Validates: Requirements 2.2, 2.3, 2.4**

- [x] 3. 实现序列帧动画系统





  - [x] 3.1 创建 FrameAnimator 类


    - 管理帧列表和当前帧索引
    - 实现 start/stop/reset 方法
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 3.2 集成 FrameAnimator 到 PetWidget

    - 替换静态图像为动画帧
    - 正常帧率 8fps，休眠帧率 4fps
    - _Requirements: 7.1, 7.4_

  - [x] 3.3 实现动画状态切换逻辑

    - 状态变化时重置帧计数器
    - 加载新动作的帧序列
    - _Requirements: 7.3_
  - [x] 3.4 Write property test for frame cycling


    - **Property 8: Frame Cycling**
    - **Validates: Requirements 7.1, 7.2, 7.3**

- [x] 4. Checkpoint - 确保基础动画系统测试通过





  - Ensure all tests pass, ask the user if questions arise.

- [x] 5. 实现 Stage 1 幼年期交互限制




  - [x] 5.1 修改 PetWidget.mousePressEvent() 阻止 Stage 1 点击

    - Stage 1 时忽略左键点击
    - 保留右键菜单功能
    - _Requirements: 3.3, 3.5_

  - [x] 5.2 修改 PetWidget.mouseMoveEvent() 阻止 Stage 1 拖拽
    - Stage 1 时忽略拖拽事件

    - _Requirements: 3.4_
  - [x] 5.3 确保 Stage 1 宠物使用 baby_swim 动画并可自主移动

    - _Requirements: 3.1, 3.2_

  - [x] 5.4 Write property test for baby interaction blocking


    - **Property 4: Baby Interaction Blocking**
    - **Validates: Requirements 3.3, 3.4, 3.5**

- [x] 6. 实现 Stage 2 成年期完全解锁




  - [x] 6.1 实现成年期动画切换逻辑


    - 移动时使用 swim 动画
    - 静止时使用 sleep 动画
    - _Requirements: 4.1, 4.2_

  - [x] 6.2 实现愤怒动画触发

    - 5次点击在2秒内触发 angry 动画
    - _Requirements: 4.3_

  - [x] 6.3 实现拖拽动画切换

    - 水平拖拽使用 drag_h
    - 垂直拖拽使用 drag_v
    - _Requirements: 4.4, 4.5_

- [x] 7. 实现拖拽翻转逻辑



  - [x] 7.1 创建 FlipTransform 工具类


    - `should_flip_horizontal(delta_x)`: delta_x < 0 时返回 True
    - `should_flip_vertical(delta_y)`: delta_y > 0 时返回 True
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 7.2 实现 `apply_horizontal_flip(pixmap)` 水平镜像
    - 使用 QImage.mirrored(True, False)

    - _Requirements: 5.2_
  - [x] 7.3 实现 `apply_vertical_flip(pixmap)` 垂直翻转
    - 使用 QImage.mirrored(False, True)
    - _Requirements: 5.4_
  - [x] 7.4 集成翻转逻辑到拖拽事件处理


    - 根据拖拽方向应用翻转
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [x] 7.5 Write property test for horizontal flip logic

    - **Property 5: Horizontal Flip Logic**
    - **Validates: Requirements 5.1, 5.2**

  - [x] 7.6 Write property test for vertical flip logic

    - **Property 6: Vertical Flip Logic**
    - **Validates: Requirements 5.3, 5.4**

- [x] 8. Checkpoint - 确保交互系统测试通过





  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. 实现夜间模式颜色滤镜





  - [x] 9.1 创建 NightFilter 类


    - 定义颜色分组: GREEN_GROUP = ['puffer', 'starfish'], PURPLE_GROUP = ['crab', 'jelly', 'ray']
    - 定义颜色: 绿色 #00FF88, 紫色 #8B00FF, 透明度 0.2
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 9.2 实现 `get_overlay_color(pet_id)` 方法
    - 根据 pet_id 返回对应颜色

    - _Requirements: 6.2, 6.3_
  - [x] 9.3 实现 `apply_filter(pixmap, pet_id)` 方法
    - 使用 QPainter CompositionMode 叠加颜色

    - _Requirements: 6.1_
  - [x] 9.4 集成夜间滤镜到 PetWidget.refresh_display()

    - 当 theme_mode == "halloween" 时应用滤镜
    - 对几何占位符也应用滤镜
    - _Requirements: 6.1, 6.4_
  - [x] 9.5 Write property test for night filter color selection


    - **Property 7: Night Filter Color Selection**
    - **Validates: Requirements 6.2, 6.3**

- [x] 10. 更新盲盒动画系统



  - [x] 10.1 修改 ui_gacha.py 加载盲盒序列帧


    - 路径: `assets/blindbox/box_{0-3}.png`
    - _Requirements: 8.1_

  - [x] 10.2 实现盲盒帧动画播放
    - 抖动阶段循环播放 box_0 到 box_3

    - _Requirements: 8.2_
  - [x] 10.3 实现盲盒资源回退

    - 加载失败时使用现有占位符
    - _Requirements: 8.3_

- [x] 11. 更新背景加载逻辑






  - [x] 11.1 修改 ocean_background.py 加载新背景

    - 白天: `assets/environment/seabed_day.png`
    - 夜晚: `assets/environment/seabed_night.png`
    - _Requirements: 1.8_

- [x] 12. 实现占位符回退机制





  - [x] 12.1 确保所有加载失败场景回退到 V7 几何占位符


    - 检测空文件 (0 bytes)
    - 检测无效图像 (isNull)
    - _Requirements: 1.9_

  - [x] 12.2 Write property test for fallback to placeholder

    - **Property 9: Fallback to Placeholder**
    - **Validates: Requirements 1.9, 6.4**

- [x] 13. Final Checkpoint - 确保所有测试通过





  - Ensure all tests pass, ask the user if questions arise.
