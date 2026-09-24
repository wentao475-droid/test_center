(function(window) {
    'use strict';

    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    function getBlockText(blocks, index) {
        return blocks[index] && blocks[index].text ? blocks[index].text : '暂无可用分析内容。';
    }

    function renderBlock(title, icon, text) {
        return [
            '<article class="ai-insight-block">',
            '<div class="ai-insight-block-title"><i class="fa ' + icon + '" aria-hidden="true"></i>' + title + '</div>',
            '<div class="ai-insight-block-text">' + escapeHtml(text) + '</div>',
            '</article>'
        ].join('');
    }

    function render(target, model) {
        if (!target || !model) {
            return;
        }
        var blocks = model.blocks || [];
        var advice = model.advice || [];
        target.innerHTML = [
            '<div class="ai-insight-head">',
            '<div class="ai-insight-title">' + escapeHtml(model.title || 'AI综合评价') + '</div>',
            '<div class="ai-insight-subtitle">' + escapeHtml(model.subtitle || '基于本次成绩、作答过程与能力表现生成') + '</div>',
            '</div>',
            '<section class="ai-insight-overview">',
            '<div class="ai-insight-overview-title"><i class="fa fa-magic" aria-hidden="true"></i>整体表现</div>',
            '<div class="ai-insight-overview-text">' + escapeHtml(model.summary) + '</div>',
            '</section>',
            '<div class="ai-insight-grid">',
            renderBlock('主要优势', 'fa-thumbs-up', getBlockText(blocks, 0)),
            renderBlock('主要问题', 'fa-question-circle', getBlockText(blocks, 1)),
            renderBlock('错题建议', 'fa-list-alt', getBlockText(blocks, 2)),
            '<section class="ai-insight-advice">',
            '<div class="ai-insight-advice-title"><i class="fa fa-clipboard" aria-hidden="true"></i>学习建议</div>',
            '<ul class="ai-insight-advice-list">',
            advice.map(function(item) { return '<li>' + escapeHtml(item) + '</li>'; }).join(''),
            '</ul>',
            '</section>',
            '</div>'
        ].join('');
    }

    window.AiInsight = { render: render };
})(window);
