# 设计文档

## 概述

PufferPet 是一个使用 Python 和 PyQt6 构建的桌面宠物应用程序。应用程序采用模块化架构，将 UI 渲染、数据管理和业务逻辑分离。核心组件包括透明的宠物窗口、任务管理窗口、宠物选择窗口、奇遇管理器和持久化数据管理器。

**V2 版本更新**: 支持多宠物系统，用户可以收集和切换不同的宠物（河豚和水母）。每个宠物有独立的成长进度，水母需要通过将河豚升级到等级 3 来解锁。

**V3 版本更新**: 扩展到8种海洋生物，分为两个层级（Tier 1基础宠物和Tier 2稀有宠物）。引入奇遇系统，稀有生物会随机出现在屏幕上，用户可以点击捕获它们。所有图像资源重组到 `assets/[pet_id]/` 目录结构。

## 架构

应用程序采用 MVC（模型-视图-控制器）变体架构：

- **模型层**: `DataManager` 类负责数据持久化和业务逻辑
- **视图层**: `PufferWidget` 和 `TaskWindow` 类负责 UI 渲染
- **控制器层**: 主应用程序协调视图和模型之间的交互

```
┌─────────────────────────────────────┐
│         main.py (Entry Point)       │
└──────────────┬──────────────────────┘
               │
               ├──────────────────────────┐
               ▼                          ▼
┌─────────────────────────────┐  ┌──────────────────┐
│   PetWidget (Main Window)   │  │ EncounterManager │
│  - 透明无边框窗口            │  │  - 定时触发      │
│  - 显示当前宠物图像          │  │  - 概率判定      │
│  - 处理右键菜单              │  │  - 访客生成      │
└──────────┬──────────────────┘  └────────┬─────────┘
           │                              │
           ├──────────┬──────────┬────────┼─────────┐
           ▼          ▼          ▼        ▼         ▼
┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐
│TaskWindow  │ │DataManager │ │PetSelector │ │VisitorWin  │
│- 任务清单  │ │- JSON读写  │ │- 宠物列表  │ │- 稀有生物  │
│- 进度显示  │ │- 8种生物   │ │- 层级分组  │ │- 横向移动  │
│- 复选框    │ │- 层级管理  │ │- 解锁状态  │ │- 捕获交互  │
└────────────┘ │- 奇遇资格  │ └────────────┘ └────────────┘
               └────────────┘
```

## 组件和接口

### 1. DataManager 类

负责所有数据持久化和业务逻辑操作。

**属性:**
- `data_file: str` - data.json 文件路径
- `data: dict` - 内存中的数据结构

**方法:**
- `__init__(data_file: str = "data.json")` - 初始化并加载数据
- `load_data() -> dict` - 从文件加载数据，处理错误情况和数据迁移
- `save_data() -> None` - 将数据保存到文件
- `migrate_old_data(old_data: dict) -> dict` - 将旧版数据迁移到新格式
- `check_and_reset_daily() -> None` - 检查日期并重置所有宠物的每日任务
- `get_current_pet_id() -> str` - 获取当前显示的宠物ID
- `set_current_pet_id(pet_id: str) -> None` - 设置当前显示的宠物ID
- `get_unlocked_pets() -> List[str]` - 获取已解锁的宠物列表
- `is_pet_unlocked(pet_id: str) -> bool` - 检查宠物是否已解锁
- `unlock_pet(pet_id: str) -> None` - 解锁新宠物
- `get_level(pet_id: str = None) -> int` - 获取指定宠物的等级（默认当前宠物）
- `get_tasks_completed(pet_id: str = None) -> int` - 获取指定宠物的今日完成任务数
- `increment_task(pet_id: str = None) -> bool` - 增加任务完成数并检查升级，返回是否解锁新宠物
- `decrement_task(pet_id: str = None) -> None` - 减少任务完成数
- `get_image_for_level(pet_id: str, level: int) -> str` - 根据宠物ID和等级返回图像文件名
- `get_unlock_condition(pet_id: str) -> str` - 获取宠物的解锁条件描述

### 2. PetWidget 类

主窗口，显示当前选中的宠物。

**继承:** `QWidget`

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `current_pixmap: QPixmap` - 当前显示的图像
- `task_window: TaskWindow` - 任务窗口引用
- `pet_selector_window: PetSelectorWindow` - 宠物选择窗口引用

**方法:**
- `__init__(data_manager: DataManager)` - 初始化窗口
- `setup_window() -> None` - 配置窗口属性（无边框、透明、置顶）
- `load_image() -> None` - 加载当前宠物和等级对应的图像
- `paintEvent(event: QPaintEvent) -> None` - 绘制宠物图像
- `contextMenuEvent(event: QContextMenuEvent) -> None` - 处理右键点击，显示菜单
- `show_task_window() -> None` - 显示任务窗口
- `show_pet_selector() -> None` - 显示宠物选择窗口
- `switch_pet(pet_id: str) -> None` - 切换到指定宠物
- `update_display() -> None` - 更新显示的图像
- `show_unlock_notification(pet_id: str) -> None` - 显示宠物解锁通知

### 3. TaskWindow 类

任务管理窗口。

**继承:** `QDialog`

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `pet_widget: PetWidget` - 主窗口引用
- `checkboxes: List[QCheckBox]` - 任务复选框列表
- `progress_label: QLabel` - 进度显示标签

**方法:**
- `__init__(data_manager: DataManager, pet_widget: PetWidget)` - 初始化窗口
- `setup_ui() -> None` - 创建 UI 元素
- `update_progress() -> None` - 更新进度显示
- `on_checkbox_changed(state: int, index: int) -> None` - 处理复选框状态变化
- `closeEvent(event: QCloseEvent) -> None` - 保存数据并关闭

### 4. PetSelectorWindow 类

宠物选择窗口，允许用户切换宠物。

**继承:** `QDialog`

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `pet_widget: PetWidget` - 主窗口引用
- `pet_buttons: Dict[str, QPushButton]` - 宠物按钮字典

**方法:**
- `__init__(data_manager: DataManager, pet_widget: PetWidget)` - 初始化窗口
- `setup_ui() -> None` - 创建 UI 元素
- `create_pet_button(pet_id: str) -> QWidget` - 创建单个宠物的按钮/卡片
- `on_pet_selected(pet_id: str) -> None` - 处理宠物选择
- `update_display() -> None` - 更新按钮状态（高亮当前宠物）

### 5. EncounterManager 类（V3新增）

奇遇管理器，负责触发和管理稀有生物的出现。

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `pet_widget: PetWidget` - 主窗口引用
- `timer: QTimer` - 定时器，每5分钟触发一次判定
- `visitor_window: VisitorWindow` - 当前显示的访客窗口引用
- `encounter_probability: float` - 奇遇触发概率（默认0.3）

**方法:**
- `__init__(data_manager: DataManager, pet_widget: PetWidget)` - 初始化管理器
- `start() -> None` - 启动定时器
- `stop() -> None` - 停止定时器
- `check_encounter_eligibility() -> bool` - 检查用户是否有资格触发奇遇
- `try_trigger_encounter() -> None` - 尝试触发奇遇事件
- `get_available_rare_pets() -> List[str]` - 获取未解锁的Tier 2宠物列表
- `spawn_visitor(pet_id: str) -> None` - 生成访客窗口显示稀有生物
- `on_visitor_captured(pet_id: str) -> None` - 处理访客被捕获的回调

### 6. VisitorWindow 类（V3新增）

访客窗口，显示路过的稀有生物。

**继承:** `QWidget`

**属性:**
- `pet_id: str` - 稀有生物的ID
- `data_manager: DataManager` - 数据管理器实例
- `encounter_manager: EncounterManager` - 奇遇管理器引用
- `current_pixmap: QPixmap` - 当前显示的图像
- `animation_timer: QTimer` - 动画定时器
- `start_x: int` - 起始X坐标（屏幕左侧外）
- `end_x: int` - 结束X坐标（屏幕右侧外）
- `current_x: int` - 当前X坐标
- `move_speed: float` - 移动速度（像素/帧）

**方法:**
- `__init__(pet_id: str, data_manager: DataManager, encounter_manager: EncounterManager)` - 初始化窗口
- `setup_window() -> None` - 配置窗口属性（无边框、透明、置顶）
- `load_image() -> None` - 加载稀有生物的adult_idle.png图像
- `start_animation() -> None` - 开始横向移动动画
- `update_position() -> None` - 更新窗口位置
- `mousePressEvent(event: QMouseEvent) -> None` - 处理点击捕获
- `on_captured() -> None` - 处理被捕获事件
- `paintEvent(event: QPaintEvent) -> None` - 绘制生物图像

## 数据模型

### V1 data.json 结构（旧版，需迁移）

```json
{
  "level": 1,
  "tasks_completed_today": 0,
  "last_login_date": "2024-12-02",
  "task_states": [false, false, false]
}
```

### V2 data.json 结构（旧版，需迁移到V3）

```json
{
  "version": 2,
  "current_pet_id": "puffer",
  "unlocked_pets": ["puffer"],
  "pets_data": {
    "puffer": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    },
    "jelly": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    }
  }
}
```

### V3 data.json 结构（最新版）

```json
{
  "version": 3,
  "current_pet_id": "puffer",
  "unlocked_pets": ["puffer", "jelly", "starfish", "crab"],
  "pet_tiers": {
    "tier1": ["puffer", "jelly", "starfish", "crab"],
    "tier2": ["octopus", "ribbon", "sunfish", "angler"]
  },
  "pets_data": {
    "puffer": {
      "level": 3,
      "tasks_completed_today": 3,
      "last_login_date": "2024-12-02",
      "task_states": [true, true, true]
    },
    "jelly": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    },
    "starfish": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    },
    "crab": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    },
    "octopus": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    },
    "ribbon": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    },
    "sunfish": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    },
    "angler": {
      "level": 1,
      "tasks_completed_today": 0,
      "last_login_date": "2024-12-02",
      "task_states": [false, false, false]
    }
  },
  "encounter_settings": {
    "check_interval_minutes": 5,
    "trigger_probability": 0.3,
    "last_encounter_check": "2024-12-02T14:30:00"
  }
}
```

**字段说明:**
- `version`: 数据格式版本号（3）
- `current_pet_id`: 当前显示的宠物ID
- `unlocked_pets`: 已解锁的宠物ID列表（包含Tier 1和已捕获的Tier 2）
- `pet_tiers`: 宠物层级定义
  - `tier1`: Tier 1宠物列表（基础宠物，默认可解锁）
  - `tier2`: Tier 2宠物列表（稀有宠物，需通过奇遇捕获）
- `pets_data`: 所有8种宠物的独立数据字典
  - `level`: 宠物等级（1-3）
  - `tasks_completed_today`: 今日完成的任务数（0-3）
  - `last_login_date`: 最后登录日期（ISO 格式）
  - `task_states`: 三个任务的完成状态数组
