# AMC 时间分配结构标签化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 `AMC竞赛模考成绩分析.html` 中“时间分配结构”模块的“诊断”列改造成与“时间效率全景表”一致的“类型判定标签 + 图例解释”形式，不再逐行展示长文本诊断。

**Architecture:** 仅修改 `AMC竞赛模考成绩分析.html` 的前端原型展示逻辑，不改后端或存储契约。保留当前分段统计计算方式，但把 `buildTimeAllocationDiagnosis()` 产出的长文本诊断切换为统一的类型枚举，再通过已有 `time-type-badge` 标签样式和新增图例说明完成解释，保证两个时间模块的判定语言一致。

**Tech Stack:** 原生 HTML / CSS / JavaScript、现有 `time-type-badge` 样式体系

---

## Summary

- 仅修改 `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`。
- 将“时间分配结构”表格最后一列从 `诊断` 文本改为 `类型判定` 标签。
- 为“时间分配结构”增加与全景表同风格的图例说明，用统一枚举解释每种标签含义。
- 保留当前 `基础段 / 进阶段 / 冲刺段` 的统计分组逻辑。
- 不保留逐行长文本诊断，避免和图例解释重复。

## Current State Analysis

### 当前实现位置

- 文件：`d:\AI学习\test_center\AMC竞赛模考成绩分析.html`
- 当前“时间分配结构”渲染函数：
  - `renderTimeAllocationPanel(details)`
- 当前时间分配结构计算函数：
  - `buildTimeAllocationGroups(details)`
  - `buildTimeAllocationDiagnosis(group)`

### 当前展示方式

- “时间效率全景表”当前已经使用：
  - `typeMeta`
  - `time-type-badge`
  - 标签类名：`gold / trap / blackhole / leak`
- “时间分配结构”当前仍使用：
  - 表头：`诊断`
  - 每行单元格：`group.diagnosis`
  - 展示的是一段中文长句

### 当前问题

- 两个时间模块的判定表达不统一：
  - 全景表是标签化
  - 分段结构是文字描述
- 用户明确要求此处也改成和全景表一样的表现形式：
  - 先得出类型判定
  - 对应显示标签
  - 再给出统一图例解释

## Assumptions & Decisions

- 本次只改“时间分配结构”模块，不改“时间效率全景表”的现有判定结构。
- 诊断长文案不再逐行显示，改为：
  - 表格列中显示类型标签
  - 模块内统一显示图例解释
- 分段判定沿用与现有逻辑一致的时间偏差和得分占比思路，但产出枚举标签而不是句子。
- 为了与全景表统一，分段类型也复用现有四个标签体系：
  - `时间金矿`
  - `时间陷阱`
  - `时间黑洞`
  - `时间漏洞`
- 图例说明不重复逐行解释，而是集中放在“时间分配结构”标题下方或表格上方。

## Proposed Changes

### 1. 调整“时间分配结构”模块文案与布局

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 在“时间分配结构”模块中新增一段图例说明区域。
- 将表头中的 `诊断` 改为 `类型判定`。

**Why**

- 用户要求这里和“时间效率全景表”保持一致，标签和图例应成为主表达方式。

**How**

- 在 `timeAllocationPanel` 对应模块中，渲染结构从：

```html
<table>
  <thead>
    <tr>
      <th>区间</th>
      <th>你的用时</th>
      <th>推荐用时</th>
      <th>偏差</th>
      <th>得分占比</th>
      <th>诊断</th>
    </tr>
  </thead>
</table>
```

- 改为：

```html
<div class="time-legend-copy">
  <span class="time-type-badge gold">时间金矿</span>
  <span>区段时间投入合理，且得分回报高。</span>
  ...
</div>

<table>
  <thead>
    <tr>
      <th>区间</th>
      <th>你的用时</th>
      <th>推荐用时</th>
      <th>偏差</th>
      <th>得分占比</th>
      <th>类型判定</th>
    </tr>
  </thead>
</table>
```

