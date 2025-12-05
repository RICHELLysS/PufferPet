# 需求文档

## 简介

PufferPet 是一个基于 Python + PyQt6 的桌面宠物应用程序。该应用在桌面上显示一只可爱的河豚，通过完成每日任务来培养和进化河豚。应用程序具有透明背景、始终置顶的特性，并通过右键菜单提供任务管理功能。

## 术语表

- **PufferPet应用**: 桌面宠物应用程序的主系统
- **宠物窗口**: 显示宠物图像的无边框透明窗口
- **任务窗口**: 显示每日任务清单的弹出窗口
- **数据文件**: 存储用户进度的 data.json 文件
- **等级**: 宠物的成长阶段（Level 1-3）
- **每日任务**: 用户每天需要完成的三个固定任务
- **宠物ID**: 唯一标识宠物类型的字符串（例如 "puffer" 或 "jelly"）
- **解锁条件**: 用户需要满足的特定条件才能解锁新宠物
- **切换菜单**: 允许用户在已解锁宠物之间切换的界面
- **Tier 1宠物**: 基础宠物层级，默认可解锁，拥有完整成长系统
- **Tier 2宠物**: 稀有宠物层级，只能通过奇遇事件捕获解锁
- **奇遇事件**: 稀有生物随机出现在屏幕上的事件
- **奇遇管理器**: 负责触发和管理奇遇事件的后台组件
- **访客窗口**: 显示路过的稀有生物的临时窗口

## 需求

### 需求 1

**用户故事:** 作为用户，我希望在桌面上看到一只透明背景的河豚宠物，以便它能自然地融入我的工作环境。

#### 验收标准

1. WHEN PufferPet应用启动 THEN PufferPet应用 SHALL 创建一个无边框窗口
2. WHEN 河豚窗口显示 THEN PufferPet应用 SHALL 渲染完全透明的背景
3. WHEN PufferPet应用启动 THEN PufferPet应用 SHALL 从 assets 文件夹加载 stage1_idle.png 图像
4. WHEN 河豚窗口创建 THEN PufferPet应用 SHALL 设置窗口为始终置顶模式
5. WHEN 指定的图像文件不存在 THEN PufferPet应用 SHALL 显示红色方块占位符并继续运行

### 需求 2

**用户故事:** 作为用户，我希望河豚能够根据我完成的任务数量成长和进化，以便获得成就感和持续的动力。

#### 验收标准

1. WHEN PufferPet应用首次启动 THEN PufferPet应用 SHALL 创建 data.json 文件存储等级、今日完成任务数和最后登录日期
2. WHEN PufferPet应用启动 THEN PufferPet应用 SHALL 读取 data.json 文件并加载用户数据
3. WHEN 当前日期与最后登录日期不同 THEN PufferPet应用 SHALL 将今日完成任务数重置为零
4. WHEN 用户今日完成任务数达到 3 且等级小于 3 THEN PufferPet应用 SHALL 将等级增加 1
5. WHEN 等级为 1 THEN PufferPet应用 SHALL 显示 stage1_idle.png 图像
6. WHEN 等级为 2 THEN PufferPet应用 SHALL 显示 stage2_idle.png 图像
7. WHEN 等级为 3 THEN PufferPet应用 SHALL 显示 stage3_idle.png 图像
8. WHEN 用户数据发生变化 THEN PufferPet应用 SHALL 立即将更新后的数据写入 data.json 文件

### 需求 3

**用户故事:** 作为用户，我希望通过右键点击河豚来访问任务清单，以便方便地管理和完成每日任务。

#### 验收标准

1. WHEN 用户在河豚窗口上右键点击 THEN PufferPet应用 SHALL 显示任务窗口
2. WHEN 任务窗口显示 THEN 任务窗口 SHALL 展示当前的任务进度（格式：X/3）
3. WHEN 任务窗口显示 THEN 任务窗口 SHALL 包含三个固定任务的复选框（喝一杯水、伸个懒腰、专注工作30分钟）
4. WHEN 用户勾选任务复选框 THEN PufferPet应用 SHALL 增加今日完成任务数
5. WHEN 用户取消勾选任务复选框 THEN PufferPet应用 SHALL 减少今日完成任务数
6. WHEN 今日完成任务数达到 3 THEN PufferPet应用 SHALL 立即触发河豚进化并更新显示图像
7. WHEN 任务窗口关闭 THEN PufferPet应用 SHALL 保存任务完成状态到数据文件

### 需求 4

**用户故事:** 作为用户，我希望应用程序能够优雅地处理错误情况，以便即使出现问题也不会导致程序崩溃。

