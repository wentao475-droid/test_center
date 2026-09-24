# AMC竞赛模考 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有考试平台原型中新增 `AMC竞赛模考` 考试类型，补齐入口、AMC 首页、AMC 考试记录、AMC 结果页，并让考试过程完整复用牛剑 G5 组合卷流程。

**Architecture:** 以现有原生 HTML 原型页为基础，新增 AMC 专属页面文件；同时将 `学科考试.html` 与 `休息页.html` 中仅支持 G5 的组合卷流程参数化，扩展为同时支持 `g5` 与 `amc` 两种 flow。结果页不直接复用 G5 文件，而是新建 AMC 专属结果页，页面内容先与 G5 成绩分析保持一致，便于后续独立迭代。

**Tech Stack:** 原生 HTML / CSS / JavaScript、Bootstrap 5、jQuery、ECharts、`sessionStorage`

---

## Summary

- 新增考试入口卡片：在 `考试入口.html` 的雅思考试卡片后插入 `AMC竞赛模考`。
- 新增 AMC 首页：使用 G5 模考首页版式，改为 AMC 文案、AMC 题组数据、AMC 路由与 AMC session key。
- 复用组合卷考试流程：把 `学科考试.html` 与 `休息页.html` 中写死的 G5 流程泛化为 flow 配置映射，支持 `amc`。
- 新增 AMC 考试记录页：沿用 G5 记录页结构，但读取/展示 `amcExamRecord`，并跳转到 AMC 结果页。
- 新增 AMC 结果页：新建 AMC 专属文件，首版内容与 G5 成绩分析保持一致，但读取 `amcExamRecord` 并使用 AMC 页面链接。
- 个人中心本次不新建页面：AMC 相关页面中的“个人中心”继续保持占位，不纳入实现。

## Current State Analysis

### 入口与页面现状

- `考试入口.html` 当前开放入口只有 `牛剑G5笔试模考.html` 与 `雅思考试首页.html`，AMC 尚未出现。
- `牛剑G5笔试模考.html` 已具备 AMC 可复用的“轮次 + 科目筛选 + 组合卷开始考试”框架。
- `牛剑G5考试记录.html` 已具备“静态历史记录 + 最近完成记录从 `sessionStorage` 动态注入”的实现。
- `牛剑G5成绩分析.html` 已具备多科目 tabs、答题详情、知识点图表与 `latest=1` 动态读记录的能力。
- `雅思考试首页.html`、`考试记录.html` 与 G5 页面风格不同，但 AMC 需求明确要求考试过程与 G5 相同，因此 AMC 更适合沿 G5 分支落地。

### 共享流程现状

- `学科考试.html` 通过 URL `?flow=g5` 和 `sessionStorage.g5ExamSession` 识别 G5 组合卷流程。
- `学科考试.html` 提交中间子卷后跳转 `休息页.html?flow=g5`，全部完成后写入 `g5ExamRecord` 并跳转 `牛剑G5考试记录.html`。
- `休息页.html` 通过 `?flow=g5` 识别是否展示“子卷完成状态”，并固定跳回 `学科考试.html?flow=g5`。
- 以上两个共享页当前只支持 G5，AMC 若直接接入会缺少 session key、record key、完成后目标页等配置。

### 个人中心现状

- 仓库中不存在可直接复用的个人中心页面文件。
- `牛剑G5笔试模考.html`、`牛剑G5考试记录.html`、`牛剑G5成绩分析.html`、`雅思考试首页.html` 中的“个人中心”均为 `href="#"` 占位。
- 已确认本次 AMC 不新增个人中心页面，因此只需在 AMC 页面中保持相同占位方式，不额外扩 scope。

## Assumptions & Decisions

- AMC 页面命名采用显式中文名称，遵循现有项目文件命名风格。
- AMC 首页、记录页、结果页均走 AMC 专属文件，不与 G5 文件共用同一入口页面。
- AMC 考试过程与 G5 一致，但 session/record 存储 key 独立，避免与 G5 数据互相覆盖：
  - `amcExamSession`
  - `amcExamRecord`
