package com.manim.controller;

import com.manim.exception.BusinessException;
import com.manim.exception.UnauthorizedException;
import com.manim.pojo.Result;
import com.manim.pojo.Task;
import com.manim.pojo.User;
import com.manim.pojo.Work;
import com.manim.service.TaskService;
import com.manim.service.UserService;
import com.manim.utils.UserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 模板创作 & 渲染任务接口
 * <p>对应接口文档：五、模板创作模块 + 渲染状态</p>
 */
@Tag(name = "模板创作接口")
@RestController
@RequestMapping("/api/v1")
public class TemplateController {

    @Autowired
    private TaskService taskService;

    @Autowired
    private UserService userService;

    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录或登录已过期");
        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("当前用户不存在");
        return user.getId();
    }

    @Operation(summary = "模板参数生成动画（核心渲染接口）")
    @PostMapping("/template/generate")
    public Result<Integer> generate(
            @Parameter(description = "动画需求文本") @RequestParam("userInput") String userInput,
            @Parameter(description = "最大重试次数（默认 3）") @RequestParam(value = "maxRetry", required = false, defaultValue = "3") Integer maxRetry) {

        if (userInput == null || userInput.trim().isEmpty()) throw new BusinessException("userInput 不能为空");
        Integer userId = getCurrentUserId();
        Integer taskId = taskService.submitTask(userId, userInput.trim(), maxRetry);
        return Result.success(taskId);
    }

    @Operation(summary = "查询渲染任务状态")
    @GetMapping("/render/status")
    public Result<Task> getRenderStatus(
            @Parameter(description = "任务 ID") @RequestParam("taskId") Integer taskId) {
        Integer userId = getCurrentUserId();
        Task task = taskService.getTaskById(taskId);
        if (task == null) throw new BusinessException("任务不存在");
        if (!task.getUserId().equals(userId)) throw new BusinessException("无权访问该任务");
        return Result.success(task);
    }

    @Operation(summary = "查询当前用户全部历史任务")
    @GetMapping("/task/list")
    public Result<List<Task>> listTasks() {
        Integer userId = getCurrentUserId();
        return Result.success(taskService.listTasksByUserId(userId));
    }
}