#### 验收标准

1. WHEN 图像文件缺失或无法加载 THEN PufferPet应用 SHALL 显示红色方块占位符
2. WHEN data.json 文件损坏或格式错误 THEN PufferPet应用 SHALL 创建新的默认数据文件
3. WHEN 文件系统权限不足无法写入 data.json THEN PufferPet应用 SHALL 记录错误并在内存中维护状态
4. WHEN 发生未预期的异常 THEN PufferPet应用 SHALL 捕获异常并继续运行


## V2 版本新增需求

### 需求 5

**用户故事:** 作为用户，我希望能够收集和切换不同的宠物，以便体验更多样化的桌面宠物内容。

#### 验收标准

1. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 current_pet_id 字段标识当前显示的宠物
2. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 unlocked_pets 列表存储所有已解锁的宠物ID
3. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 pets_data 字典分别存储每个宠物的独立数据
4. WHEN PufferPet应用首次启动 THEN unlocked_pets 列表 SHALL 仅包含 "puffer"
5. WHEN 宠物窗口显示 THEN PufferPet应用 SHALL 根据 current_pet_id 加载对应宠物的图像
6. WHEN 用户切换宠物 THEN PufferPet应用 SHALL 更新 current_pet_id 并刷新显示
7. WHEN 用户切换宠物 THEN PufferPet应用 SHALL 保存当前宠物的数据并加载新宠物的数据
8. WHEN 旧版 data.json 文件存在 THEN PufferPet应用 SHALL 自动迁移数据到新格式

### 需求 6

**用户故事:** 作为用户，我希望通过达成特定条件来解锁新宠物（水母），以便获得长期游戏目标和成就感。

#### 验收标准

1. WHEN 河豚达到等级 3 THEN PufferPet应用 SHALL 自动解锁水母宠物
2. WHEN 水母被解锁 THEN PufferPet应用 SHALL 将 "jelly" 添加到 unlocked_pets 列表
3. WHEN 水母被解锁 THEN PufferPet应用 SHALL 在 pets_data 中创建水母的初始数据
4. WHEN 水母被解锁 THEN PufferPet应用 SHALL 显示解锁通知或提示
5. WHEN 宠物尚未解锁 THEN 切换菜单 SHALL 显示该宠物为锁定状态
6. WHEN 用户尝试切换到未解锁的宠物 THEN PufferPet应用 SHALL 阻止切换并提示解锁条件

### 需求 7

**用户故事:** 作为用户，我希望通过右键菜单访问宠物切换功能，以便方便地在已解锁的宠物之间切换。

#### 验收标准

1. WHEN 用户在宠物窗口上右键点击 THEN PufferPet应用 SHALL 显示包含"切换宠物"选项的菜单
2. WHEN 用户点击"切换宠物"选项 THEN PufferPet应用 SHALL 显示宠物选择窗口
3. WHEN 宠物选择窗口显示 THEN 宠物选择窗口 SHALL 列出所有已解锁的宠物
4. WHEN 宠物选择窗口显示 THEN 宠物选择窗口 SHALL 显示未解锁宠物的锁定状态和解锁条件
5. WHEN 用户选择已解锁的宠物 THEN PufferPet应用 SHALL 切换到该宠物并关闭选择窗口
6. WHEN 用户选择当前正在显示的宠物 THEN PufferPet应用 SHALL 直接关闭选择窗口
7. WHEN 宠物选择窗口显示 THEN 宠物选择窗口 SHALL 高亮显示当前正在使用的宠物

### 需求 8

**用户故事:** 作为用户，我希望每个宠物都有独立的成长进度，以便我可以分别培养不同的宠物。

#### 验收标准

1. WHEN 用户完成任务 THEN PufferPet应用 SHALL 仅更新当前显示宠物的任务完成数
2. WHEN 用户切换宠物 THEN 新宠物 SHALL 显示其自己的等级和进度
3. WHEN 切换回之前的宠物 THEN 该宠物 SHALL 保持其之前的等级和进度
4. WHEN 日期变化触发重置 THEN PufferPet应用 SHALL 重置所有宠物的每日任务完成数
5. WHEN 水母等级为 1 THEN PufferPet应用 SHALL 显示 jelly_stage1_idle.png 图像
6. WHEN 水母等级为 2 THEN PufferPet应用 SHALL 显示 jelly_stage2_idle.png 图像
7. WHEN 水母等级为 3 THEN PufferPet应用 SHALL 显示 jelly_stage3_idle.png 图像


## V3 版本新增需求（浅海扩容与奇遇系统）

### 需求 9

