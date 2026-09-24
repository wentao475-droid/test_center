# AMC 时间效率分析模块 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 `AMC竞赛模考成绩分析.html` 中，于“AMC 知识点子节点导航”上方新增“时间效率分析”原型模块，并基于现有成绩分析页面做非重复的数据整合与展示。

**Architecture:** 本次仅规划前端原型，不扩展真实接口或存储契约。实现上在现有 AMC 成绩分析页中扩展单题 mock 数据结构，新增一个由“异常题效率表 + 分段时间分配诊断 + 策略画像”组成的时间效率模块，并将当前孤立的“平均单题用时”卡片并入新模块，避免重复展示。

**Tech Stack:** 原生 HTML / CSS / JavaScript、Bootstrap 5、ECharts、页面内 mock 数据结构

---

## Summary

- 仅修改 `AMC竞赛模考成绩分析.html`，不新增页面。
- 在 `AMC 知识点子节点导航` 上方插入新的“时间效率分析”模块。
- 将现有 `已作答题目单题平均用时` 从 `insight-wrap` 中移除或并入新模块，不再单独展示。
- 扩展当前 `details` mock 数据，为每题增加时间效率分析所需字段。
- 使用“题目级时间效率 + 分段耗时结构 + 策略画像”三层内容替代当前单点时间展示。
- 保留现有顶部 `正确率 / 用时 / 试卷分数 / 成绩` 与 `question-map`、`答题详情`，新模块只补充它们没有表达的“时间效率关系”。

## Current State Analysis

### 当前页面结构

- 目标文件为 `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`。
- 主分析区 `analysis-card` 当前包含：
  - 顶部总体统计 `stats-row`
  - 对错图例与 `question-map`
  - `insight-wrap` 中的单个 `time-metric-card`
  - 知识点图表模块 `knowledge-chart-card`
  - 知识点子节点导航 `knowledge-card-section`
- `AMC 知识点子节点导航` 位于 `knowledge-chart-card` 内部的末尾，在 `knowledge-card-divider` 下方。

### 当前已有时间相关内容

- 已有总体时间数据：
  - `statDuration`：整卷/当前科目用时
  - `avgAnsweredTime`：已作答题目单题平均用时
- 已有正确率相关数据：
  - `statAccuracy`
  - `question-map`
  - `questionDetails` 中每题对错详情
- 当前时间数据表达方式偏粗，只能看到“总共用了多久”和“平均每题多久”，看不到：
  - 哪些题“快且对”
  - 哪些题“慢但对”
  - 哪些题“慢且错”
  - 哪个题段时间分配失衡

### 当前数据结构缺口

- 现有 `details` 数据项只有：
  - `title`
  - `stem`
  - `studentAnswer`
  - `correctAnswer`
  - `knowledge`
  - `status`
- 当前并没有前端 mock 字段来承载截图中需要的：
  - 题号
  - 模块
  - 难度层
  - 单题作答时间
  - 推荐用时
  - 单题得分 / 满分
- 因此若要实现截图中的时间效率分析，必须先扩展前端 mock 数据结构。

## Assumptions & Decisions

- 本次为“仅前端原型”，不设计后端 API、数据库字段或 sessionStorage 新协议。
- “不要重复展示和分析相同的数据”的落地原则：
  - 顶部 `stats-row` 继续保留整体 `用时 / 正确率 / 分数 / 成绩`
  - `question-map` 继续保留题目级对错分布
  - 新模块只展示“时间和结果之间的关系”
  - 现有 `time-metric-card` 不再独立保留，能力被新模块吸收
- 新模块位置固定为：
  - `knowledge-chart-stage` 之后
  - `knowledge-card-divider` 之前
  - 即视觉上位于“AMC 知识点子节点导航”上方
- 时间效率分析模块按截图精神拆成 3 块：
  1. 时间效率全景表
  2. 时间分配结构
  3. 策略人格画像
- 题目分段默认按 AMC 常见卷结构做前端原型分组：
  - 基础段：1-10
  - 进阶段：11-20
  - 冲刺段：21-25
- 时间效率判定规则在前端原型中固定，不依赖真实后端：
  - `时间金矿`：做对，且实际用时 <= 推荐用时
  - `时间陷阱`：做对，但实际用时显著超出推荐用时
  - `时间黑洞`：做错，且实际用时显著超出推荐用时
  - `时间漏洞`：做错，且实际用时明显低于推荐用时或快速放弃
