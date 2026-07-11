package com.manim.service.impl;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.manim.dto.PythonResponse;
import com.manim.mapper.TaskMapper;
import com.manim.pojo.Task;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

/**
 * 异步渲染任务服务
 * <p>
 * 独立为单独的 {@link Service} bean，确保 {@link Async} 注解通过 Spring AOP 代理生效，
 * 避免在 {@link TaskServiceImpl} 中同类自调用绕过代理的问题。
 * </p>
 */
@Service
public class RenderTaskService {

    private static final Logger log = LoggerFactory.getLogger(RenderTaskService.class);

    @Autowired
    private TaskMapper taskMapper;

    @Value("${manim.ai.base-url}")
    private String aiBaseUrl;

    @Value("${manim.ai.generate-endpoint}")
    private String generateEndpoint;

    @Value("${manim.ai.read-timeout}")
    private int readTimeout;

    /**
     * 异步调用 Python AI 服务生成动画视频
     * <p>
     * 运行在独立的异步线程池中，不阻塞调用方。
     * 根据 Python 返回结果更新 task 表中的 video_path 或 error_log。
     * </p>
     *
     * @param taskId    任务主键
     * @param userInput 用户需求文本
     * @param maxRetry  Python 重试次数
     */
    @Async
    public void asyncRender(Integer taskId, String userInput, Integer maxRetry) {
        try {
            JSONObject requestBody = JSONUtil.createObj()
                    .set("requirement", userInput)
                    .set("max_retry", maxRetry);

            String url = aiBaseUrl + generateEndpoint;
            log.info("调用 Python AI 服务: POST {}, 请求体: {}", url, requestBody);

            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(readTimeout)
                    .execute();

            int httpStatus = response.getStatus();
            String responseBody = response.body();
            log.info("Python 服务响应状态码: {}, 响应体: {}", httpStatus, responseBody);

            if (httpStatus != 200) {
                markTaskFailed(taskId, "Python 服务返回异常状态码: " + httpStatus);
                return;
            }

            // Python 响应格式: {"code": 0, "data": {"success": true, "code": "...", "video_path": "...", ...}}
            // 先解包 data 层再映射到 PythonResponse
            JSONObject respJson = JSONUtil.parseObj(responseBody);
            JSONObject dataJson = respJson.getJSONObject("data");
            if (dataJson == null) {
                markTaskFailed(taskId, "Python 服务响应缺少 data 字段");
                return;
            }
            PythonResponse pythonResp = JSONUtil.toBean(dataJson, PythonResponse.class);
            updateTaskFromPythonResponse(taskId, pythonResp);

        } catch (Exception e) {
            log.error("调用 Python AI 服务异常", e);
            markTaskFailed(taskId, "调用 AI 服务网络异常: " + e.getMessage());
        }
    }

    /**
     * 根据 Python 返回结果更新任务状态
     */
    private void updateTaskFromPythonResponse(Integer taskId, PythonResponse resp) {
        Task task = taskMapper.selectById(taskId);
        if (task == null) return;

        task.setErrorLog(resp.getLog());

        if (resp.isSuccess()) {
            task.setStatus(1);               // 成功
            task.setVideoPath(resp.getVideoPath());
        } else {
            task.setStatus(2);               // 失败
        }
        taskMapper.updateById(task);
    }

    /**
     * 标记任务为失败状态（网络异常 / 非 200 响应）
     */
    private void markTaskFailed(Integer taskId, String errorMsg) {
        Task task = taskMapper.selectById(taskId);
        if (task == null) return;
        task.setStatus(2);                   // 失败
        task.setErrorLog(errorMsg);
        taskMapper.updateById(task);
    }
}