**用户故事:** 作为用户，我希望能够收集更多种类的海洋生物，以便体验更丰富的宠物收集乐趣。

#### 验收标准

1. WHEN PufferPet应用启动 THEN 数据文件 SHALL 支持8种生物的数据存储
2. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 pet_tiers 字段定义每个宠物的层级
3. WHEN 用户首次启动V3版本 THEN Tier 1宠物列表 SHALL 包含 puffer、jelly、starfish、crab
4. WHEN 用户首次启动V3版本 THEN Tier 2宠物列表 SHALL 包含 octopus、ribbon、sunfish、angler
5. WHEN Tier 1宠物显示 THEN PufferPet应用 SHALL 根据等级加载对应的图像文件
6. WHEN 加载宠物图像 THEN PufferPet应用 SHALL 从 assets/[pet_id]/ 目录加载图像
7. WHEN 宠物图像文件不存在 THEN PufferPet应用 SHALL 显示带颜色的方块占位符
8. WHEN V2版本数据文件存在 THEN PufferPet应用 SHALL 自动迁移数据到V3格式

### 需求 10

**用户故事:** 作为用户，我希望通过奇遇系统发现和捕获稀有生物，以便获得探索和收集的乐趣。

#### 验收标准

1. WHEN 用户拥有至少1只等级3的Tier 1宠物 THEN 奇遇管理器 SHALL 启用奇遇触发机制
2. WHEN 用户没有等级3的Tier 1宠物 THEN 奇遇管理器 SHALL 禁用奇遇触发机制
3. WHEN 奇遇管理器启用 THEN 奇遇管理器 SHALL 每5分钟进行一次奇遇判定
4. WHEN 进行奇遇判定 THEN 奇遇管理器 SHALL 以30%概率触发奇遇事件
5. WHEN 奇遇事件触发 THEN 奇遇管理器 SHALL 从未解锁的Tier 2宠物中随机选择一只
6. WHEN 所有Tier 2宠物已解锁 THEN 奇遇管理器 SHALL 不再触发奇遇事件
7. WHEN 奇遇事件触发 THEN 访客窗口 SHALL 显示选中的稀有生物
8. WHEN 访客窗口显示 THEN 访客窗口 SHALL 加载稀有生物的adult_idle.png图像

### 需求 11

**用户故事:** 作为用户，我希望看到稀有生物从屏幕一侧游到另一侧，以便感受到生动的海洋氛围。

#### 验收标准

1. WHEN 访客窗口创建 THEN 访客窗口 SHALL 在屏幕左侧边缘外初始化位置
2. WHEN 访客窗口显示 THEN 访客窗口 SHALL 以恒定速度向右移动
3. WHEN 访客窗口移动 THEN 访客窗口 SHALL 在15到20秒内完成从左到右的移动
4. WHEN 访客窗口到达屏幕右侧边缘 THEN 访客窗口 SHALL 自动关闭并销毁
5. WHEN 访客窗口显示 THEN 访客窗口 SHALL 保持透明背景和始终置顶
6. WHEN 访客窗口移动期间 THEN 访客窗口 SHALL 不阻塞用户的其他操作
7. WHEN 访客窗口显示 THEN 访客窗口 SHALL 不响应右键菜单事件

### 需求 12

**用户故事:** 作为用户，我希望能够点击路过的稀有生物来捕获它们，以便将它们添加到我的收藏中。

#### 验收标准

1. WHEN 用户点击访客窗口 THEN PufferPet应用 SHALL 触发捕获事件
2. WHEN 捕获事件触发 THEN 访客窗口 SHALL 立即停止移动并关闭
3. WHEN 捕获事件触发 THEN PufferPet应用 SHALL 显示捕获成功通知
4. WHEN 显示捕获通知 THEN 通知 SHALL 包含稀有生物的名称
5. WHEN 捕获成功 THEN PufferPet应用 SHALL 将稀有生物ID添加到unlocked_pets列表
6. WHEN 捕获成功 THEN PufferPet应用 SHALL 在pets_data中创建该生物的初始数据
7. WHEN 捕获成功 THEN PufferPet应用 SHALL 立即保存数据到data.json文件
8. WHEN 稀有生物被捕获 THEN 该生物 SHALL 在宠物选择窗口中变为可选择状态

### 需求 13

**用户故事:** 作为用户，我希望所有解锁的宠物（包括稀有生物）都能正常切换和培养，以便享受完整的养成体验。

#### 验收标准

