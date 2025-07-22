
## Task

Build an AI Avatar Platform that has the following components and fuctions:

## Components

### 数字人制造车间
#### 一个直播数字人agent
它有知识库储备和通用的知识注入功能

#### 通用数字人组装
包括后台的编辑管理能力，具体编辑管理能力TBD

#### 数字人内容生成
从“一句话“由大模型生成

#### 数字人任务编排
通过n8n workflow编排数字人的任务

### 内容工厂
#### 内容导入Agent
通过API, MCP导入外部内容，由Agent开发实现，使用包括WebSurfer, WebCrawler这样的工具

#### 文案生成Agent
由Agent通过大模型、“工具增强”、n8n的能力生成，内容可能来自：
1. 通过“一句话”
2. 根据导入的内容，进行再加工微创新 
3. 模仿某个大"IP"的风格重塑导入内容

#### 视频制作一条龙Agent
通过“工具增强“和n8n的Workflow能力开发实现，更多细节待定TBD

### 生态平台接入
#### 接入发布一条龙Agent
通过n8n Workflow和WebSurfer实现接入发布一条龙服务

### 数据分析
提供直播数字人的相关数据及数据分析

## Example Case

### LiveFootballAvatar
Build a project called "LiveFootballAvatar" that:
- Ingests real-time football match data
- Uses a language model to generate commentary
- Sends commentary to a live avatar (e.g. DUIX or SenseAvatar)
- Integrates with MCP server to manage function calls
- Triggers actions via n8n workflows (e.g. update avatar status, send messages)

