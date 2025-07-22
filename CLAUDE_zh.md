# CLAUDE_zh.md

本文件为Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 项目概述

**AI数字人平台 (commagents)** - 一个综合性AI驱动的数字人平台，用于创建、管理和运营数字人进行内容生成和直播。该平台由四个主要组件组成：数字人制造车间、内容工厂、生态系统集成和数据分析。

**足球直播数字人(LiveFootballAvatar)**作为初始示例实现，展示了平台通过实时足球解说生成的能力。

## 平台架构

### 1. 数字人制造车间

#### 直播数字人智能体
- **知识库管理**: 存储和注入数字人个性的知识
- **通用知识集成**: 动态知识更新和上下文感知

#### 通用数字人组装
- **后台管理**: 数字人配置的管理界面
- **数字人定制**: 个性、声音、外观和行为设置

#### 数字人内容生成
- **一句话生成**: 从简单提示生成完整的数字人响应
- **LLM驱动**: 使用配置的语言模型进行自然内容创建

#### 数字人任务编排
- **n8n工作流集成**: 自动化数字人任务和响应
- **事件驱动动作**: 基于外部事件和调度的触发

### 2. 内容工厂

#### 网红内容采集智能体
- **WebSurfer集成**: 社交媒体平台自动浏览和内容抓取
- **多媒体提取**: 下载和处理视频博客、图片和短视频
- **内容分类管理**: 按类型、日期和互动指标组织采集内容
- **平台覆盖**: TikTok、Instagram、YouTube、Twitter等主要平台

#### 风格分析智能体
- **内容风格提取**: 分析视觉美学、语调、主题和展示模式
- **AI模式识别**: 使用计算机视觉和NLP识别独特风格元素
- **趋势识别**: 提取重复主题、话题和内容格式
- **个性建模**: 创建全面的网红个性和品牌档案

#### 文案生成智能体
- **风格匹配生成**: 制作模仿识别网红风格的内容
- **多格式创建**: 生成视频博客、图片、短视频和社交媒体帖子
- **品牌一致性**: 跨内容类型保持连贯的声音和视觉身份
- **工具增强**: 使用LLM + 外部工具 + n8n工作流 + AI图像/视频生成

#### 视频制作一条龙智能体
- **端到端视频创建**: 从脚本到最终视频
- **n8n工作流集成**: 自动化制作流水线
- **工具集成**: 外部视频处理工具

### 3. 生态平台接入

#### 社交媒体发布智能体
- **多平台分发**: 自动发布到TikTok、Instagram、YouTube、Twitter等
- **平台优化**: 为每个社交媒体平台适配内容格式和元数据
- **调度和时间**: 基于观众互动模式优化发布时间
- **跨平台策略**: 协调多个平台的内容发布
- **WebSurfer集成**: 平台特定发布逻辑和API管理

### 4. 数据分析
- **直播数字人指标**: 性能跟踪和分析
- **用户参与**: 交互和响应分析
- **内容性能**: 成功指标和优化洞察

## 当前实现（足球直播数字人示例）

### 核心架构

- **基于MetaGPT的多智能体系统**: 使用MetaGPT的Team框架和专门的Role和Action类
- **事件驱动解说**: 比赛事件根据事件类型前缀路由到相应智能体
- **数字人集成**: 生成的解说通过情感映射发送到数字人API
- **n8n工作流集成**: 触发外部工作流进行数字人控制和消息传递

## 智能体角色

### 实况解说员 (`agents/playbyplay_commentator.py`)
- 处理一般比赛事件（进球、扑救、点球）
- 生成生动、富有激情的1-2句解说
- 无特定前缀事件的默认接收者

### 战术分析师 (`agents/tactical_analyst.py`)
- 处理带有"TACTICAL:"前缀的事件
- 提供2-3句阵型和战术的战略分析
- 专注于战术解释

### 节目主持人 (`agents/show_host.py`)
- 处理带有"TRANSITION:"前缀的事件
- 调节其他解说员之间的讨论流程
- 提供平滑过渡和总结

## 核心组件

### 足球解说团队 (`agents/football_commentary_team.py`)
主要编排类，功能包括：
- 初始化包含所有三个智能体的MetaGPT团队
- 根据前缀将事件路由到相应智能体
- 管理解说生成工作流

### 事件路由逻辑
```python
send_to = "PlayByPlayCommentator"  # 默认
if event.startswith('TACTICAL:'):
    send_to = "TacticalAnalyst"
elif event.startswith('TRANSITION:'):
    send_to = "ShowHost"
```

## 配置

### 主配置 (`config/config2.example.yaml`)
标准MetaGPT配置，涵盖：
- LLM设置 (OpenAI/Azure/等)
- 角色特定LLM配置
- 嵌入、搜索、浏览器自动化设置
- TTS集成 (Azure, iFlytek)

### 足球数字人配置 (`config/football_avatar.yaml`)
项目特定设置：
- 数字人API端点配置
- 不同事件类型的情感映射
- n8n webhook URL和事件类型
- MCP服务器设置

## 开发命令

### 平台开发
```bash
# 运行完整平台（实现后）
python main.py

# 运行特定组件
python agents/avatar/base_avatar_agent.py
python agents/content/content_import_agent.py
python workflows/workflow_manager.py
```

### 当前示例（足球直播数字人）
```bash
# 运行足球解说系统
python agents/football_commentary_team.py

# 运行当前实现的测试
python test_commentary.py
```

### 配置设置
1. 复制 `config/config2.example.yaml` 到 `config/config2.yaml`
2. 更新配置文件中的API密钥和端点
3. 在 `config/football_avatar.yaml` 中配置数字人API端点

## 集成点

### MCP服务器集成
- 服务器URL: `http://localhost:8080`
- 工具: `process_match_event`, `trigger_avatar`

### n8n工作流
- Webhook: `http://localhost:5678/webhook/match`
- 支持的事件类型: goal, card, substitution, save, halftime, tactical, stat, transition, penalty

### 数字人API
- 端点: `http://localhost:8000/speak`
- 载荷格式: `{"text": "解说内容", "emotion": "excited", "language": "Chinese"}`

## 开发注意事项

- 系统全程使用async/await模式
- 每个智能体都扩展MetaGPT的Role类，具有自定义Action实现
- 事件处理通过MetaGPT的Team.run()方法处理，带有目标消息路由
- 所有智能体都监听Message类型以触发其动作