1. WHEN Tier 2宠物被解锁 THEN 该宠物 SHALL 拥有与Tier 1宠物相同的成长系统
2. WHEN 用户切换到Tier 2宠物 THEN 宠物窗口 SHALL 显示该宠物的当前等级图像
3. WHEN Tier 2宠物等级为1 THEN PufferPet应用 SHALL 显示baby_idle.png图像
4. WHEN Tier 2宠物等级为2或3 THEN PufferPet应用 SHALL 显示adult_idle.png图像
5. WHEN 用户完成任务 THEN Tier 2宠物 SHALL 像Tier 1宠物一样升级
6. WHEN 宠物选择窗口显示 THEN 窗口 SHALL 按层级分组显示宠物
7. WHEN 宠物选择窗口显示 THEN 窗口 SHALL 显示每个宠物的层级标签
8. WHEN 未解锁的Tier 2宠物显示 THEN 解锁条件 SHALL 提示"通过奇遇捕获"


## V3.5 版本新增需求（深海盲盒与生态平衡）

### 需求 14

**用户故事:** 作为用户，我希望通过完成任务获得奖励，以便有持续的动力完成每日任务并收集更多生物。

#### 验收标准

1. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 cumulative_tasks_completed 字段记录累计完成任务数
2. WHEN 用户完成任务 THEN PufferPet应用 SHALL 增加 cumulative_tasks_completed 计数
3. WHEN cumulative_tasks_completed 达到12的倍数 THEN PufferPet应用 SHALL 触发奖励判定
4. WHEN 奖励判定触发 THEN PufferPet应用 SHALL 以70%概率解锁Tier 2宠物或以30%概率获得深海盲盒
5. WHEN 获得Tier 2宠物奖励且所有Tier 2宠物已解锁 THEN PufferPet应用 SHALL 跳过奖励或给予替代奖励
6. WHEN 获得深海盲盒 THEN PufferPet应用 SHALL 立即开启盲盒并按权重随机抽取Tier 3宠物
7. WHEN 盲盒开启 THEN PufferPet应用 SHALL 显示"你钓到了[生物名]！"通知
8. WHEN 奖励判定完成 THEN PufferPet应用 SHALL 重置 cumulative_tasks_completed 为0

### 需求 15

**用户故事:** 作为用户，我希望收集稀有的深海巨兽，以便体验更丰富的收集乐趣和视觉效果。

#### 验收标准

1. WHEN PufferPet应用启动 THEN 数据文件 SHALL 支持6种Tier 3深海巨兽的数据存储
2. WHEN 深海盲盒开启 THEN PufferPet应用 SHALL 按以下权重随机选择：水滴鱼40%、鳐鱼25%、白鲸15%、虎鲸10%、鲨鱼8%、蓝鲸2%
3. WHEN Tier 3宠物被抽中 THEN PufferPet应用 SHALL 将该宠物添加到库存
4. WHEN Tier 3宠物显示 THEN PufferPet应用 SHALL 从 assets/deep_sea/[pet_id]/ 目录加载图像
5. WHEN Tier 3宠物显示 THEN PufferPet应用 SHALL 根据宠物类型应用1.5x到5.0x的缩放倍率
6. WHEN 水滴鱼显示 THEN PufferPet应用 SHALL 应用1.5x缩放倍率
7. WHEN 蓝鲸显示 THEN PufferPet应用 SHALL 应用5.0x缩放倍率
8. WHEN Tier 3宠物图像文件不存在 THEN PufferPet应用 SHALL 显示带颜色的方块占位符

### 需求 16

**用户故事:** 作为用户，我希望管理我的宠物库存，以便控制屏幕上显示的宠物数量并保持桌面整洁。

#### 验收标准

1. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 unlocked_pets 列表记录所有拥有的宠物（上限20只）
2. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 active_pets 列表记录当前显示的宠物（上限5只）
3. WHEN 用户拥有的宠物数量达到20只 THEN PufferPet应用 SHALL 阻止获取新宠物
4. WHEN 库存已满且尝试获取新宠物 THEN PufferPet应用 SHALL 显示"鱼缸满了，请先放生"提示
5. WHEN 获得新宠物且屏幕上少于5只 THEN PufferPet应用 SHALL 自动将新宠物添加到active_pets并显示
6. WHEN 获得新宠物且屏幕上已有5只 THEN PufferPet应用 SHALL 仅将新宠物添加到unlocked_pets库存
7. WHEN 应用启动 THEN PufferPet应用 SHALL 仅加载和显示active_pets列表中的宠物
8. WHEN active_pets列表为空 THEN PufferPet应用 SHALL 从unlocked_pets中选择一只宠物显示

### 需求 17

**用户故事:** 作为用户，我希望能够放生不需要的宠物，以便为新宠物腾出空间并管理我的收藏。