### 2. 将分段诊断函数从“输出句子”改为“输出类型”

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 替换 `buildTimeAllocationDiagnosis(group)` 的职责。

**Why**

- 当前函数返回整句中文，会导致表格继续以长文本方式展示，不符合新的交互要求。

**How**

- 将现有：

```js
function buildTimeAllocationDiagnosis(group) {
  return '投入明显偏高，但得分回报一般...';
}
```

- 改为例如：

```js
function classifyTimeAllocationGroup(group) {
  if (Math.abs(group.overrunRate) <= 0.15 && group.scoreRate >= 0.6) return 'gold';
  if (group.overrunRate > 0.25 && group.scoreRate < 0.5) return 'blackhole';
  if (group.overrunRate > 0.15) return 'trap';
  return 'leak';
}
```

- 并在 `buildTimeAllocationGroups(details)` 中挂载：

```js
group.typeKey = classifyTimeAllocationGroup(group);
group.typeMeta = getTimeTypeMeta(group.typeKey);
```

### 3. 渲染时间分配结构标签列

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 将 `renderTimeAllocationPanel(details)` 最后一列改成标签渲染。

**Why**

- 这是用户当前最直接提出的改动目标。

**How**

- 现有：

```js
'<td class="time-diagnosis">' + escapeHtml(group.diagnosis) + '</td>'
```

- 改为：

```js
'<td><span class="time-type-badge ' + group.typeMeta.className + '">' + escapeHtml(group.typeMeta.label) + '</span></td>'
```

- 表头同步改为：

```js
'<thead><tr><th>区间</th><th>你的用时</th><th>推荐用时</th><th>偏差</th><th>得分占比</th><th>类型判定</th></tr></thead>'
```

### 4. 为时间分配结构补统一图例说明

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 增加一段面向“区段级分析”的图例说明。

**Why**

- 用户要求“对应有个标签，然后给出图例解释即可”。
- 若没有图例，标签含义对用户不够直观。

**How**

- 使用与全景表一致的标签样式，图例文案可针对“区段级”表述重写：
  - `时间金矿`：区段时间投入合理，且得分回报高，建议保持
  - `时间陷阱`：区段耗时偏高，但仍有得分，说明节奏偏慢
  - `时间黑洞`：区段耗时过高且得分回报低，应优先调整策略
  - `时间漏洞`：区段投入不足且得分偏低，存在提前放弃或分配失衡

- 图例位置建议：
  - 放在“时间分配结构”标题说明下方
  - 放在表格上方

### 5. 清理旧的分段诊断残留

**Files:**
- Modify: `d:\AI学习\test_center\AMC竞赛模考成绩分析.html`

**What**

- 清理不再使用的 `diagnosis` 文案字段和相关样式依赖。

**Why**

- 新方案不再逐行输出长文本诊断，继续保留会造成死代码。

**How**

- 删除或停用：
  - `buildTimeAllocationDiagnosis()` 返回句子逻辑
  - `group.diagnosis`
  - `time-diagnosis` 在时间分配表中的渲染依赖

- 如果 `time-diagnosis` 样式只剩全局残留且无其他用途，可一并移除；若仍被别处使用，则仅停止在此模块引用。

## Verification Steps

- 打开 `AMC竞赛模考成绩分析.html`，确认“时间分配结构”表头已从 `诊断` 改为 `类型判定`。
- 确认每个分段最后一列显示为标签，而不是长文本句子。
- 确认“时间分配结构”模块内存在图例说明，并与全景表的标签体系一致。
- 确认图例只做统一解释，不在每行重复长句。
- 确认 `基础段 / 进阶段 / 冲刺段` 的统计值本身未受影响：
  - 你的用时
  - 推荐用时
  - 偏差
  - 得分占比
- 检查脚本与样式：
  - 无对已删除 `group.diagnosis` 的残留引用
  - 无表格列数错位
  - 无新增语法错误

