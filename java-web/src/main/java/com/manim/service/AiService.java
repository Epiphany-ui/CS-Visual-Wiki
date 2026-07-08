package com.manim.service;

import java.util.Map;

/**
 * AI 代码生成/修复业务接口
 * <p>封装对 Python AI 服务的 HTTP 调用</p>
 */
public interface AiService {

    /**
     * AI 自然语言生成 Manim 代码
     *
     * @param userPrompt  用户自然语言需求
     * @param knowledgeId 关联知识点 ID（可选）
     * @return { manimCode, description, suggestedParams }
     */
    Map<String, Object> generateCode(String userPrompt, Integer knowledgeId);

    /**
     * AI 代码智能修复
     *
     * @param errorLog 错误日志
     * @param oldCode  当前代码
     * @return { fixedCode, fixNote }
     */
    Map<String, Object> fixCode(String errorLog, String oldCode);
}
