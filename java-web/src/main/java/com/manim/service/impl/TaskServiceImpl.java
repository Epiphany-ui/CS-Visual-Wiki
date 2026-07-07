package com.manim.service.impl;

import cn.hutool.http.HttpRequest;
import cn.hutool.http.HttpResponse;
import cn.hutool.json.JSONObject;
import cn.hutool.json.JSONUtil;
import com.manim.dto.PythonResponse;
import com.manim.mapper.TaskMapper;
import com.manim.pojo.Task;
import com.manim.service.TaskService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

/**
 * 任务业务实现
 */
@Service
public class TaskServiceImpl implements TaskService {

    private static final Logger log = LoggerFactory.getLogger(TaskServiceImpl.class);

    @Autowired
    private TaskMapper taskMapper;

    @Value("${manim.ai.base-url}")
    private String aiBaseUrl;

    @Value("${manim.ai.generate-endpoint}")
    private String generateEndpoint;

    @Value("${manim.ai.connect-timeout}")
    private int connectTimeout;

    @Value("${manim.ai.read-timeout}")
    private int readTimeout;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Long submitTask(String userInput, Integer maxRetry) {
        // 1. 创建任务记录，状态为 0-等待中
        Task task = new Task();
        task.setUserInput(userInput);
        task.setMaxRetry(maxRetry != null ? maxRetry : 3);
        task.setStatus(0);
        task.setTryCount(0);
        taskMapper.insert(task);

        // 2. 异步调用 Python 服务渲染（不阻塞当前请求）
        Long taskId = task.getId();
        asyncRender(taskId, userInput, task.getMaxRetry());

        return taskId;
    }

    @Override
    public Task getTaskById(Long id) {
        return taskMapper.selectById(id);
    }

    @Override
    public List<Task> listAllTasks() {
        return taskMapper.selectList(null);
    }

    // ==================== 异步调用 Python 服务 ====================

    /**
     * 异步调用 Python AI 服务生成动画
     */
    @Async
    public void asyncRender(Long taskId, String userInput, Integer maxRetry) {
        // 1. 更新状态为 1-生成中
        Task task = taskMapper.selectById(taskId);
        if (task == null) {
            log.error("任务不存在，taskId={}", taskId);
            return;
        }
        task.setStatus(1);
        taskMapper.updateById(task);

        try {
            // 2. 构建请求 JSON
            JSONObject requestBody = JSONUtil.createObj()
                    .set("user_input", userInput)
                    .set("max_retry", maxRetry);

            String url = aiBaseUrl + generateEndpoint;
            log.info("调用 Python AI 服务: POST {}, 请求体: {}", url, requestBody);

            // 3. 发送 HTTP 请求（Hutool）
            HttpResponse response = HttpRequest.post(url)
                    .header("Content-Type", "application/json")
                    .body(requestBody.toString())
                    .timeout(readTimeout)
                    .execute();

            int httpStatus = response.getStatus();
            String responseBody = response.body();
            log.info("Python 服务响应状态码: {}, 响应体: {}", httpStatus, responseBody);

            // 4. 解析响应
            if (httpStatus != 200) {
                markTaskFailed(taskId, "Python 服务返回异常状态码: " + httpStatus + ", 响应: " + responseBody);
                return;
            }

            PythonResponse pythonResp = JSONUtil.toBean(responseBody, PythonResponse.class);
            updateTaskFromPythonResponse(taskId, pythonResp);

        } catch (Exception e) {
            log.error("调用 Python AI 服务异常", e);
            markTaskFailed(taskId, "调用 AI 服务网络异常: " + e.getMessage());
        }
    }

    /**
     * 根据 Python 返回结果更新任务
     */
    private void updateTaskFromPythonResponse(Long taskId, PythonResponse resp) {
        Task task = taskMapper.selectById(taskId);
        if (task == null) return;

        task.setGeneratedCode(resp.getCode());
        task.setTryCount(resp.getTryCount());
        task.setErrorLog(resp.getLog());

        if (resp.isSuccess()) {
            task.setStatus(2); // 成功
            task.setVideoUrl(resp.getVideoPath());
        } else {
            task.setStatus(3); // 失败
        }
        taskMapper.updateById(task);
    }

    /**
     * 标记任务为失败状态
     */
    private void markTaskFailed(Long taskId, String errorMsg) {
        Task task = taskMapper.selectById(taskId);
        if (task == null) return;
        task.setStatus(3);
        task.setErrorLog(errorMsg);
        taskMapper.updateById(task);
    }
}