- “效率指数”直接采用截图给出的原型定义：
  - `效率指数 = 得分 / 用时（分/分钟）`

## Proposed Changes

### 1. 调整页面布局，只保留一个统一的时间分析入口

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 删除或替换当前 `insight-wrap` 内的 `time-metric-card`。
- 在 `knowledge-chart-card` 内、`knowledge-card-divider` 之前新增一个 `time-efficiency-section`。

**Why**

- 当前“平均单题用时”与截图里的新模块会重复表达时间维度。
- 用户明确要求“结合已有成绩分析内容，不要重复展示和分析相同的数据”。

**How**

- 保留顶部总览统计不动。
- 将“平均单题用时”从单卡片升级为新模块中的一个子结果或辅助说明，不再单独占位。
- 新模块结构建议：

```html
<div class="time-efficiency-section">
  <div class="time-efficiency-head">
    <div class="time-efficiency-title">时间效率分析</div>
    <div class="time-efficiency-desc">回答：我在哪些题目上浪费了时间？哪些题目做得又快又好？</div>
  </div>

  <div class="time-efficiency-panel" id="timeEfficiencyOverview"></div>
  <div class="time-allocation-panel" id="timeAllocationPanel"></div>
  <div class="time-persona-panel" id="timePersonaPanel"></div>
</div>
```

### 2. 扩展当前 `details` mock 数据结构，补齐时间效率分析字段

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 为每个 `details[]` 项新增时间效率分析所需字段。

**Why**

- 截图中的模块核心是题目级时间数据，而当前前端 mock 只有对错，没有“时间-得分-模块”三元关系。

**How**

- 每题详情结构扩展为：

```js
{
  questionNo: 3,
  module: '代数',
  difficultyTier: '基础',
  timeSpentSec: 60,
  recommendedTimeSec: 120,
  earnedScore: 6,
  fullScore: 6,
  title: '1. 单选题',
  stem: '...',
  studentAnswer: 'B',
  correctAnswer: 'D',
  knowledge: '#Function Transformations',
  status: 'wrong'
}
```

- 至少对 AMC 当前会展示的这些分支补齐字段：
  - `AMC 8 综合模考`
  - `AMC 10 综合模考`
  - `AMC 10 综合模考 -> paperTabs`
  - `AMC 12 综合模考`

- 若当前某分支仍只保留 2-3 道样例题，则前端原型内至少保证这些样例题具备完整字段，后续表格只基于这些样例题渲染。

### 3. 新增题目级时间效率计算函数

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 增加专门的时间效率计算工具函数，不混在现有 `renderQuestionDetails()` 逻辑里。

**Why**

- 现有页面已包含知识点、答题详情、图表切换逻辑；时间效率分析若直接写在渲染函数里会进一步放大单文件复杂度。

**How**

- 新增函数建议：

```js
function buildTimeEfficiencyRows(details) {}
function classifyTimeEfficiency(row) {}
function buildTimeAllocationGroups(details) {}
function buildStrategyPersona(details) {}
function formatSecondsToMinuteText(seconds) {}
function calcOverrunRate(timeSpentSec, recommendedTimeSec) {}
function calcEfficiencyIndex(earnedScore, timeSpentSec) {}
```

- 计算规则：
  - `用时`：由 `timeSpentSec` 转为“X分Y秒”或“X分钟”
  - `推荐用时`：由 `recommendedTimeSec` 转展示文本
  - `超时率 = (实际用时 - 推荐用时) / 推荐用时`
  - `得分 = earnedScore`
  - `效率指数 = earnedScore / (timeSpentSec / 60)`

- 类型判定阈值建议：
  - `时间金矿`：`earnedScore === fullScore && timeSpentSec <= recommendedTimeSec`
  - `时间陷阱`：`earnedScore === fullScore && timeSpentSec > recommendedTimeSec * 1.3`
  - `时间黑洞`：`earnedScore === 0 && timeSpentSec > recommendedTimeSec * 1.3`
  - `时间漏洞`：`earnedScore === 0 && timeSpentSec < recommendedTimeSec * 0.6`

