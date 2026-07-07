package com.manim.controller;

import com.manim.pojo.Result;
import com.manim.pojo.Task;
import com.manim.service.TaskService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * JSON 业务接口控制器（统一前缀 /api）
 */
@Tag(name = "业务 JSON 接口")
@RestController
@RequestMapping("/api")
public class ApiController {

    @Autowired
    private TaskService taskService;

    /**
     * 提交动画生成任务
     */
    @Operation(summary = "提交动画生成任务", description = "入库后异步调用 Python 服务渲染，返回新任务 ID")
    @PostMapping("/submit")
    public Result<Long> submit(
            @Parameter(description = "用户动画需求文本", required = true)
            @RequestParam("userInput") String userInput,

            @Parameter(description = "最大重试次数（默认 3）")
            @RequestParam(value = "maxRetry", required = false, defaultValue = "3") Integer maxRetry) {

        // 校验参数
        if (userInput == null || userInput.trim().isEmpty()) {
            return Result.fail("userInput 不能为空");
        }

        Long taskId = taskService.submitTask(userInput.trim(), maxRetry);
        return Result.success(taskId);
    }

    /**
     * 根据任务 ID 查询单条任务（前端轮询用）
     */
    @Operation(summary = "查询任务状态", description = "前端轮询接口，根据任务 ID 查询最新状态")
    @GetMapping("/task/status/{id}")
    public Result<Task> getTaskStatus(
            @Parameter(description = "任务主键 ID", required = true)
            @PathVariable("id") Long id) {

        Task task = taskService.getTaskById(id);
        if (task == null) {
            return Result.fail("任务不存在，id=" + id);
        }
        return Result.success(task);
    }

    /**
     * 查询全部历史任务列表
     */
    @Operation(summary = "查询历史任务列表", description = "按创建时间倒序返回所有任务")
    @GetMapping("/task/list")
    public Result<List<Task>> listTasks() {
        List<Task> taskList = taskService.listAllTasks();
        return Result.success(taskList);
    }
}