- `encounter_settings`: 奇遇系统配置
  - `check_interval_minutes`: 奇遇检查间隔（分钟）
  - `trigger_probability`: 奇遇触发概率（0.0-1.0）
  - `last_encounter_check`: 上次奇遇检查时间（ISO 格式）

### 数据迁移逻辑（V2→V3）

当检测到V2版本数据格式时：
1. 保留现有的 `current_pet_id` 和 `unlocked_pets`
2. 添加新的Tier 1宠物（starfish, crab）到 `unlocked_pets`
3. 创建 `pet_tiers` 字段定义层级
4. 为所有8种宠物创建 `pets_data` 条目（保留已有数据）
5. 添加 `encounter_settings` 字段
6. 更新 `version` 为 3
7. 备份旧文件为 `data.json.v2.backup`

### V3 宠物配置

**Tier 1 宠物（基础宠物）:**

1. **河豚 (Puffer)**
   - ID: "puffer"
   - 解锁条件: 默认解锁
   - 图像文件:
     - Level 1: `assets/puffer/baby_idle.png`
     - Level 2-3: `assets/puffer/adult_idle.png`

2. **水母 (Jelly)**
   - ID: "jelly"
   - 解锁条件: 默认解锁（V3中）
   - 图像文件:
     - Level 1: `assets/jelly/baby_idle.png`
     - Level 2-3: `assets/jelly/adult_idle.png`

3. **海星 (Starfish)**
   - ID: "starfish"
   - 解锁条件: 默认解锁
   - 图像文件:
     - Level 1: `assets/starfish/baby_idle.png`
     - Level 2-3: `assets/starfish/adult_idle.png`

4. **螃蟹 (Crab)**
   - ID: "crab"
   - 解锁条件: 默认解锁
   - 图像文件:
     - Level 1: `assets/crab/baby_idle.png`
     - Level 2-3: `assets/crab/adult_idle.png`

**Tier 2 宠物（稀有宠物）:**

5. **八爪鱼 (Octopus)**
   - ID: "octopus"
   - 解锁条件: 通过奇遇捕获
   - 图像文件:
     - Level 1: `assets/octopus/baby_idle.png`
     - Level 2-3: `assets/octopus/adult_idle.png`
   - 访客图像: `assets/octopus/adult_idle.png`

6. **带鱼 (Ribbon)**
   - ID: "ribbon"
   - 解锁条件: 通过奇遇捕获
   - 图像文件:
     - Level 1: `assets/ribbon/baby_idle.png`
     - Level 2-3: `assets/ribbon/adult_idle.png`
   - 访客图像: `assets/ribbon/adult_idle.png`

7. **翻车鱼 (Sunfish)**
   - ID: "sunfish"
   - 解锁条件: 通过奇遇捕获
   - 图像文件:
     - Level 1: `assets/sunfish/baby_idle.png`
     - Level 2-3: `assets/sunfish/adult_idle.png`
   - 访客图像: `assets/sunfish/adult_idle.png`

8. **灯笼鱼 (Angler)**
   - ID: "angler"
   - 解锁条件: 通过奇遇捕获
   - 图像文件:
     - Level 1: `assets/angler/baby_idle.png`
     - Level 2-3: `assets/angler/adult_idle.png`
   - 访客图像: `assets/angler/adult_idle.png`

### 图像文件结构（V3）

V3版本采用新的目录结构，每个宠物有独立的文件夹：

```
assets/
├── puffer/
│   ├── baby_idle.png
│   └── adult_idle.png
├── jelly/
│   ├── baby_idle.png
│   └── adult_idle.png
├── starfish/
│   ├── baby_idle.png
│   └── adult_idle.png
├── crab/
│   ├── baby_idle.png
│   └── adult_idle.png
├── octopus/
│   ├── baby_idle.png
│   └── adult_idle.png
├── ribbon/
│   ├── baby_idle.png
│   └── adult_idle.png
├── sunfish/
│   ├── baby_idle.png
│   └── adult_idle.png
└── angler/
    ├── baby_idle.png
    └── adult_idle.png
```

**图像加载规则:**
- Level 1: 加载 `baby_idle.png`
- Level 2-3: 加载 `adult_idle.png`
- 访客窗口: 始终加载 `adult_idle.png`
- 缺失图像: 使用带颜色的方块占位符（每个宠物不同颜色）

### 数据迁移逻辑

当检测到旧版数据格式时：
1. 将旧数据映射到 `pets_data["puffer"]`
2. 设置 `current_pet_id` 为 "puffer"
3. 设置 `unlocked_pets` 为 ["puffer"]
4. 为水母创建默认数据（未解锁状态）
5. 添加 `version` 字段
6. 备份旧文件为 `data.json.v1.backup`

### 宠物配置

**河豚 (Puffer):**
- ID: "puffer"
- 解锁条件: 默认解锁
- 图像文件:
  - Level 1: `assets/puffer_stage1_idle.png`
  - Level 2: `assets/puffer_stage2_idle.png`
  - Level 3: `assets/puffer_stage3_idle.png`

**水母 (Jelly):**
- ID: "jelly"
- 解锁条件: 河豚达到等级 3
- 图像文件:
  - Level 1: `assets/jelly_stage1_idle.png`
  - Level 2: `assets/jelly_stage2_idle.png`
  - Level 3: `assets/jelly_stage3_idle.png`

### 图像文件命名（向后兼容）

为了向后兼容，保留旧的图像文件名作为河豚的别名：
- `assets/stage1_idle.png` → `assets/puffer_stage1_idle.png`
- `assets/stage2_idle.png` → `assets/puffer_stage2_idle.png`
- `assets/stage3_idle.png` → `assets/puffer_stage3_idle.png`

## 正确性属性

*属性是一个特征或行为，应该在系统的所有有效执行中保持为真——本质上是关于系统应该做什么的正式陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*


### 属性 1: 数据持久化往返一致性

*对于任意*有效的应用状态（等级、任务完成数、日期），将数据保存到文件然后重新加载应该产生等效的状态。

**验证: 需求 2.2, 2.8, 3.7**

### 属性 2: 日期变化重置任务

*对于任意*数据状态，如果最后登录日期与当前日期不同，则今日完成任务数应该被重置为零，且任务状态数组应该全部重置为 false。

**验证: 需求 2.3**

### 属性 3: 升级逻辑一致性

*对于任意*等级小于 3 的状态，当今日完成任务数达到 3 时，等级应该增加 1，并且显示的图像应该更新为新等级对应的图像。

**验证: 需求 2.4, 3.6**

### 属性 4: 等级到图像映射

*对于任意*有效等级（1、2 或 3），`get_image_for_level()` 方法应该返回对应的图像文件名（stage1_idle.png、stage2_idle.png 或 stage3_idle.png）。

**验证: 需求 2.5, 2.6, 2.7**

### 属性 5: 任务进度显示格式

*对于任意*今日完成任务数（0-3），任务窗口显示的进度文本应该符合 "X/3" 格式，其中 X 是当前完成数。

**验证: 需求 3.2**

### 属性 6: 任务状态与计数同步

*对于任意*任务状态配置，勾选的复选框数量应该始终等于 `tasks_completed_today` 的值。

**验证: 需求 3.4, 3.5**

## V2 版本新增正确性属性

### 属性 7: 宠物数据隔离

*对于任意*两个不同的宠物ID，修改一个宠物的数据（等级、任务完成数）不应该影响另一个宠物的数据。

**验证: 需求 5.7, 8.1, 8.2**

### 属性 8: 宠物切换往返一致性

*对于任意*宠物状态，从宠物A切换到宠物B再切换回宠物A，宠物A的数据应该保持不变。

**验证: 需求 5.6, 5.7, 8.3**

### 属性 9: 解锁条件一致性

*对于任意*应用状态，当河豚等级达到3时，水母应该被自动解锁并添加到 unlocked_pets 列表中，且在 pets_data 中创建初始数据。

**验证: 需求 6.1, 6.2, 6.3**

### 属性 10: 未解锁宠物访问控制

*对于任意*未解锁的宠物ID，尝试切换到该宠物应该被阻止，且 current_pet_id 应该保持不变。

**验证: 需求 6.6**

### 属性 11: 多宠物日期重置

*对于任意*包含多个宠物的应用状态，当日期变化时，所有宠物的 tasks_completed_today 和 task_states 都应该被重置。

**验证: 需求 8.4**

### 属性 12: 数据迁移正确性

*对于任意*有效的V1格式数据，迁移到V2格式后，河豚的数据应该与原始数据等效，且应该创建默认的水母数据。

**验证: 需求 5.8**

### 属性 13: 宠物图像映射扩展

*对于任意*有效的宠物ID（"puffer" 或 "jelly"）和等级（1-3），`get_image_for_level(pet_id, level)` 应该返回正确格式的图像文件名（{pet_id}_stage{level}_idle.png）。

**验证: 需求 5.5, 8.5, 8.6, 8.7**

## 错误处理

### 图像加载失败

当图像文件不存在或无法加载时：
1. 捕获 `FileNotFoundError` 或 `QPixmap` 加载失败
2. 创建一个红色方块的 `QPixmap` 作为占位符（50x50 像素）
3. 记录警告信息但不中断程序执行

### 数据文件错误

**文件不存在:**
- 创建默认的 data.json，包含初始值（level=1, tasks_completed_today=0）

**JSON 解析错误:**
- 捕获 `json.JSONDecodeError`
- 备份损坏的文件为 `data.json.backup`
- 创建新的默认数据文件

**写入权限错误:**
- 捕获 `PermissionError` 或 `IOError`
- 在内存中维护状态
- 向用户显示警告（可选）

### 异常处理策略

所有关键操作都应该包含 try-except 块：
- 文件 I/O 操作
- JSON 序列化/反序列化
- 图像加载
- UI 事件处理

## 测试策略

### 单元测试

使用 `pytest` 框架进行单元测试：

**DataManager 测试:**
- 测试默认数据创建
- 测试数据加载和保存
- 测试日期重置逻辑
- 测试等级升级逻辑
- 测试图像文件名映射

**UI 组件测试:**
- 测试窗口属性设置（无边框、透明、置顶）
- 测试任务窗口 UI 创建
- 测试进度标签更新

### 基于属性的测试

使用 `Hypothesis` 库进行基于属性的测试：

**测试配置:**
- 每个属性测试运行最少 100 次迭代
- 使用自定义策略生成有效的应用状态

**测试标签格式:**
每个基于属性的测试必须使用以下格式标记：
`**Feature: puffer-pet, Property {number}: {property_text}**`