### 4. 渲染“时间效率全景表”，但避免重复题目详情

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 新增一个表格模块，展示题目级时间效率信息。

**Why**

- 这是截图中最核心的内容，但不能和下方“答题详情”完全重复。

**How**

- 表格建议字段：
  - 题号
  - 模块
  - 难度层
  - 用时
  - 推荐用时
  - 超时率
  - 得分
  - 效率指数
  - 类型判定

- 为避免与 `questionDetails` 重复：
  - 这里不再展示题干、学生答案、正确答案
  - 只展示“时间-得分-效率”的摘要信息
  - 默认按“最值得关注”的题排序：`时间黑洞`、`时间陷阱` 优先

- 前端原型可以只渲染“异常题 + 代表题”，而不是把所有题全部铺满表格。

### 5. 新增“时间分配结构”模块，做分段诊断而不是重复总用时

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 新增一个按题号分段的时间分配表，呼应截图中第 2 块内容。

**Why**

- 顶部已展示总用时，新模块不应该再重复“总共用时多少”，而应回答“时间花在了哪里”。

**How**

- 基于 `questionNo` 分段：
  - 基础段：1-10
  - 进阶段：11-20
  - 冲刺段：21-25

- 每段输出：
  - 你的用时
  - 推荐用时
  - 偏差
  - 得分占比
  - 诊断

- 诊断文案由规则生成，例如：
  - “基础段投入明显偏高，但得分回报一般，建议压缩简单题停留时间”
  - “进阶段时间控制较稳，是当前整卷效率最优区间”
  - “冲刺段时间投入不足且得分偏低，存在提前放弃倾向”

- 这部分不重复顶部 `statDuration`，而是强调“结构失衡”。

### 6. 新增“策略人格画像”模块，承接截图中的总结型输出

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 在时间分配表之后增加“策略人格画像”摘要。

**Why**

- 该块是对上方题目级和分段级分析的归纳，能把时间效率模块从“数据展示”升级为“可解释建议”。

**How**

- 依据题目级和分段级统计生成 1 个主标签 + 2-3 条解释。
- 画像标签建议固定枚举：
  - `保守型`
  - `自洽型`
  - `均衡型`
  - `孤注型`

- 输出示例：

```html
<div class="time-persona-card persona-balanced">
  <div class="persona-title">策略人格：均衡型</div>
  <ul>
    <li>基础段时间投入与得分较匹配</li>
    <li>中段存在 1-2 道“时间陷阱”题</li>
    <li>冲刺段提前放弃倾向不明显</li>
  </ul>
</div>
```

- 该块不重复知识点模块中的评语，专注于“时间策略”。

### 7. 清理重复文案与无效旧变量

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 完成新模块接入后，清理当前页面中不再需要的旧时间分析残留。

**Why**

- 当前文件已存在：
  - 注释掉的 `timeComment`
  - 单点 `avgAnsweredTime` 卡片
  - 相关 DOM 引用
- 若不清理，后续会出现重复分析或死代码。

**How**

- 删除或迁移：
  - `insight-wrap > time-metric-card`
  - `avgAnsweredTime / avgAnsweredTimeMeta / avgAnsweredTimeRule` 相关 DOM 绑定
  - 已废弃的 `timeComment` 注释块
- 将“平均单题用时”作为新模块中的辅助计算项，而不是独立卡片。

## Verification Steps

- 打开 `AMC竞赛模考成绩分析.html`，确认“时间效率分析”模块位于 `AMC 知识点子节点导航` 上方。
- 确认原有顶部 `正确率 / 用时 / 分数 / 成绩` 仍保留，新模块没有再次重复这些总览数字。
- 确认原 `已作答题目单题平均用时` 卡片不再单独出现。
- 切换不同 `subject` / `paperTab` 时：
  - 时间效率全景表随当前分支刷新
  - 分段时间分配表随当前分支刷新
  - 策略人格画像随当前分支刷新
- 确认“答题详情”仍正常工作，没有因 `details` 结构扩展而报错。
- 确认知识点图表和“AMC 知识点子节点导航”仍正常显示，没有被新模块打断。
- 检查页面脚本：
  - 无失效 DOM 引用
  - 无重复时间分析模块
  - 新增 mock 数据字段都被实际消费