- `学科考试.html` 与 `休息页.html` 不拆新文件，直接扩展为多 flow 共享页，减少重复代码与后续维护成本。
- AMC 结果页新建专属文件，但首版内容与 `牛剑G5成绩分析.html` 基本一致，只替换页面身份、链接、存储 key 与默认考试数据。
- 本次只保证从“考试入口 -> AMC 首页 -> AMC 考试过程 -> AMC 考试记录 -> AMC 结果页”的主路径闭环；不额外改造雅思/G5 页面顶部下拉中的考试类型列表，避免扩大影响面。

## Proposed Changes

### 1. 修改 `考试入口.html`

**Why**

- 这是用户进入各考试类型的统一入口，AMC 必须在此暴露出来。
- 用户要求 AMC 入口出现在“雅思考试”后面，需要精确控制卡片顺序。

**How**

- 在雅思考试卡片之后、前测考试卡片之前插入一张新的 `exam-card available`。
- 设置：
  - 标题：`AMC竞赛模考`
  - 描述：`AMC竞赛全真模拟`
  - `data-target="AMC竞赛模考.html"`
- 视觉上沿用现有入口卡片样式，不新增新的布局逻辑。

### 2. 新增 `AMC竞赛模考.html`

**Why**

- AMC 需要独立考试首页，与 G5 一样展示轮次、科目筛选和组合卷列表。
- 用户要求 AMC 过程与 G5 相同，因此最稳妥方案是以 G5 首页为模板做 AMC 分支。

**How**

- 以 `牛剑G5笔试模考.html` 为基础复制新文件。
- 替换页面身份相关文案：
  - `<title>`
  - hero 标题/说明
  - 侧边栏首页链接高亮
  - 顶部下拉默认项
- 修改链接：
  - 首页：`AMC竞赛模考.html`
  - 考试记录：`AMC竞赛模考考试记录.html`
  - 个人中心：保持 `#`
- 新建 AMC 题组数据数组，字段结构沿用 G5 的 `name / duration / round / subjects / subPapers / accent`。
- `startPaper()` 中改为：
  - `flow: 'amc'`
  - 写入 `sessionStorage.setItem('amcExamSession', ...)`
  - 清理 `sessionStorage.removeItem('amcExamRecord')`
  - 跳转 `学科考试.html?flow=amc`

### 3. 修改 `学科考试.html`

**Why**

- 这是 AMC 能否完整复用 G5 考试过程的核心共享页。
- 当前逻辑把 G5 的 session key、record key、完成跳转页写死，AMC 无法直接接入。

**How**

- 引入统一 flow 配置映射，例如：
  - `g5 -> { sessionKey, recordKey, breakUrl, recordUrl, contextLabel }`
  - `amc -> { sessionKey, recordKey, breakUrl, recordUrl, contextLabel }`
- 使用 URL 参数 `flow` 识别当前是否为组合卷流程，而不是只判断 `flow === 'g5'`。
- 读取当前 flow 对应的 session key，并生成统一的 `groupSession / groupRecordKey / flowConfig`。
- 保持现有页面 UI 不变，只让 AMC 复用：
  - 顶部考试上下文 pill
  - 当前子卷标题/剩余时间展示
  - 子卷提交后的中转跳转
  - 全部子卷完成后的记录写入与目标页跳转
- 提交完成记录时：
  - G5 继续写 `g5ExamRecord` 并跳到 `牛剑G5考试记录.html`
  - AMC 写 `amcExamRecord` 并跳到 `AMC竞赛模考考试记录.html`
- 确保原 G5 行为不回归，AMC 只是新增分支而不是替换旧逻辑。

### 4. 修改 `休息页.html`

**Why**

- AMC 过程和 G5 一样是多子卷连续考试，提交中间子卷后必须复用同一个过渡页。
- 当前页面只认 `flow=g5`，AMC 无法显示子卷状态和正确回跳。

**How**

- 引入与 `学科考试.html` 相同的 flow 配置思路，至少支持 `g5` 和 `amc`。
- 从当前 flow 对应的 session key 读取会话数据。
- 当 flow 为 `amc` 时：
  - 展示 AMC 子卷完成状态
  - 下一子卷按钮跳转 `学科考试.html?flow=amc`
- 保持雅思默认休息页逻辑完全不变。

### 5. 新增 `AMC竞赛模考考试记录.html`

**Why**