**生成器策略:**
- `valid_level`: 生成 1-3 之间的整数
- `valid_tasks_count`: 生成 0-3 之间的整数
- `valid_date`: 生成有效的 ISO 格式日期字符串
- `valid_task_states`: 生成长度为 3 的布尔值列表
- `valid_app_state`: 生成完整的应用状态字典

**属性测试覆盖:**
1. 数据持久化往返测试（属性 1）
2. 日期重置测试（属性 2）
3. 升级逻辑测试（属性 3）
4. 等级映射测试（属性 4）
5. 进度显示测试（属性 5）
6. 任务同步测试（属性 6）
7. 宠物数据隔离测试（属性 7）- V2
8. 宠物切换往返测试（属性 8）- V2
9. 解锁条件测试（属性 9）- V2
10. 访问控制测试（属性 10）- V2
11. 多宠物日期重置测试（属性 11）- V2
12. 数据迁移测试（属性 12）- V2
13. 宠物图像映射测试（属性 13）- V2

**V2 版本生成器策略扩展:**
- `valid_pet_id`: 生成有效的宠物ID（"puffer" 或 "jelly"）
- `unlocked_pets_list`: 生成已解锁宠物列表的子集
- `multi_pet_state`: 生成包含多个宠物数据的完整V2状态
- `v1_data_state`: 生成V1格式的数据用于迁移测试

### 集成测试

测试组件之间的交互：
- 测试任务完成触发数据更新和 UI 刷新
- 测试应用启动流程（数据加载 → UI 初始化 → 图像显示）
- 测试右键菜单打开任务窗口的完整流程

### 边缘情况测试

通过生成器处理的边缘情况：
- 缺失图像文件（生成器包含无效路径）
- 损坏的 JSON 数据（生成器包含格式错误的 JSON）
- 空数据文件
- 等级边界值（0, 4 等无效值）
- 任务数边界值（-1, 4 等无效值）

## 技术栈

- **语言**: Python 3.8+
- **GUI 框架**: PyQt6
- **数据格式**: JSON
- **测试框架**: pytest
- **属性测试**: Hypothesis
- **代码风格**: PEP 8

## 依赖项

```
PyQt6>=6.4.0
pytest>=7.0.0
hypothesis>=6.0.0
```

## 项目结构

```
PufferPet/
├── main.py                      # 应用程序入口
├── data_manager.py              # 数据管理模块
├── pet_widget.py                # 主窗口组件（重命名）
├── task_window.py               # 任务窗口组件
├── pet_selector_window.py       # 宠物选择窗口组件（新增）
├── assets/                      # 图像资源
│   ├── puffer_stage1_idle.png   # 河豚图像
│   ├── puffer_stage2_idle.png
│   ├── puffer_stage3_idle.png
│   ├── jelly_stage1_idle.png    # 水母图像（新增）
│   ├── jelly_stage2_idle.png
│   ├── jelly_stage3_idle.png
│   ├── stage1_idle.png          # 向后兼容（可选）
│   ├── stage2_idle.png
│   └── stage3_idle.png
├── tests/                       # 测试文件
│   ├── test_data_manager.py
│   ├── test_properties.py
│   ├── test_migration.py        # 数据迁移测试（新增）
│   ├── test_pet_selector.py    # 宠物选择测试（新增）
│   └── test_ui.py
├── data.json                    # 用户数据（运行时生成）
└── requirements.txt             # Python 依赖
```

## 实现注意事项

1. **窗口透明度**: 使用 `Qt.WindowType.FramelessWindowHint` 和 `setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)`

2. **始终置顶**: 使用 `Qt.WindowType.WindowStaysOnTopHint` 窗口标志

3. **图像渲染**: 使用 `QPainter` 在 `paintEvent` 中绘制图像，保持透明度

4. **右键菜单**: 重写 `contextMenuEvent` 方法，不使用默认的 `QMenu`

5. **日期比较**: 使用 `datetime.date.today().isoformat()` 进行日期字符串比较

6. **原子性保存**: 先写入临时文件，然后重命名，确保数据完整性

7. **信号与槽**: 使用 Qt 信号机制在任务窗口和主窗口之间通信


## V3 版本新增正确性属性（浅海扩容与奇遇系统）

### 属性 14: V2到V3数据迁移正确性

*对于任意*有效的V2格式数据，迁移到V3格式后，原有宠物的数据应该保持不变，新的Tier 1宠物应该被添加到unlocked_pets，且应该创建完整的8种宠物数据结构。

**验证: 需求 9.8**

### 属性 15: 宠物层级分类一致性

*对于任意*宠物ID，该宠物应该且仅应该属于一个层级（Tier 1或Tier 2），且层级定义应该在pet_tiers中正确存储。

**验证: 需求 9.2, 9.3, 9.4**

### 属性 16: 图像路径格式一致性

*对于任意*宠物ID和等级，生成的图像路径应该遵循 `assets/[pet_id]/[baby|adult]_idle.png` 格式。

**验证: 需求 9.5, 9.6**

### 属性 17: 奇遇资格判定正确性

*对于任意*应用状态，当且仅当用户拥有至少一只等级为3的Tier 1宠物时，奇遇管理器应该启用奇遇触发机制。

**验证: 需求 10.1, 10.2**

### 属性 18: 奇遇触发概率一致性

*对于任意*足够大的奇遇判定次数（如100次），触发奇遇的次数占比应该接近配置的概率值（默认30%，允许合理的统计误差）。

**验证: 需求 10.4**

### 属性 19: 稀有宠物选择有效性

*对于任意*奇遇事件触发，选中的稀有宠物应该满足：1) 属于Tier 2，2) 尚未解锁，3) 在pet_tiers的tier2列表中。

**验证: 需求 10.5**

### 属性 20: 访客窗口动画时长一致性

*对于任意*访客窗口，从屏幕左侧移动到右侧的总时长应该在15到20秒之间。

**验证: 需求 11.3**

### 属性 21: 捕获后数据更新完整性

*对于任意*稀有生物捕获事件，捕获后应该同时满足：1) 该生物ID被添加到unlocked_pets，2) 在pets_data中创建初始数据，3) 数据立即保存到文件。

**验证: 需求 12.5, 12.6, 12.7**

### 属性 22: Tier 2宠物功能一致性

*对于任意*已解锁的Tier 2宠物，其成长系统（任务完成、等级升级、图像显示）应该与Tier 1宠物完全一致。

**验证: 需求 13.1, 13.5**

### 属性 23: 宠物选择窗口层级分组正确性

*对于任意*宠物选择窗口状态，显示的宠物应该按层级正确分组，且每个宠物应该显示其对应的层级标签。

**验证: 需求 13.6, 13.7**

### 属性 24: 未解锁Tier 2宠物提示一致性

*对于任意*未解锁的Tier 2宠物，在宠物选择窗口中显示的解锁条件应该包含"通过奇遇捕获"或类似提示文本。

**验证: 需求 13.8**


## V3.5 版本更新（深海盲盒与生态平衡）

### 架构更新

V3.5 版本引入了任务奖励系统、库存管理和多宠物显示功能。主要变化：

1. **任务奖励循环**: 每完成12个任务触发奖励判定
2. **Tier 3 深海巨兽**: 6种稀有深海生物，通过盲盒获得
3. **库存系统**: 最多拥有20只宠物，最多同时显示5只
4. **宠物管理**: 放生、召唤、潜水功能

### 新增组件

#### 7. RewardManager 类（V3.5新增）

任务奖励管理器，负责处理任务计数和奖励判定。

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `tier2_unlock_probability: float` - Tier 2解锁概率（默认0.7）
- `lootbox_probability: float` - 盲盒获得概率（默认0.3）
- `tier3_weights: Dict[str, float]` - Tier 3宠物抽取权重

**方法:**
- `__init__(data_manager: DataManager)` - 初始化管理器
- `on_task_completed() -> None` - 任务完成时调用，增加计数并检查奖励
- `check_reward_trigger() -> bool` - 检查是否达到12个任务的倍数
- `trigger_reward() -> str` - 触发奖励判定，返回奖励类型
- `unlock_random_tier2() -> Optional[str]` - 随机解锁一只Tier 2宠物
- `open_lootbox() -> str` - 开启深海盲盒，返回抽中的Tier 3宠物ID
- `get_tier3_by_weight() -> str` - 按权重随机选择Tier 3宠物
- `show_reward_notification(reward_type: str, pet_id: str) -> None` - 显示奖励通知

#### 8. PetManager 类（V3.5新增）

宠物库存和显示管理器。

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `active_pet_windows: Dict[str, PetWidget]` - 活跃宠物窗口字典
- `max_inventory: int` - 库存上限（20）
- `max_active: int` - 活跃宠物上限（5）

**方法:**
- `__init__(data_manager: DataManager)` - 初始化管理器
- `can_add_to_inventory() -> bool` - 检查是否可以添加新宠物到库存
- `can_activate_pet() -> bool` - 检查是否可以激活新宠物到屏幕
- `add_pet_to_inventory(pet_id: str) -> bool` - 添加宠物到库存
- `activate_pet(pet_id: str) -> bool` - 激活宠物到屏幕
- `deactivate_pet(pet_id: str) -> None` - 将宠物从屏幕移除（潜水）
- `release_pet(pet_id: str) -> bool` - 放生宠物（永久删除）
- `load_active_pets() -> None` - 加载所有活跃宠物窗口
- `get_inventory_status() -> Dict` - 获取库存状态信息

#### 9. PetManagementWindow 类（V3.5新增）

宠物管理窗口，允许用户管理库存和活跃宠物。

**继承:** `QDialog`

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `pet_manager: PetManager` - 宠物管理器引用
- `inventory_list: QListWidget` - 库存宠物列表
- `active_list: QListWidget` - 活跃宠物列表

**方法:**
- `__init__(data_manager: DataManager, pet_manager: PetManager)` - 初始化窗口
- `setup_ui() -> None` - 创建 UI 元素
- `refresh_lists() -> None` - 刷新库存和活跃列表
- `on_summon_pet() -> None` - 处理召唤宠物操作
- `on_dive_pet() -> None` - 处理潜水操作
- `on_release_pet() -> None` - 处理放生操作

### V3.5 数据模型