#### 验收标准

1. WHEN 用户在宠物窗口上右键点击 THEN 右键菜单 SHALL 包含"放生"选项
2. WHEN 用户点击"放生"选项 THEN PufferPet应用 SHALL 显示二次确认对话框
3. WHEN 用户确认放生 THEN PufferPet应用 SHALL 从unlocked_pets中删除该宠物ID
4. WHEN 用户确认放生 THEN PufferPet应用 SHALL 从active_pets中删除该宠物ID
5. WHEN 用户确认放生 THEN PufferPet应用 SHALL 从pets_data中删除该宠物的数据
6. WHEN 用户确认放生 THEN PufferPet应用 SHALL 关闭该宠物的窗口
7. WHEN 用户确认放生 THEN PufferPet应用 SHALL 立即保存数据到data.json文件
8. WHEN 用户取消放生 THEN PufferPet应用 SHALL 保持宠物状态不变

### 需求 18

**用户故事:** 作为用户，我希望能够在库存和屏幕之间切换宠物，以便灵活管理我想要显示的宠物。

#### 验收标准

1. WHEN 用户访问宠物管理界面 THEN 界面 SHALL 显示所有库存中的宠物（unlocked_pets）
2. WHEN 用户访问宠物管理界面 THEN 界面 SHALL 区分显示当前活跃的宠物（active_pets）
3. WHEN 用户选择库存中的宠物召唤 THEN PufferPet应用 SHALL 检查active_pets是否少于5只
4. WHEN active_pets少于5只且用户召唤宠物 THEN PufferPet应用 SHALL 将宠物添加到active_pets并显示窗口
5. WHEN active_pets已有5只且用户召唤宠物 THEN PufferPet应用 SHALL 显示"屏幕上已有5只宠物"提示
6. WHEN 用户选择活跃宠物潜水 THEN PufferPet应用 SHALL 从active_pets中移除该宠物并关闭窗口
7. WHEN 用户选择活跃宠物潜水 THEN 该宠物 SHALL 保留在unlocked_pets库存中
8. WHEN 宠物管理操作完成 THEN PufferPet应用 SHALL 立即保存数据到data.json文件


## V4 版本新增需求（Kiroween Hackathon - 深海亡灵帝国）

### 需求 19

**用户故事:** 作为黑客松参赛者，我希望展示万圣节主题皮肤系统，以便在 Costume Contest 赛道中获得高分。

#### 验收标准

1. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 theme_mode 字段控制主题模式
2. WHEN theme_mode 设置为 "halloween" THEN PufferPet应用 SHALL 优先加载万圣节主题图像
3. WHEN 加载宠物图像且theme_mode为halloween THEN PufferPet应用 SHALL 首先尝试加载 assets/[pet_id]/halloween_idle.png
4. WHEN 万圣节图像文件不存在 THEN PufferPet应用 SHALL 回退到普通图像并应用幽灵滤镜效果
5. WHEN 应用幽灵滤镜 THEN PufferPet应用 SHALL 设置图像透明度为0.6
6. WHEN 应用幽灵滤镜 THEN PufferPet应用 SHALL 添加绿色或紫色光晕特效
7. WHEN theme_mode 为 "halloween" THEN 所有UI窗口 SHALL 应用暗黑主题样式表
8. WHEN 暗黑主题激活 THEN 右键菜单 SHALL 显示黑底、绿字、橙色边框样式

### 需求 20

**用户故事:** 作为黑客松参赛者，我希望展示 Kiro 的 Steering 功能，以便在 Implementation 评分中获得高分。

#### 验收标准

1. WHEN 项目初始化 THEN 项目 SHALL 包含 .kiro/steering.md 文件
2. WHEN Steering文件存在 THEN 文件内容 SHALL 定义深海代码船长的角色和代码风格要求
3. WHEN 生成代码注释 THEN 注释 SHALL 使用阴森、戏剧性的语气
4. WHEN 编写代码 THEN 代码风格 SHALL 极其防御性以防止崩溃
5. WHEN Steering规则激活 THEN 所有错误处理 SHALL 包含戏剧性的警告信息
6. WHEN 关键操作执行 THEN 日志信息 SHALL 使用海盗/深海主题的语言
7. WHEN 代码生成 THEN 变量命名 SHALL 反映深海/诅咒主题（可选但推荐）
8. WHEN 文档生成 THEN 文档 SHALL 保持深海亡灵帝国的叙事风格

### 需求 21

**用户故事:** 作为黑客松参赛者，我希望展示 Kiro 的 Agent Hooks 功能，以便展示自动化工作流。

#### 验收标准