- AMC 需要独立的考试记录页，且用户要求与该考试类型配套。
- G5 记录页已有“静态样例 + 最近完成记录动态插入”的成熟结构，可直接复用。

**How**

- 以 `牛剑G5考试记录.html` 为基础复制新文件。
- 更新页面身份与链接：
  - 标题改为 AMC
  - 侧边栏首页跳到 `AMC竞赛模考.html`
  - 侧边栏记录页指向自身
  - 详情链接跳到 `AMC竞赛模考成绩分析.html`
  - 个人中心继续 `#`
- 顶部下拉默认值替换为 AMC 文案。
- 动态记录读取逻辑改为 `sessionStorage.getItem('amcExamRecord')`。
- 最近完成记录中的详情按钮改为：
  - `AMC竞赛模考成绩分析.html?exam=...&latest=1`
- 静态历史记录中的考试名称替换成 AMC 相关示例，便于页面语义一致。

### 6. 新增 `AMC竞赛模考成绩分析.html`

**Why**

- 用户已确认结果页要“新建 AMC 专属页，但内容先做成相同的”。
- 直接复用 G5 文件会限制后续 AMC 独立迭代，因此需要建立专属文件。

**How**

- 以 `牛剑G5成绩分析.html` 为基础复制新文件。
- 更新页面身份：
  - `<title>`、报告名称、顶部/侧边栏文案中的 G5 改为 AMC
  - 首页/记录页链接改为 AMC 页面
  - 个人中心继续 `#`
- 记录读取逻辑改为 `sessionStorage.getItem('amcExamRecord')`
- 保留 `latest=1` 参数逻辑，使 AMC 最新考试完成后也能注入动态数据。
- 新增 AMC 默认配置对象，结构保持与 G5 `defaultConfig` 一致，至少覆盖 AMC 首页中会出现的考试名称，避免 `exam` 参数找不到配置时回退到 G5。
- 首版图表、知识点、题目详情可完全沿用 G5 数据结构，只替换为 AMC 身份文案和默认 exam key。

### 7. AMC 页面内的占位与导航一致性

**Why**

- AMC 新增多个页面后，若侧边栏和顶部文案不统一，会破坏原型完整度。

**How**

- 在 `AMC竞赛模考.html`、`AMC竞赛模考考试记录.html`、`AMC竞赛模考成绩分析.html` 中统一：
  - 左侧导航当前页高亮
  - `考试首页 / 考试记录 / 真题案例 / 个人中心` 菜单结构
  - 个人中心继续保留 `href="#"` 占位
- `真题案例` 暂沿用 `学科考试.html` 链接，保持与 G5 现状一致，不做额外产品扩展。

## Verification Steps

- 登录后进入 `考试入口.html`，确认 `AMC竞赛模考` 卡片位于“雅思考试”后、“前测考试”前。
- 点击 AMC 入口，进入 `AMC竞赛模考.html`，确认 AMC 文案、轮次 tab、筛选器与按钮显示正常。
- 在 AMC 首页点击“开始考试”，确认：
  - 页面跳到 `学科考试.html?flow=amc`
  - `sessionStorage.amcExamSession` 已写入
  - 不覆盖 `g5ExamSession`
- 在 AMC 考试页提交首个子卷，确认跳到 `休息页.html?flow=amc`，并展示 AMC 子卷完成状态。
- 在 AMC 完成最后一个子卷后，确认：
  - `sessionStorage.amcExamRecord` 已写入
  - 跳转到 `AMC竞赛模考考试记录.html`
  - 最近完成区块显示 AMC 最新记录
- 在 AMC 记录页点击“查看详情”，确认跳到 `AMC竞赛模考成绩分析.html?exam=...&latest=1`，并读取 `amcExamRecord` 展示。
- 回归验证 G5：
  - 从 `牛剑G5笔试模考.html` 发起流程仍走 `flow=g5`
  - G5 中间提交仍到 `休息页.html?flow=g5`
  - G5 最终完成仍跳到 `牛剑G5考试记录.html`
- 视觉检查 AMC 相关三页，确认：
  - 侧边栏高亮正确
  - 页面文案没有残留 “牛剑G5”
  - 个人中心仍为占位，不出现死链报错