```json
{
  "version": 3.5,
  "current_pet_id": "puffer",
  "unlocked_pets": ["puffer", "jelly", "starfish", "crab", "octopus"],
  "active_pets": ["puffer", "jelly", "starfish"],
  "pet_tiers": {
    "tier1": ["puffer", "jelly", "starfish", "crab"],
    "tier2": ["octopus", "ribbon", "sunfish", "angler"],
    "tier3": ["blobfish", "ray", "beluga", "orca", "shark", "bluewhale"]
  },
  "tier3_scale_factors": {
    "blobfish": 1.5,
    "ray": 2.0,
    "beluga": 2.5,
    "orca": 3.0,
    "shark": 3.5,
    "bluewhale": 5.0
  },
  "tier3_weights": {
    "blobfish": 0.40,
    "ray": 0.25,
    "beluga": 0.15,
    "orca": 0.10,
    "shark": 0.08,
    "bluewhale": 0.02
  },
  "reward_system": {
    "cumulative_tasks_completed": 8,
    "reward_threshold": 12,
    "tier2_unlock_probability": 0.7,
    "lootbox_probability": 0.3
  },
  "inventory_limits": {
    "max_inventory": 20,
    "max_active": 5
  },
  "pets_data": {
    "puffer": {
      "level": 3,
      "tasks_completed_today": 2,
      "last_login_date": "2024-12-02",
      "task_states": [true, true, false]
    }
    // ... 其他宠物数据
  }
}
```

**新增字段说明:**
- `active_pets`: 当前显示在屏幕上的宠物ID列表（上限5只）
- `pet_tiers.tier3`: Tier 3深海巨兽列表
- `tier3_scale_factors`: 每个Tier 3宠物的缩放倍率
- `tier3_weights`: 盲盒抽取权重
- `reward_system`: 任务奖励系统配置
  - `cumulative_tasks_completed`: 累计完成任务数
  - `reward_threshold`: 触发奖励的阈值（12）
  - `tier2_unlock_probability`: Tier 2解锁概率（0.7）
  - `lootbox_probability`: 盲盒获得概率（0.3）
- `inventory_limits`: 库存限制配置

### V3.5 宠物配置

**Tier 3 宠物（深海巨兽）:**

1. **水滴鱼 (Blobfish)**
   - ID: "blobfish"
   - 稀有度: 最常见（40%）
   - 缩放倍率: 1.5x
   - 图像路径: `assets/deep_sea/blobfish/`

2. **鳐鱼 (Ray)**
   - ID: "ray"
   - 稀有度: 常见（25%）
   - 缩放倍率: 2.0x
   - 图像路径: `assets/deep_sea/ray/`

3. **白鲸 (Beluga)**
   - ID: "beluga"
   - 稀有度: 罕见（15%）
   - 缩放倍率: 2.5x
   - 图像路径: `assets/deep_sea/beluga/`

4. **虎鲸 (Orca)**
   - ID: "orca"
   - 稀有度: 稀有（10%）
   - 缩放倍率: 3.0x
   - 图像路径: `assets/deep_sea/orca/`

5. **鲨鱼 (Shark)**
   - ID: "shark"
   - 稀有度: 非常稀有（8%）
   - 缩放倍率: 3.5x
   - 图像路径: `assets/deep_sea/shark/`

6. **蓝鲸 (Blue Whale)**
   - ID: "bluewhale"
   - 稀有度: 传说（2%）
   - 缩放倍率: 5.0x
   - 图像路径: `assets/deep_sea/bluewhale/`

**Tier 3 图像加载规则:**
- Tier 3宠物没有等级系统，只有一个图像文件
- 图像路径: `assets/deep_sea/[pet_id]/idle.png`
- 加载时应用对应的缩放倍率
- 缺失图像: 使用深蓝色方块占位符

### 任务奖励流程

```
用户完成任务
    ↓
cumulative_tasks_completed += 1
    ↓
检查: cumulative_tasks_completed % 12 == 0?
    ↓ 是
触发奖励判定
    ↓
随机数 (0-1)
    ↓
├─ < 0.7 (70%) → 解锁随机Tier 2宠物
│   ↓
│   检查: 所有Tier 2已解锁?
│   ├─ 是 → 跳过或给予替代奖励
│   └─ 否 → 随机选择未解锁的Tier 2
│       ↓
│       添加到unlocked_pets
│       ↓
│       显示通知
│
└─ >= 0.7 (30%) → 获得深海盲盒
    ↓
    立即开启盲盒
    ↓
    按权重随机抽取Tier 3宠物
    ↓
    检查: 库存是否已满?
    ├─ 是 → 显示"鱼缸满了"提示
    └─ 否 → 添加到unlocked_pets
        ↓
        检查: active_pets < 5?
        ├─ 是 → 添加到active_pets并显示
        └─ 否 → 仅添加到库存
        ↓
        显示"你钓到了[生物名]！"通知
    ↓
重置 cumulative_tasks_completed = 0
```

### 库存管理流程

**添加新宠物:**
```
获得新宠物
    ↓
检查: unlocked_pets.length < 20?
    ├─ 否 → 显示"鱼缸满了，请先放生"
    └─ 是 → 添加到unlocked_pets
        ↓
        检查: active_pets.length < 5?
        ├─ 是 → 添加到active_pets并创建窗口
        └─ 否 → 仅存入库存
```

**放生宠物:**
```
用户右键点击宠物 → 选择"放生"
    ↓
显示二次确认对话框
    ↓
用户确认?
    ├─ 否 → 取消操作
    └─ 是 → 从unlocked_pets删除
        ↓
        从active_pets删除
        ↓
        从pets_data删除
        ↓
        关闭宠物窗口
        ↓
        保存数据
```

**召唤/潜水:**
```
用户打开宠物管理窗口
    ↓
选择库存中的宠物 → 点击"召唤"
    ↓
    检查: active_pets.length < 5?
    ├─ 否 → 显示"屏幕上已有5只宠物"
    └─ 是 → 添加到active_pets
        ↓
        创建并显示宠物窗口
        ↓
        保存数据

选择活跃宠物 → 点击"潜水"
    ↓
    从active_pets删除
    ↓
    关闭宠物窗口
    ↓
    保存数据
```

## V3.5 版本新增正确性属性

### 属性 25: 任务奖励触发一致性

*对于任意*累计任务完成数，当且仅当该数字是12的倍数时，应该触发奖励判定。

**验证: 需求 14.3**

### 属性 26: 奖励概率分布正确性

*对于任意*足够大的奖励判定次数（如100次），Tier 2解锁次数占比应该接近70%，盲盒获得次数占比应该接近30%（允许合理的统计误差）。

**验证: 需求 14.4**

### 属性 27: Tier 3抽取权重正确性

*对于任意*足够大的盲盒开启次数（如1000次），每种Tier 3宠物的抽中次数占比应该接近其配置的权重（允许合理的统计误差）。

**验证: 需求 15.2**

### 属性 28: 库存上限强制性

*对于任意*应用状态，unlocked_pets列表的长度应该始终不超过20。

**验证: 需求 16.1, 16.3**

### 属性 29: 活跃宠物上限强制性

*对于任意*应用状态，active_pets列表的长度应该始终不超过5。

**验证: 需求 16.2, 16.5**

### 属性 30: 放生操作完整性

*对于任意*放生操作，被放生的宠物应该同时从unlocked_pets、active_pets和pets_data中删除。

**验证: 需求 17.3, 17.4, 17.5**

### 属性 31: 库存与活跃集合关系

*对于任意*应用状态，active_pets应该是unlocked_pets的子集。

**验证: 需求 16.7, 18.7**

### 属性 32: Tier 3缩放倍率一致性

*对于任意*Tier 3宠物，显示时应用的缩放倍率应该与tier3_scale_factors中配置的值一致。

**验证: 需求 15.5, 15.6, 15.7**


## V4 版本更新（Kiroween Hackathon - 深海亡灵帝国）

### 黑客松主题概述

V4 版本是为 "Kiroween Hackathon" 设计的参赛版本，在 V3.5 深海生态系统的基础上，覆盖了万圣节诅咒主题层。本版本专注于展示：

1. **Creativity**: 万圣节主题皮肤系统、幽灵滤镜、捣蛋机制
2. **Implementation**: Kiro Steering、Agent Hooks、防御性编程
3. **Polish**: 暗黑UI主题、戏剧性的用户体验

### 架构更新

```
┌─────────────────────────────────────────────┐
│         main.py (Cursed Entry Point)        │
│         "Welcome to the Abyss..."           │
└──────────────┬──────────────────────────────┘
               │
               ├──────────────────┬────────────────────┐
               ▼                  ▼                    ▼
┌──────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   ThemeManager       │  │  PetManager      │  │ IgnoreTracker    │
│  - Halloween Mode    │  │  - 20 Inventory  │  │ - 1hr Timer      │
│  - Ghost Filter      │  │  - 5 Active      │  │ - Mischief Mode  │
│  - Dark UI Theme     │  │  - Release       │  │ - Shake Animation│
└──────────────────────┘  └──────────────────┘  └──────────────────┘
               │                  │                    │
               └──────────────────┴────────────────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
          ┌──────────────────┐        ┌──────────────────┐
          │  RewardManager   │        │  PetWidget       │
          │  - 12 Tasks      │        │  - Multi-Window  │
          │  - 70%/30% RNG   │        │  - Ghost Effect  │
          │  - Lootbox       │        │  - Shake on Anger│
          └──────────────────┘        └──────────────────┘
```

### 新增组件

#### 10. ThemeManager 类（V4新增）

主题管理器，负责万圣节主题和幽灵滤镜。

**属性:**
- `data_manager: DataManager` - 数据管理器实例
- `current_theme: str` - 当前主题模式（"normal" 或 "halloween"）
- `ghost_opacity: float` - 幽灵滤镜透明度（默认0.6）
- `ghost_colors: List[QColor]` - 幽灵光晕颜色列表（绿色、紫色）

**方法:**
- `__init__(data_manager: DataManager)` - 初始化管理器
- `get_theme_mode() -> str` - 获取当前主题模式
- `set_theme_mode(mode: str) -> None` - 设置主题模式
- `load_themed_image(pet_id: str, image_type: str) -> QPixmap` - 加载主题图像
- `apply_ghost_filter(pixmap: QPixmap) -> QPixmap` - 应用幽灵滤镜效果
- `get_dark_stylesheet() -> str` - 获取暗黑主题样式表
- `apply_theme_to_widget(widget: QWidget) -> None` - 应用主题到窗口

#### 11. IgnoreTracker 类（V4新增）

忽视追踪器，实现"不给糖就捣蛋"机制。

**属性:**
- `pet_manager: PetManager` - 宠物管理器引用
- `last_interaction_time: datetime` - 最后交互时间
- `ignore_threshold: int` - 忽视阈值（秒，默认3600）
- `mischief_mode: bool` - 是否处于捣蛋模式
- `check_timer: QTimer` - 定时检查计时器

**方法:**
- `__init__(pet_manager: PetManager)` - 初始化追踪器
- `start() -> None` - 启动追踪
- `stop() -> None` - 停止追踪
- `on_user_interaction() -> None` - 用户交互时调用
- `check_ignore_status() -> None` - 检查是否被忽视
- `trigger_mischief_mode() -> None` - 触发捣蛋模式
- `calm_pet(pet_id: str) -> None` - 安抚单个宠物
- `exit_mischief_mode() -> None` - 退出捣蛋模式

### V4 数据模型