1. WHEN 项目初始化 THEN 项目 SHALL 包含 .kiro/hooks/ 目录
2. WHEN hooks目录存在 THEN 目录 SHALL 包含示例 hook 文件
3. WHEN 创建pre-commit hook THEN hook SHALL 包含检查TODO的逻辑说明
4. WHEN 检测到TODO THEN hook SHALL 触发桌面宠物警告气泡
5. WHEN 警告气泡显示 THEN 消息 SHALL 使用诅咒/威胁性的语气
6. WHEN hook文档创建 THEN 文档 SHALL 清晰说明hook的触发条件和行为
7. WHEN hook示例提供 THEN 示例 SHALL 展示与桌面宠物的集成可能性
8. WHEN 项目文档更新 THEN 文档 SHALL 说明如何启用和配置hooks

### 需求 22

**用户故事:** 作为用户，我希望宠物在被忽视时会表现出不满，以便增加互动性和趣味性。

#### 验收标准

1. WHEN PufferPet应用运行 THEN 应用 SHALL 追踪最后一次用户交互时间
2. WHEN 用户点击任何宠物 THEN 应用 SHALL 重置忽视计时器
3. WHEN 用户连续1小时未点击任何宠物 THEN 应用 SHALL 触发"捣蛋模式"
4. WHEN 捣蛋模式触发 THEN 所有活跃宠物 SHALL 进入愤怒状态
5. WHEN 宠物进入愤怒状态 THEN 宠物 SHALL 尝试加载 angry_idle.png 图像
6. WHEN angry图像不存在 THEN 宠物 SHALL 开始疯狂抖动动画
7. WHEN 抖动动画播放 THEN 宠物窗口 SHALL 在当前位置周围随机移动
8. WHEN 用户点击愤怒的宠物 THEN 宠物 SHALL 恢复正常状态并停止抖动
9. WHEN 所有愤怒宠物被安抚 THEN 应用 SHALL 退出捣蛋模式
10. WHEN 捣蛋模式激活 THEN 应用 SHALL 显示"不给糖就捣乱！"通知

### 需求 23

**用户故事:** 作为黑客松评委，我希望看到完整的项目结构和文档，以便评估项目的实现质量。

#### 验收标准

1. WHEN 项目提交 THEN 项目 SHALL 包含完整的 .kiro/ 目录结构
2. WHEN .kiro目录存在 THEN 目录 SHALL 包含 steering.md 文件
3. WHEN .kiro目录存在 THEN 目录 SHALL 包含 hooks/ 子目录
4. WHEN 项目文档生成 THEN README SHALL 包含黑客松特性说明章节
5. WHEN 特性说明编写 THEN 文档 SHALL 突出展示 Kiro 原生功能的使用
6. WHEN 代码提交 THEN 所有关键模块 SHALL 包含详细的文档字符串
7. WHEN 文档字符串编写 THEN 文档 SHALL 遵循 Steering 定义的风格
8. WHEN 项目演示 THEN 演示 SHALL 能够展示万圣节主题、库存管理和捣蛋机制


## V5 版本新增需求（深潜与屏保 - Deep Dive & Screensaver）

### 需求 24

**用户故事:** 作为用户，我希望能够开启深潜模式，以便在沉浸式的海底环境中观赏我的宠物，不受桌面图标干扰。

#### 验收标准

1. WHEN 用户开启深潜模式 THEN PufferPet应用 SHALL 创建一个全屏无边框窗口
2. WHEN 深潜背景窗口创建 THEN 窗口 SHALL 位于桌面图标之上但位于宠物窗口之下
3. WHEN 深潜背景显示 THEN 背景 SHALL 加载 assets/environment/seabed.png 图像
4. WHEN 深潜背景显示 THEN 背景 SHALL 叠加半透明蓝色滤镜（rgba(0, 50, 100, 0.3)）
5. WHEN 深潜模式激活 THEN 背景 SHALL 显示随机上升的气泡粒子动画
6. WHEN 气泡粒子生成 THEN 气泡 SHALL 从屏幕底部飘升到顶部
7. WHEN 用户关闭深潜模式 THEN 全屏背景窗口 SHALL 立即关闭并恢复原生桌面
8. WHEN 深潜模式激活 THEN 所有宠物窗口 SHALL 保持在背景窗口之上可见

### 需求 25

**用户故事:** 作为用户，我希望应用能在我离开电脑时自动进入屏保模式，以便享受怀旧的待机体验。

#### 验收标准

