package com.manim.service.impl;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.manim.service.AiService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

/**
 * AI 代码生成/修复业务实现
 * <p>通过 HTTP 调用 Python AI 服务</p>
 */
@Service
public class AiServiceImpl implements AiService {

    private static final Logger log = LoggerFactory.getLogger(AiServiceImpl.class);

    @Value("${manim.ai.base-url}")
    private String aiBaseUrl;

    @Value("${manim.ai.read-timeout:180000}")
    private int readTimeout;

    @Override
    public Map<String, Object> generateCode(String userPrompt, Integer knowledgeId) {
        String url = aiBaseUrl + "/ai/generate";

        JSONObject requestBody = JSONUtil.createObj()
                .set("user_prompt", userPrompt);
        if (knowledgeId != null) {
            requestBody.set("knowledge_id", knowledgeId);
        }

        log.info("调用 AI 代码生成: POST {}, prompt={}", url, userPrompt);
        return callAiService(url, requestBody);
    }

    @Override
    public Map<String, Object> fixCode(String errorLog, String oldCode) {
        String url = aiBaseUrl + "/ai/fix";

        JSONObject requestBody = JSONUtil.createObj()
                .set("error_log", errorLog)
                .set("old_code", oldCode);

        log.info("调用 AI 代码修复: POST {}", url);
        return callAiService(url, requestBody);
    }

    /**
     * 通用 AI 服务调用
     */
    private Map<String, Object> callAiService(String url, JSONObject requestBody) {
        Map<String, Object> result = new HashMap<>();

        try {
            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(readTimeout)
                    .execute();

            if (response.getStatus() != 200) {
                log.warn("AI 服务返回异常: status={}", response.getStatus());
                result.put("manimCode", "// AI 服务暂不可用，请稍后重试");
                result.put("description", "服务异常: HTTP " + response.getStatus());
                return result;
            }

            JSONObject resp = JSONUtil.parseObj(response.body());
            result.put("manimCode", resp.getStr("code", ""));
            result.put("description", resp.getStr("description", ""));
            result.put("suggestedParams", resp.get("suggested_params"));

        } catch (Exception e) {
            log.error("调用 AI 服务异常", e);
            result.put("manimCode", "// AI 服务连接失败: " + e.getMessage());
            result.put("description", "网络异常，请检查 AI 服务是否启动");
        }
        return result;
    }
}