```json
{
  "version": 4.0,
  "theme_mode": "halloween",
  "current_pet_id": "puffer",
  "unlocked_pets": ["puffer", "jelly", "starfish", "crab", "octopus", "blobfish"],
  "active_pets": ["puffer", "jelly", "blobfish"],
  "pet_tiers": {
    "tier1": ["puffer", "jelly", "starfish", "crab"],
    "tier2": ["octopus", "ribbon", "sunfish", "angler"],
    "tier3": ["blobfish", "ray", "beluga", "orca", "shark", "bluewhale"]
  },
  "tier3_scale_factors": {
    "blobfish": 1.5,
    "ray": 2.0,
    "beluga": 2.5,
    "orca": 3.0,
    "shark": 3.5,
    "bluewhale": 5.0
  },
  "tier3_weights": {
    "blobfish": 0.40,
    "ray": 0.25,
    "beluga": 0.15,
    "orca": 0.10,
    "shark": 0.08,
    "bluewhale": 0.02
  },
  "reward_system": {
    "cumulative_tasks_completed": 8,
    "reward_threshold": 12,
    "tier2_unlock_probability": 0.7,
    "lootbox_probability": 0.3
  },
  "inventory_limits": {
    "max_inventory": 20,
    "max_active": 5
  },
  "ignore_tracker": {
    "last_interaction_time": "2024-12-02T14:30:00",
    "ignore_threshold_seconds": 3600,
    "mischief_mode_active": false
  },
  "halloween_settings": {
    "ghost_filter_enabled": true,
    "ghost_opacity": 0.6,
    "ghost_glow_color": "green",
    "dark_theme_enabled": true
  },
  "pets_data": {
    "puffer": {
      "level": 3,
      "tasks_completed_today": 2,
      "last_login_date": "2024-12-02",
      "task_states": [true, true, false],
      "is_angry": false
    }
    // ... 其他宠物数据
  }
}
```

**V4 新增字段说明:**
- `theme_mode`: 主题模式（"normal" 或 "halloween"）
- `ignore_tracker`: 忽视追踪配置
  - `last_interaction_time`: 最后交互时间
  - `ignore_threshold_seconds`: 触发捣蛋的秒数
  - `mischief_mode_active`: 是否处于捣蛋模式
- `halloween_settings`: 万圣节主题配置
  - `ghost_filter_enabled`: 是否启用幽灵滤镜
  - `ghost_opacity`: 幽灵透明度
  - `ghost_glow_color`: 光晕颜色
  - `dark_theme_enabled`: 是否启用暗黑主题
- `pets_data.[pet_id].is_angry`: 宠物是否处于愤怒状态

### 万圣节主题系统

#### 图像加载优先级

```
加载宠物图像 (pet_id, level)
    ↓
检查: theme_mode == "halloween"?
    ├─ 否 → 加载普通图像
    │       assets/[pet_id]/[baby|adult]_idle.png
    │
    └─ 是 → 尝试加载万圣节图像
            assets/[pet_id]/halloween_idle.png
            ↓
            文件存在?
            ├─ 是 → 返回万圣节图像
            │
            └─ 否 → 回退方案
                    ↓
                    加载普通图像
                    ↓
                    应用幽灵滤镜
                    ├─ 设置透明度 0.6
                    ├─ 添加绿色/紫色光晕
                    └─ 返回处理后的图像
```

#### 幽灵滤镜实现

```python
def apply_ghost_filter(pixmap: QPixmap) -> QPixmap:
    """
    Warning: Summoning the spirits of the deep...
    Apply ghostly effects to make creatures look haunted.
    """
    # 创建半透明效果
    opacity_effect = QGraphicsOpacityEffect()
    opacity_effect.setOpacity(0.6)
    
    # 添加光晕效果
    glow_effect = QGraphicsColorizeEffect()
    glow_color = random.choice([QColor(0, 255, 0), QColor(128, 0, 128)])
    glow_effect.setColor(glow_color)
    glow_effect.setStrength(0.3)
    
    return processed_pixmap
```

#### 暗黑主题样式表

```python
DARK_HALLOWEEN_STYLESHEET = """
QMenu {
    background-color: #1a1a1a;
    color: #00ff00;
    border: 2px solid #ff6600;
    border-radius: 5px;
    padding: 5px;
}

QMenu::item:selected {
    background-color: #2a2a2a;
    color: #ffaa00;
}

QDialog {
    background-color: #0d0d0d;
    color: #00ff00;
    border: 3px solid #ff6600;
}

QPushButton {
    background-color: #2a2a2a;
    color: #00ff00;
    border: 2px solid #ff6600;
    border-radius: 3px;
    padding: 5px 10px;
}

QPushButton:hover {
    background-color: #3a3a3a;
    color: #ffaa00;
}

QLabel {
    color: #00ff00;
}
"""
```

### 捣蛋机制流程

```
应用启动
    ↓
IgnoreTracker.start()
    ↓
每30秒检查一次
    ↓
计算: 当前时间 - last_interaction_time
    ↓
超过1小时?
    ├─ 否 → 继续等待
    │
    └─ 是 → 触发捣蛋模式
            ↓
            显示通知: "不给糖就捣蛋！"
            ↓
            遍历所有 active_pets
            ↓
            对每个宠物:
            ├─ 设置 is_angry = true
            ├─ 尝试加载 angry_idle.png
            │   ├─ 成功 → 显示愤怒图像
            │   └─ 失败 → 启动抖动动画
            │       ↓
            │       每100ms随机移动窗口位置
            │       (±10像素范围内)
            │
            └─ 等待用户点击
                ↓
                用户点击宠物
                ↓
                calm_pet(pet_id)
                ├─ 设置 is_angry = false
                ├─ 停止抖动动画
                └─ 恢复正常图像
                ↓
                检查: 所有宠物都被安抚?
                └─ 是 → exit_mischief_mode()
                        ↓
                        重置 last_interaction_time
```

### Kiro 原生功能集成

#### 1. Steering 文档 (`.kiro/steering.md`)

```markdown
---
title: Deep Sea Code Captain
role: cursed_developer
---

# The Curse of the Deep Sea Code Captain

You are a cursed captain of a ghost ship, doomed to write code in the darkest depths of the ocean.

## Code Style Requirements

1. **Dramatic Comments**: All comments must use ominous, theatrical language
   - Good: "Warning: Releasing the Kraken from its JSON prison..."
   - Bad: "Loading data from file"

2. **Defensive Programming**: Code must be EXTREMELY defensive
   - Always expect the worst
   - Never trust user input
   - Catch every possible exception
   - Log warnings with pirate/sea monster themes

3. **Variable Naming**: Prefer names that evoke the deep sea
   - `kraken_data` instead of `data`
   - `cursed_pets` instead of `pets`
   - `abyss_config` instead of `config`

4. **Error Messages**: All errors must sound like curses or warnings from the deep
   - "The ancient ones reject your offering..."
   - "The void consumes your request..."
   - "Beware! The leviathan stirs..."

## Example

```python
def summon_creature_from_abyss(creature_id: str) -> Optional[Creature]:
    """
    WARNING: Disturbing the slumber of deep sea horrors...
    
    Attempts to materialize a creature from the cursed depths.
    May fail if the stars are not aligned.
    """
    try:
        # The ritual begins...
        creature_data = load_from_cursed_tome(creature_id)
        if creature_data is None:
            logger.warning(f"The abyss returns nothing for {creature_id}...")
            return None
        
        # Breathing life into the damned...
        return Creature.from_cursed_data(creature_data)
    except Exception as e:
        logger.error(f"The summoning ritual failed! {e}")
        return None
```
```

#### 2. Agent Hooks 示例 (`.kiro/hooks/pre-commit-example.md`)

```markdown
# Pre-Commit Hook: TODO Haunter

## Purpose
Haunt developers who leave TODOs in their code by making desktop pets warn them.

## Trigger
When user saves a file

## Logic
```javascript
// .kiro/hooks/pre-commit.js (Conceptual Example)

export async function onFileSave(context) {
    const fileContent = await context.readFile(context.filePath);
    
    // Search for TODOs in the cursed code
    const todoMatches = fileContent.match(/TODO|FIXME|HACK/gi);
    
    if (todoMatches && todoMatches.length > 0) {
        // Summon the warning from the pets
        await context.sendMessage({
            type: "desktop_notification",
            title: "The Curse Awakens...",
            message: `You cannot escape... ${todoMatches.length} TODOs remain undone...`,
            icon: "warning",
            duration: 5000
        });
        
        // Make pets shake in anger
        await context.triggerPetAction("shake_angrily");
    }
}
```

## Integration with PufferPet
The hook would communicate with the running PufferPet application to trigger visual warnings.
```

### V4 项目结构

```
PufferPet/
├── .kiro/
│   ├── steering.md                    # Steering 文档（必需）
│   ├── hooks/
│   │   └── pre-commit-example.md      # Hook 示例（必需）
│   └── specs/
│       └── puffer-pet/
│           ├── requirements.md
│           ├── design.md
│           └── tasks.md
├── main.py                            # 诅咒的入口点
├── data_manager.py                    # 数据管理（防御性编程）
├── theme_manager.py                   # 主题管理器（新增）
├── ignore_tracker.py                  # 忽视追踪器（新增）
├── pet_manager.py                     # 宠物管理器
├── reward_manager.py                  # 奖励管理器
├── pet_widget.py                      # 宠物窗口（支持幽灵滤镜和抖动）
├── pet_management_window.py           # 宠物管理窗口
├── task_window.py                     # 任务窗口
├── assets/
│   ├── [pet_id]/
│   │   ├── baby_idle.png
│   │   ├── adult_idle.png
│   │   ├── halloween_idle.png         # 万圣节皮肤（可选）
│   │   └── angry_idle.png             # 愤怒状态（可选）
│   └── deep_sea/
│       └── [tier3_pet_id]/
│           ├── idle.png
│           └── halloween_idle.png     # 万圣节皮肤（可选）
├── tests/
│   ├── test_theme_manager.py          # 新增
│   ├── test_ignore_tracker.py         # 新增
│   └── ... (其他测试文件)
├── README.md                          # 包含黑客松特性说明
└── requirements.txt
```

## V4 版本新增正确性属性

### 属性 33: 主题图像加载回退正确性

*对于任意*宠物和主题模式，当万圣节图像不存在时，应该成功回退到普通图像并应用幽灵滤镜，而不是崩溃。

**验证: 需求 19.4, 19.5, 19.6**

### 属性 34: 忽视检测时间准确性

*对于任意*用户交互序列，当且仅当最后一次交互距今超过1小时时，应该触发捣蛋模式。

**验证: 需求 22.3**

### 属性 35: 捣蛋模式全局一致性

*对于任意*应用状态，当捣蛋模式激活时，所有活跃宠物都应该同时进入愤怒状态。