1. WHEN PufferPet应用运行 THEN 应用 SHALL 监听鼠标和键盘活动
2. WHEN 用户5分钟内无任何操作 THEN 应用 SHALL 自动激活深潜模式
3. WHEN 屏保模式自动激活 THEN 所有活跃宠物 SHALL 移动到屏幕中央区域聚拢
4. WHEN 宠物聚拢到中央 THEN 宠物 SHALL 尝试播放睡觉或悬浮动画
5. WHEN 睡觉动画不存在 THEN 宠物 SHALL 显示普通idle图像并轻微上下浮动
6. WHEN 检测到鼠标移动 THEN 应用 SHALL 立即退出深潜模式
7. WHEN 检测到键盘敲击 THEN 应用 SHALL 立即退出深潜模式
8. WHEN 退出屏保模式 THEN 宠物 SHALL 返回到原来的位置

### 需求 26

**用户故事:** 作为用户，我希望深潜模式能与万圣节主题联动，以便在不同主题下获得不同的视觉体验。

#### 验收标准

1. WHEN 深潜模式激活且theme_mode为halloween THEN 背景颜色 SHALL 变为暗紫色或黑色
2. WHEN 万圣节深潜模式激活 THEN 气泡粒子 SHALL 变为鬼火粒子效果
3. WHEN 鬼火粒子显示 THEN 粒子 SHALL 使用绿色或紫色发光效果
4. WHEN 万圣节深潜模式激活 THEN 背景滤镜 SHALL 使用rgba(50, 0, 50, 0.4)
5. WHEN 主题模式切换 THEN 深潜背景 SHALL 实时更新视觉效果
6. WHEN 万圣节模式下宠物聚拢 THEN 宠物 SHALL 尝试加载halloween_sleep.png图像
7. WHEN 万圣节睡觉图像不存在 THEN 宠物 SHALL 应用幽灵滤镜到普通睡觉图像
8. WHEN 深潜模式退出 THEN 主题设置 SHALL 保持不变

### 需求 27

**用户故事:** 作为用户，我希望能够通过菜单控制深潜模式，以便随时手动开启或关闭沉浸式体验。

#### 验收标准

1. WHEN 用户右键点击托盘图标 THEN 菜单 SHALL 包含"深潜模式"开关选项
2. WHEN 深潜模式关闭时点击开关 THEN 应用 SHALL 激活深潜模式
3. WHEN 深潜模式开启时点击开关 THEN 应用 SHALL 关闭深潜模式
4. WHEN 深潜模式状态改变 THEN 菜单选项文字 SHALL 更新为当前状态
5. WHEN 深潜模式手动开启 THEN 宠物 SHALL 不自动聚拢到中央
6. WHEN 深潜模式通过屏保自动开启 THEN 宠物 SHALL 自动聚拢到中央
7. WHEN 用户手动关闭深潜模式 THEN 空闲计时器 SHALL 重置
8. WHEN 深潜模式状态改变 THEN 数据文件 SHALL 记录当前状态


## V5.5 版本新增需求（动态昼夜循环 - Dynamic Day/Night Cycle）

### 需求 28

**用户故事:** 作为用户，我希望应用能够根据现实时间自动切换昼夜模式，以便获得与真实世界同步的沉浸式体验。

#### 验收标准

1. WHEN PufferPet应用运行 THEN 应用 SHALL 获取系统本地时间进行昼夜判定
2. WHEN 系统时间在06:00至18:00之间 THEN 应用 SHALL 判定为白天模式
3. WHEN 系统时间在18:00至06:00之间 THEN 应用 SHALL 判定为黑夜模式
4. WHEN 应用运行期间 THEN 时间管理器 SHALL 每分钟检查一次当前时间
5. WHEN 时间跨越昼夜阈值 THEN 应用 SHALL 自动平滑切换到对应模式
6. WHEN 切换到白天模式 THEN theme_mode SHALL 设置为 "normal"
7. WHEN 切换到黑夜模式 THEN theme_mode SHALL 设置为 "halloween"
8. WHEN 模式切换发生 THEN 应用 SHALL 立即更新所有视觉效果

### 需求 29

**用户故事:** 作为用户，我希望白天和黑夜模式有明显不同的视觉效果，以便清晰感知当前的时间状态。

#### 验收标准

1. WHEN 白天模式激活 THEN 宠物 SHALL 显示正常图像
2. WHEN 白天模式激活 THEN 深潜背景 SHALL 加载 seabed_day.png 图像
3. WHEN 白天模式激活 THEN 背景滤镜 SHALL 使用浅蓝色（rgba(0, 50, 100, 0.3)）
4. WHEN 白天模式激活 THEN 粒子效果 SHALL 显示普通气泡
5. WHEN 黑夜模式激活 THEN 宠物 SHALL 应用幽灵滤镜或加载万圣节图像
6. WHEN 黑夜模式激活 THEN 深潜背景 SHALL 加载 seabed_night.png 图像
7. WHEN seabed_night.png不存在 THEN 应用 SHALL 对白天背景应用深紫色滤镜
8. WHEN 黑夜模式激活 THEN 粒子效果 SHALL 显示发光的鬼火粒子