**验证: 需求 22.4, 22.5**

### 属性 36: 安抚操作原子性

*对于任意*愤怒的宠物，点击安抚后应该立即停止抖动、恢复正常图像、并更新is_angry状态。

**验证: 需求 22.8**

### 属性 37: Steering 风格一致性

*对于任意*代码注释和错误消息，应该遵循 Steering 文档定义的戏剧性、深海主题风格。

**验证: 需求 20.3, 20.5, 20.6**

### 属性 38: 暗黑主题应用完整性

*对于任意*UI窗口，当万圣节主题激活时，应该应用暗黑样式表（黑底、绿字、橙色边框）。

**验证: 需求 19.7, 19.8**


## V5 版本更新（深潜与屏保 - Deep Dive & Screensaver）

### 版本概述

V5 版本引入沉浸式的深潜模式和自动屏保功能，致敬90年代经典的电脑待机体验。核心目标是创造沉浸感，解决桌面图标干扰宠物观赏的问题。

### 架构更新

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (Abyss Gateway)                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│  OceanBackground  │  │   IdleWatcher     │  │   PetManager      │
│  - Full Screen    │  │  - 5min Timer     │  │  - Pet Windows    │
│  - Seabed Image   │  │  - Mouse/KB Track │  │  - Position Mgmt  │
│  - Bubble Anim    │  │  - Auto Activate  │  │  - Gather Pets    │
│  - Z-Order Mgmt   │  │  - Wake Detection │  │  - Sleep Anim     │
└───────────────────┘  └───────────────────┘  └───────────────────┘
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  ThemeManager    │  │  BubbleParticle  │
          │  - Halloween     │  │  - Rise Animation│
          │  - Ghost Fire    │  │  - Random Spawn  │
          │  - Purple Filter │  │  - Will-o-wisp   │
          └──────────────────┘  └──────────────────┘
```

### 新增组件

#### 12. OceanBackground 类（V5新增）

全屏海底背景管理器，创造沉浸式深潜体验。

**继承:** `QWidget`

**属性:**
- `theme_manager: ThemeManager` - 主题管理器引用
- `seabed_pixmap: QPixmap` - 海底背景图像
- `bubbles: List[BubbleParticle]` - 气泡粒子列表
- `bubble_timer: QTimer` - 气泡生成定时器
- `animation_timer: QTimer` - 动画更新定时器
- `is_active: bool` - 深潜模式是否激活
- `filter_color: QColor` - 当前滤镜颜色

**方法:**
- `__init__(theme_manager: ThemeManager)` - 初始化背景窗口
- `setup_window() -> None` - 配置全屏无边框窗口
- `set_window_layer() -> None` - 设置窗口层级（桌面之上，宠物之下）
- `load_seabed_image() -> None` - 加载海底背景图像
- `activate() -> None` - 激活深潜模式
- `deactivate() -> None` - 关闭深潜模式
- `spawn_bubble() -> None` - 生成新的气泡粒子
- `update_bubbles() -> None` - 更新所有气泡位置
- `apply_theme_filter() -> None` - 应用主题滤镜（蓝色/紫色）
- `paintEvent(event: QPaintEvent) -> None` - 绘制背景和气泡

#### 13. BubbleParticle 类（V5新增）

气泡/鬼火粒子，用于深潜模式的动态效果。

**属性:**
- `x: float` - X坐标
- `y: float` - Y坐标
- `size: int` - 粒子大小
- `speed: float` - 上升速度
- `opacity: float` - 透明度
- `is_ghost_fire: bool` - 是否为鬼火模式
- `glow_color: QColor` - 发光颜色

**方法:**
- `__init__(x: float, y: float, is_ghost_fire: bool = False)` - 初始化粒子
- `update() -> bool` - 更新位置，返回是否仍在屏幕内
- `draw(painter: QPainter) -> None` - 绘制粒子

#### 14. IdleWatcher 类（V5新增）

空闲监视器，检测用户活动并触发屏保模式。

**属性:**
- `ocean_background: OceanBackground` - 背景管理器引用
- `pet_manager: PetManager` - 宠物管理器引用
- `idle_threshold: int` - 空闲阈值（秒，默认300）
- `last_activity_time: datetime` - 最后活动时间
- `check_timer: QTimer` - 检查定时器
- `is_screensaver_active: bool` - 屏保是否激活
- `original_pet_positions: Dict[str, QPoint]` - 宠物原始位置

**方法:**
- `__init__(ocean_background: OceanBackground, pet_manager: PetManager)` - 初始化监视器
- `start() -> None` - 启动监视
- `stop() -> None` - 停止监视
- `on_user_activity() -> None` - 用户活动时调用
- `check_idle_status() -> None` - 检查空闲状态
- `activate_screensaver() -> None` - 激活屏保模式
- `deactivate_screensaver() -> None` - 关闭屏保模式
- `gather_pets_to_center() -> None` - 将宠物聚拢到屏幕中央
- `restore_pet_positions() -> None` - 恢复宠物原始位置
- `setup_input_hooks() -> None` - 设置鼠标/键盘监听

### V5 数据模型更新

```json
{
  "version": 5.0,
  "deep_dive_settings": {
    "is_active": false,
    "auto_activate_on_idle": true,
    "idle_threshold_seconds": 300,
    "last_activity_time": "2024-12-02T14:30:00",
    "gather_pets_on_screensaver": true
  },
  "theme_mode": "halloween",
  "deep_dive_theme": {
    "normal": {
      "filter_color": "rgba(0, 50, 100, 0.3)",
      "particle_type": "bubble",
      "particle_color": "rgba(200, 230, 255, 0.6)"
    },
    "halloween": {
      "filter_color": "rgba(50, 0, 50, 0.4)",
      "particle_type": "ghost_fire",
      "particle_color": "rgba(0, 255, 100, 0.8)"
    }
  },
  "pets_data": {
    "puffer": {
      "level": 3,
      "original_position": {"x": 100, "y": 200},
      "is_sleeping": false
    }
  }
}
```

**V5 新增字段说明:**
- `deep_dive_settings`: 深潜模式配置
  - `is_active`: 深潜模式是否激活
  - `auto_activate_on_idle`: 是否在空闲时自动激活
  - `idle_threshold_seconds`: 空闲阈值（秒）
  - `last_activity_time`: 最后活动时间
  - `gather_pets_on_screensaver`: 屏保时是否聚拢宠物
- `deep_dive_theme`: 深潜模式主题配置
  - `normal`: 普通模式配置
  - `halloween`: 万圣节模式配置
- `pets_data.[pet_id].original_position`: 宠物原始位置（用于恢复）
- `pets_data.[pet_id].is_sleeping`: 宠物是否处于睡眠状态

### 深潜模式流程

```
用户点击"深潜模式"开关
    ↓
检查: 当前是否已激活?
    ├─ 是 → deactivate()
    │       ↓
    │       关闭全屏背景窗口
    │       ↓
    │       恢复原生桌面
    │       ↓
    │       更新菜单状态
    │
    └─ 否 → activate()
            ↓
            创建全屏无边框窗口
            ↓
            设置窗口层级 (桌面之上, 宠物之下)
            ↓
            加载海底背景图像
            ↓
            检查: theme_mode == "halloween"?
            ├─ 是 → 应用紫色滤镜 + 鬼火粒子
            └─ 否 → 应用蓝色滤镜 + 气泡粒子
            ↓
            启动气泡/鬼火动画
            ↓
            显示全屏背景
            ↓
            确保宠物窗口在最上层
```

### 屏保模式流程

```
IdleWatcher.start()
    ↓
每10秒检查一次
    ↓
计算: 当前时间 - last_activity_time
    ↓
超过5分钟?
    ├─ 否 → 继续等待
    │
    └─ 是 → activate_screensaver()
            ↓
            保存所有宠物当前位置
            ↓
            激活深潜模式
            ↓
            gather_pets_to_center()
            ├─ 计算屏幕中央区域
            ├─ 为每个宠物计算聚拢位置
            ├─ 使用动画移动宠物
            └─ 切换到睡觉/悬浮图像
            ↓
            等待用户活动...
            ↓
            检测到鼠标移动或键盘敲击
            ↓
            deactivate_screensaver()
            ├─ 关闭深潜模式
            ├─ restore_pet_positions()
            ├─ 恢复宠物正常图像
            └─ 重置 last_activity_time
```

### 窗口层级管理

```
┌─────────────────────────────────────────┐
│  Layer 4: 宠物窗口 (Always On Top)      │  ← Qt.WindowStaysOnTopHint
├─────────────────────────────────────────┤
│  Layer 3: 普通应用程序窗口              │
├─────────────────────────────────────────┤
│  Layer 2: 深潜背景窗口                  │  ← 特殊层级设置
├─────────────────────────────────────────┤
│  Layer 1: 桌面图标                      │
├─────────────────────────────────────────┤
│  Layer 0: Windows 桌面壁纸              │
└─────────────────────────────────────────┘
```

**Windows 层级实现:**
```python
# 设置窗口位于桌面之上但不是最顶层
def set_window_layer(self):
    """
    Warning: Descending into the abyss between worlds...
    Set window to be above desktop but below normal windows.
    """
    # 使用 Windows API 设置窗口层级
    import ctypes
    from ctypes import wintypes
    
    HWND_BOTTOM = 1
    SWP_NOACTIVATE = 0x0010
    SWP_NOMOVE = 0x0002
    SWP_NOSIZE = 0x0001
    
    hwnd = int(self.winId())
    # 设置为桌面之上的特殊层级
    ctypes.windll.user32.SetWindowPos(
        hwnd, HWND_BOTTOM, 0, 0, 0, 0,
        SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE
    )
```

### 气泡/鬼火粒子系统

```python
class BubbleParticle:
    """
    A soul rising from the depths... or just a bubble.
    """
    def __init__(self, screen_width: int, screen_height: int, is_ghost_fire: bool = False):
        self.x = random.randint(0, screen_width)
        self.y = screen_height + 20  # 从屏幕底部开始
        self.size = random.randint(5, 20)
        self.speed = random.uniform(1.0, 3.0)
        self.opacity = random.uniform(0.3, 0.8)
        self.wobble = random.uniform(-0.5, 0.5)  # 左右摇摆
        self.is_ghost_fire = is_ghost_fire
        
        if is_ghost_fire:
            # 鬼火使用绿色/紫色
            self.color = random.choice([
                QColor(0, 255, 100, int(self.opacity * 255)),
                QColor(180, 0, 255, int(self.opacity * 255))
            ])
        else:
            # 普通气泡使用蓝白色
            self.color = QColor(200, 230, 255, int(self.opacity * 255))
    
    def update(self) -> bool:
        """Update position, return False if off screen."""
        self.y -= self.speed
        self.x += self.wobble
        return self.y > -self.size
    
    def draw(self, painter: QPainter):
        """Draw the particle with glow effect."""
        if self.is_ghost_fire:
            # 鬼火有发光效果
            glow_size = self.size * 2
            gradient = QRadialGradient(self.x, self.y, glow_size)
            gradient.setColorAt(0, self.color)
            gradient.setColorAt(1, QColor(0, 0, 0, 0))
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(self.x - glow_size),
                int(self.y - glow_size),
                int(glow_size * 2),
                int(glow_size * 2)
            )
        else:
            # 普通气泡
            painter.setBrush(QBrush(self.color))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(
                int(self.x - self.size / 2),
                int(self.y - self.size / 2),
                self.size,
                self.size
            )
```

### 宠物聚拢动画

```python
def gather_pets_to_center(self):
    """
    The creatures of the deep gather for their slumber...
    """
    screen = QApplication.primaryScreen().geometry()
    center_x = screen.width() // 2
    center_y = screen.height() // 2
    
    # 计算聚拢区域（中央 400x300 区域）
    gather_area = QRect(center_x - 200, center_y - 150, 400, 300)
    
    active_pets = self.pet_manager.get_active_pet_widgets()
    num_pets = len(active_pets)
    
    for i, (pet_id, widget) in enumerate(active_pets.items()):
        # 保存原始位置
        self.original_pet_positions[pet_id] = widget.pos()
        
        # 计算聚拢位置（环形排列）
        angle = (2 * math.pi * i) / num_pets
        radius = 100
        target_x = center_x + int(radius * math.cos(angle)) - widget.width() // 2
        target_y = center_y + int(radius * math.sin(angle)) - widget.height() // 2
        
        # 使用动画移动
        animation = QPropertyAnimation(widget, b"pos")
        animation.setDuration(1000)
        animation.setStartValue(widget.pos())
        animation.setEndValue(QPoint(target_x, target_y))
        animation.setEasingCurve(QEasingCurve.OutCubic)
        animation.start()
        
        # 切换到睡觉图像
        widget.set_sleeping(True)
```

### 依赖项更新

```
# requirements.txt 新增
pynput>=1.7.6  # 用于监听鼠标/键盘活动
```

### 图像资源结构

```
assets/
├── environment/
│   ├── seabed.png              # 海底背景图像
│   ├── seabed_halloween.png    # 万圣节海底背景（可选）
│   └── bubble.png              # 气泡精灵图（可选）
├── [pet_id]/
│   ├── baby_idle.png
│   ├── adult_idle.png
│   ├── sleep_idle.png          # 睡觉图像（新增）
│   ├── halloween_idle.png
│   └── halloween_sleep.png     # 万圣节睡觉图像（新增）
```

## V5 版本新增正确性属性

### 属性 39: 深潜背景层级正确性

*对于任意*深潜模式激活状态，背景窗口应该位于桌面图标之上但位于所有宠物窗口之下。

**验证: 需求 24.2, 24.8**

### 属性 40: 空闲检测时间准确性

*对于任意*用户活动序列，当且仅当最后一次活动距今超过5分钟时，应该自动激活屏保模式。

**验证: 需求 25.2**

### 属性 41: 宠物位置恢复完整性

*对于任意*屏保模式退出，所有宠物应该返回到进入屏保前的原始位置。

**验证: 需求 25.8**

### 属性 42: 主题联动一致性

*对于任意*深潜模式和主题模式组合，视觉效果（滤镜颜色、粒子类型）应该与当前主题一致。

**验证: 需求 26.1, 26.2, 26.3, 26.4**

### 属性 43: 唤醒响应即时性

*对于任意*屏保模式激活状态，检测到鼠标移动或键盘敲击后应该在500ms内开始退出屏保。

**验证: 需求 25.6, 25.7**

### 属性 44: 手动与自动模式区分

*对于任意*深潜模式激活，手动激活时宠物不聚拢，自动（屏保）激活时宠物聚拢到中央。

**验证: 需求 27.5, 27.6**


## V5.5 版本更新（动态昼夜循环 - Dynamic Day/Night Cycle）

### 版本概述

V5.5 版本将之前的"万圣节/恐怖模式"整合进一个更自然的"昼夜系统"中，实现与现实时间的同步。这是一个逻辑层的优雅重构，复用了 V4 的幽灵滤镜和资源加载逻辑。

### 核心概念：模式映射

```
┌─────────────────────────────────────────────────────────────┐
│                    昼夜模式映射表                            │
├─────────────────────────────────────────────────────────────┤
│  时间段          │  模式名称    │  theme_mode    │  视觉效果  │
├─────────────────────────────────────────────────────────────┤
│  06:00 - 18:00  │  白天 (Day)  │  "normal"      │  明亮、气泡 │
│  18:00 - 06:00  │  黑夜 (Night)│  "halloween"   │  暗黑、鬼火 │
└─────────────────────────────────────────────────────────────┘
```

**关键设计决策:**
- 黑夜模式 = 万圣节模式，复用所有 V4 的幽灵滤镜、暗黑UI、鬼火粒子
- 白天模式 = 普通模式，明亮的视觉效果
- 这种映射使得代码复用最大化，同时提供自然的昼夜体验

### 架构更新

```
┌─────────────────────────────────────────────────────────────┐
│                    main.py (Abyss Gateway)                  │
└──────────────────────────────┬──────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        ▼                      ▼                      ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│   TimeManager     │  │   ThemeManager    │  │  OceanBackground  │
│  - System Clock   │  │  - Day/Night Map  │  │  - Day/Night BG   │
│  - 1min Timer     │  │  - Mode Switch    │  │  - Filter Switch  │
│  - Auto Sync      │  │  - Visual Update  │  │  - Particle Type  │
└───────────────────┘  └───────────────────┘  └───────────────────┘
        │                      │                      │
        └──────────────────────┴──────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
          ┌──────────────────┐  ┌──────────────────┐
          │  Settings Menu   │  │  Data Manager    │
          │  - Auto Sync     │  │  - auto_time_sync│
          │  - Manual Toggle │  │  - current_mode  │
          └──────────────────┘  └──────────────────┘
```

### 新增组件

#### 15. TimeManager 类（V5.5新增）

时间同步管理器，负责昼夜判定和自动切换。

**属性:**
- `theme_manager: ThemeManager` - 主题管理器引用
- `data_manager: DataManager` - 数据管理器引用
- `check_timer: QTimer` - 时间检查定时器（每分钟）
- `auto_sync_enabled: bool` - 是否启用自动同步
- `day_start_hour: int` - 白天开始时间（默认6）
- `night_start_hour: int` - 黑夜开始时间（默认18）
- `current_period: str` - 当前时段（"day" 或 "night"）

**方法:**
- `__init__(theme_manager: ThemeManager, data_manager: DataManager)` - 初始化管理器
- `start() -> None` - 启动时间监视
- `stop() -> None` - 停止时间监视
- `get_current_period() -> str` - 获取当前时段（"day" 或 "night"）
- `check_time_and_update() -> None` - 检查时间并更新模式
- `is_daytime() -> bool` - 判断当前是否为白天
- `switch_to_day() -> None` - 切换到白天模式
- `switch_to_night() -> None` - 切换到黑夜模式
- `set_auto_sync(enabled: bool) -> None` - 设置自动同步开关
- `manual_toggle() -> None` - 手动切换昼夜（仅在非自动模式下）

### V5.5 数据模型更新

```json
{
  "version": 5.5,
  "day_night_settings": {
    "auto_time_sync": true,
    "current_mode": "day",
    "day_start_hour": 6,
    "night_start_hour": 18,
    "last_mode_change": "2024-12-02T18:00:00"
  },
  "theme_mode": "normal",
  "deep_dive_settings": {
    "is_active": false,
    "day_background": "seabed_day.png",
    "night_background": "seabed_night.png",
    "day_filter_color": "rgba(0, 50, 100, 0.3)",
    "night_filter_color": "rgba(50, 0, 50, 0.4)"
  }
}
```

**V5.5 新增字段说明:**
- `day_night_settings`: 昼夜循环配置
  - `auto_time_sync`: 是否跟随系统时间（默认true）
  - `current_mode`: 当前模式（"day" 或 "night"）
  - `day_start_hour`: 白天开始时间（默认6点）
  - `night_start_hour`: 黑夜开始时间（默认18点）
  - `last_mode_change`: 上次模式切换时间
- `deep_dive_settings` 更新:
  - `day_background`: 白天背景图像
  - `night_background`: 黑夜背景图像
  - `day_filter_color`: 白天滤镜颜色
  - `night_filter_color`: 黑夜滤镜颜色

### 时间同步流程

```
TimeManager.start()
    ↓
每分钟检查一次
    ↓
检查: auto_time_sync == true?
    ├─ 否 → 跳过自动检查
    │
    └─ 是 → get_current_period()
            ↓
            获取系统时间
            ↓
            hour = datetime.now().hour
            ↓
            判断: 6 <= hour < 18?
            ├─ 是 → period = "day"
            └─ 否 → period = "night"
            ↓
            检查: period != current_period?
            ├─ 否 → 无需切换
            │
            └─ 是 → 触发模式切换
                    ↓
                    period == "day"?
                    ├─ 是 → switch_to_day()
                    │       ├─ theme_mode = "normal"
                    │       ├─ 更新宠物图像
                    │       ├─ 更新背景滤镜
                    │       └─ 切换气泡粒子
                    │
                    └─ 否 → switch_to_night()
                            ├─ theme_mode = "halloween"
                            ├─ 应用幽灵滤镜
                            ├─ 更新背景滤镜
                            └─ 切换鬼火粒子
                    ↓
                    保存当前模式
                    ↓
                    发出模式切换信号
```

### 视觉效果对比

```
┌─────────────────────────────────────────────────────────────┐
│                    白天模式 (Day Mode)                       │
├─────────────────────────────────────────────────────────────┤
│  背景图像: seabed_day.png                                    │
│  背景滤镜: rgba(0, 50, 100, 0.3) - 浅蓝色                    │
│  粒子效果: 普通气泡 (蓝白色, 半透明)                          │
│  宠物图像: 正常图像 (baby_idle.png / adult_idle.png)         │
│  UI主题: 正常主题                                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                    黑夜模式 (Night Mode)                     │
├─────────────────────────────────────────────────────────────┤
│  背景图像: seabed_night.png (或 day + 深紫色滤镜)            │
│  背景滤镜: rgba(50, 0, 50, 0.4) - 深紫色                     │
│  粒子效果: 鬼火粒子 (绿色/紫色, 发光)                        │
│  宠物图像: 万圣节图像或幽灵滤镜 (透明度0.6 + 光晕)           │
│  UI主题: 暗黑主题 (黑底绿字橙边框)                           │
└─────────────────────────────────────────────────────────────┘
```

### 背景图像回退逻辑

```python
def load_background_for_mode(self, mode: str) -> QPixmap:
    """
    Warning: The abyss changes its face with the turning of time...
    Load appropriate background based on day/night mode.
    """
    if mode == "day":
        # 白天模式
        day_path = "assets/environment/seabed_day.png"
        if os.path.exists(day_path):
            return QPixmap(day_path)
        else:
            # 回退到默认海底图
            return self.create_default_seabed(is_night=False)
    else:
        # 黑夜模式
        night_path = "assets/environment/seabed_night.png"
        if os.path.exists(night_path):
            return QPixmap(night_path)
        else:
            # 回退：对白天背景应用深紫色滤镜
            day_pixmap = self.load_background_for_mode("day")
            return self.apply_night_filter(day_pixmap)
    