### 需求 30

**用户故事:** 作为用户，我希望能够控制是否跟随系统时间，以便在需要时手动切换昼夜模式。

#### 验收标准

1. WHEN 用户打开设置菜单 THEN 菜单 SHALL 包含"跟随系统时间"复选框选项
2. WHEN "跟随系统时间"选项默认状态 THEN 选项 SHALL 为开启状态
3. WHEN "跟随系统时间"开启 THEN 应用 SHALL 忽略手动切换并强制跟随系统时间
4. WHEN "跟随系统时间"关闭 THEN 应用 SHALL 允许用户手动切换昼夜模式
5. WHEN 用户打开设置菜单 THEN 菜单 SHALL 包含"切换昼夜"操作选项
6. WHEN "跟随系统时间"开启 THEN "切换昼夜"选项 SHALL 显示为禁用状态
7. WHEN "跟随系统时间"关闭 THEN "切换昼夜"选项 SHALL 显示为可用状态
8. WHEN 用户点击"切换昼夜" THEN 应用 SHALL 在白天和黑夜模式之间切换

### 需求 31

**用户故事:** 作为用户，我希望昼夜设置能够被保存，以便下次启动时保持我的偏好。

#### 验收标准

1. WHEN PufferPet应用启动 THEN 数据文件 SHALL 包含 auto_time_sync 字段
2. WHEN auto_time_sync为true THEN 应用 SHALL 启用自动时间同步
3. WHEN auto_time_sync为false THEN 应用 SHALL 使用手动设置的模式
4. WHEN 用户更改"跟随系统时间"设置 THEN 应用 SHALL 立即保存到数据文件
5. WHEN 用户手动切换昼夜模式 THEN 应用 SHALL 保存当前模式到数据文件
6. WHEN 应用启动且auto_time_sync为false THEN 应用 SHALL 加载上次保存的模式
7. WHEN 应用启动且auto_time_sync为true THEN 应用 SHALL 根据当前时间设置模式
8. WHEN 数据文件缺少昼夜设置 THEN 应用 SHALL 使用默认值（auto_time_sync=true）


## V5.5 工具需求（智能切片与万圣节生成工具）

### 需求 32

**用户故事:** 作为开发者，我希望有一个自动化工具来处理精灵图素材，以便快速生成游戏所需的所有图像资源。

#### 验收标准

1. WHEN 运行 process_assets.py THEN 工具 SHALL 读取 assets/puffer/ 目录下的精灵图
2. WHEN 处理精灵图 THEN 工具 SHALL 自动识别并移除白色背景
3. WHEN rembg库可用 THEN 工具 SHALL 优先使用rembg进行智能去底
4. WHEN rembg库不可用 THEN 工具 SHALL 回退到左上角颜色容差法去底
5. WHEN 切片精灵图 THEN 工具 SHALL 根据指定的行列数正确分割图像
6. WHEN 行数超出row_actions长度 THEN 工具 SHALL 忽略多余的行
7. WHEN 保存切片 THEN 工具 SHALL 使用格式 [prefix]_[action]_[frame].png
8. WHEN 处理单张图片 THEN 工具 SHALL 直接保存为 [filename].png

### 需求 33

**用户故事:** 作为开发者，我希望工具能自动生成万圣节版本的素材，以便支持昼夜循环系统的黑夜模式。

#### 验收标准

1. WHEN 处理每个切片 THEN 工具 SHALL 同时生成万圣节版本
2. WHEN 生成万圣节版本 THEN 工具 SHALL 将图像转换为灰度
3. WHEN 着色万圣节图像 THEN 工具 SHALL 使用荧光绿(#00FF00)或鬼火紫(#AA00FF)
4. WHEN 设置透明度 THEN 工具 SHALL 将整体透明度设为70%
5. WHEN 保存万圣节版本 THEN 工具 SHALL 使用格式 [prefix]_halloween_[action]_[frame].png
6. WHEN 处理单张图片 THEN 工具 SHALL 生成 [filename]_halloween.png
7. WHEN 万圣节处理完成 THEN 图像 SHALL 呈现幽灵般的发光效果
8. WHEN 所有处理完成 THEN 工具 SHALL 输出完成消息