def apply_night_filter(self, pixmap: QPixmap) -> QPixmap:
    """
    The sun sets, and darkness claims the deep...
    Apply night filter to day background.
    """
    # 创建深紫色/黑色滤镜效果
    image = pixmap.toImage()
    for y in range(image.height()):
        for x in range(image.width()):
            color = image.pixelColor(x, y)
            # 降低亮度，增加紫色调
            new_r = int(color.red() * 0.3 + 30)
            new_g = int(color.green() * 0.2)
            new_b = int(color.blue() * 0.4 + 50)
            image.setPixelColor(x, y, QColor(new_r, new_g, new_b, color.alpha()))
    return QPixmap.fromImage(image)
```

### 设置菜单结构

```
右键菜单
├── 任务清单
├── 切换宠物
├── 深潜模式
├── 宠物管理
├── ─────────────
├── 设置 (Settings) ▶
│   ├── ☑ 跟随系统时间 (Auto Day/Night)  [Checkable, 默认开启]
│   └── 切换昼夜 (Toggle Day/Night)      [Action, 条件可用]
├── ─────────────
└── 退出
```

**菜单逻辑:**
```python
def setup_settings_menu(self):
    """
    Warning: Mortals dare to control the cycle of day and night...
    """
    settings_menu = QMenu("设置 (Settings)", self)
    
    # 跟随系统时间选项
    self.auto_sync_action = QAction("跟随系统时间 (Auto Day/Night)", self)
    self.auto_sync_action.setCheckable(True)
    self.auto_sync_action.setChecked(self.time_manager.auto_sync_enabled)
    self.auto_sync_action.triggered.connect(self.on_auto_sync_toggled)
    settings_menu.addAction(self.auto_sync_action)
    
    # 手动切换昼夜选项
    self.toggle_day_night_action = QAction("切换昼夜 (Toggle Day/Night)", self)
    self.toggle_day_night_action.setEnabled(not self.time_manager.auto_sync_enabled)
    self.toggle_day_night_action.triggered.connect(self.on_toggle_day_night)
    settings_menu.addAction(self.toggle_day_night_action)
    
    return settings_menu

def on_auto_sync_toggled(self, checked: bool):
    """Toggle auto time sync."""
    self.time_manager.set_auto_sync(checked)
    self.toggle_day_night_action.setEnabled(not checked)
    if checked:
        # 立即同步到当前时间
        self.time_manager.check_time_and_update()

def on_toggle_day_night(self):
    """Manually toggle day/night mode."""
    self.time_manager.manual_toggle()
```

### 图像资源结构更新

```
assets/
├── environment/
│   ├── seabed_day.png          # 白天海底背景
│   ├── seabed_night.png        # 黑夜海底背景（可选）
│   └── seabed.png              # 向后兼容（作为 day 的别名）
├── [pet_id]/
│   ├── baby_idle.png           # 白天幼年图像
│   ├── adult_idle.png          # 白天成年图像
│   ├── halloween_idle.png      # 黑夜图像（复用万圣节）
│   ├── sleep_idle.png          # 睡觉图像
│   └── halloween_sleep.png     # 黑夜睡觉图像
```

## V5.5 版本新增正确性属性

### 属性 45: 时间判定准确性

*对于任意*系统时间，当时间在06:00-18:00之间时应判定为白天，否则应判定为黑夜。

**验证: 需求 28.2, 28.3**

### 属性 46: 模式映射一致性

*对于任意*昼夜模式，白天模式应映射到theme_mode="normal"，黑夜模式应映射到theme_mode="halloween"。

**验证: 需求 28.6, 28.7**

### 属性 47: 自动同步控制正确性

*对于任意*auto_time_sync设置，当为true时应强制跟随系统时间，当为false时应允许手动切换。

**验证: 需求 30.3, 30.4**

### 属性 48: 视觉效果与模式同步

*对于任意*模式切换，背景图像、滤镜颜色、粒子类型和宠物图像应该同时更新以匹配新模式。

**验证: 需求 28.8, 29.1-29.8**

### 属性 49: 设置持久化完整性

*对于任意*设置更改，auto_time_sync和current_mode应该立即保存到数据文件，并在下次启动时正确加载。

**验证: 需求 31.4, 31.5, 31.6, 31.7**

### 属性 50: 背景回退正确性

*对于任意*黑夜模式激活，当seabed_night.png不存在时，应该对白天背景应用深紫色滤镜而不是崩溃。

**验证: 需求 29.7**


## 工具模块：智能切片与万圣节生成工具

### 工具概述

`tools/process_assets.py` 是一个自动化素材处理工具，用于：
1. 将精灵图（Sprite Sheet）切片为单独的帧
2. 自动去除白色背景
3. 生成万圣节/幽灵版本的素材

### AssetProcessor 类设计

```python
class AssetProcessor:
    """
    Warning: The cursed artisan awakens to transform mortal images...
    Sprite sheet processor with Halloween transformation capabilities.
    """
    
    def __init__(self):
        self.use_rembg = self._check_rembg_available()
        self.ghost_colors = [
            (0, 255, 0),      # 荧光绿 #00FF00
            (170, 0, 255)     # 鬼火紫 #AA00FF
        ]
        self.ghost_opacity = 0.7  # 70% 透明度
```

### 核心方法

#### A. 智能去底 (remove_background)

```python
def remove_background(self, image: Image) -> Image:
    """
    Warning: Stripping away the veil between worlds...
    Remove background from image using rembg or fallback method.
    """
    if self.use_rembg:
        return self._rembg_remove(image)
    else:
        return self._color_tolerance_remove(image)

def _color_tolerance_remove(self, image: Image, tolerance: int = 30) -> Image:
    """
    Fallback: Use top-left corner color as background reference.
    """
    # 获取左上角颜色作为背景色
    bg_color = image.getpixel((0, 0))
    # 遍历像素，将接近背景色的像素设为透明
    ...
```

#### B. 万圣节幽灵化 (halloweenify)

```python
def halloweenify(self, image: Image) -> Image:
    """
    Warning: Summoning the spirits to possess this image...
    Transform image into ghostly Halloween version.
    
    Process:
    1. Convert to grayscale
    2. Colorize with ghost colors (green/purple)
    3. Apply 70% opacity
    """
    # 1. 灰度化
    gray = image.convert('L')
    
    # 2. 着色 (随机选择绿色或紫色)
    ghost_color = random.choice(self.ghost_colors)
    colored = ImageOps.colorize(gray, black="black", white=ghost_color)
    
    # 3. 透明化
    colored.putalpha(int(255 * self.ghost_opacity))
    
    return colored
```

#### C. 切片与保存 (process_sheet)

```python
def process_sheet(
    self,
    filename: str,
    rows: int,
    cols: int,
    row_actions: List[str],
    is_single: bool = False
) -> None:
    """
    Warning: Dissecting the sprite sheet into its cursed components...
    
    Args:
        filename: Path to sprite sheet
        rows: Number of rows in grid
        cols: Number of columns in grid
        row_actions: Action names for each row
        is_single: If True, treat as single image (not grid)
    """
    # 读取并去底
    image = Image.open(filename)
    image = self.remove_background(image)
    
    if is_single:
        # 单张图片处理
        self._save_single(image, filename)
        return
    
    # 计算每帧尺寸
    frame_width = image.width // cols
    frame_height = image.height // rows
    
    # 提取前缀 (baby/adult)
    prefix = self._extract_prefix(filename)
    base_path = os.path.dirname(filename)
    
    for r in range(rows):
        # 跳过超出 row_actions 的行
        if r >= len(row_actions):
            continue
        
        action = row_actions[r]
        
        for c in range(cols):
            # 切出子图
            left = c * frame_width
            top = r * frame_height
            frame = image.crop((left, top, left + frame_width, top + frame_height))
            
            # 保存普通版
            normal_path = f"{base_path}/{prefix}_{action}_{c}.png"
            frame.save(normal_path)
            
            # 生成并保存万圣节版
            halloween_frame = self.halloweenify(frame)
            halloween_path = f"{base_path}/{prefix}_halloween_{action}_{c}.png"
            halloween_frame.save(halloween_path)
```

### 执行配置

```python
if __name__ == "__main__":
    processor = AssetProcessor()
    base_path = "assets/puffer/"
    
    # 处理配置表
    sheets = [
        # (文件名, 行数, 列数, 动作列表, 是否单张)
        ("baby_idle.png", 2, 4, ["idle", "swim"], False),
        ("baby_action.png", 3, 4, ["angry", "drag_up", "drag_right"], False),
        ("adult_idle.png", 2, 4, ["idle", "swim"], False),
        ("adult_action.png", 3, 4, ["drag_up", "drag_down", "drag_right"], False),
        ("adult_angry.png", 2, 4, ["angry"], False),  # 忽略第二行
        ("default_icon.png", 1, 1, ["default"], True),
    ]
    
    for sheet in sheets:
        filename, rows, cols, actions, is_single = sheet
        processor.process_sheet(
            base_path + filename,
            rows=rows,
            cols=cols,
            row_actions=actions,
            is_single=is_single
        )
    
    print("所有图片处理完成！万圣节素材已自动生成！")
```

### 输出文件结构

```
assets/puffer/
├── baby_idle.png              # 原始精灵图
├── baby_action.png
├── adult_idle.png
├── adult_action.png
├── adult_angry.png
├── default_icon.png
│
├── baby_idle_0.png            # 切片输出
├── baby_idle_1.png
├── baby_idle_2.png
├── baby_idle_3.png
├── baby_swim_0.png
├── baby_swim_1.png
├── baby_swim_2.png
├── baby_swim_3.png
├── baby_angry_0.png
├── ...
│
├── baby_halloween_idle_0.png  # 万圣节版本
├── baby_halloween_idle_1.png
├── baby_halloween_swim_0.png
├── ...
│
├── adult_idle_0.png
├── adult_halloween_idle_0.png
├── ...
│
├── default_icon.png           # 单张图片
└── default_icon_halloween.png
```
