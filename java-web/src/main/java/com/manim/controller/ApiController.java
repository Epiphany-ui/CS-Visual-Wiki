package com.manim.controller;

import com.manim.exception.BusinessException;
import com.manim.exception.UnauthorizedException;
import com.manim.pojo.Result;
import com.manim.pojo.Task;
import com.manim.pojo.User;
import com.manim.service.TaskService;
import com.manim.service.UserService;
import com.manim.utils.UserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 动画任务接口
 * <p>
 * 当前登录用户由 {@link com.manim.filter.AuthFilter} 解析 JWT 后写入
 * {@link UserContext}，Controller 直接从中获取。
 * </p>
 */
@Tag(name = "动画任务接口")
@RestController
@RequestMapping("/api")
public class ApiController {

    @Autowired
    private TaskService taskService;

    @Autowired
    private UserService userService;

    /**
     * 从 UserContext 获取当前登录用户的 ID
     */
    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) {
            throw new UnauthorizedException("未登录或登录已过期");
        }
        User user = userService.findByUsername(username);
        if (user == null) {
            throw new UnauthorizedException("当前用户不存在");
        }
        return user.getId();
    }

    @Operation(summary = "提交生成任务", description = "需要 JWT 认证，入库后异步调用 Python 服务渲染视频")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "提交成功，返回任务 ID"),
            @ApiResponse(responseCode = "401", description = "未登录或令牌过期",
                    content = @Content(schema = @Schema(implementation = Result.class))),
            @ApiResponse(responseCode = "500", description = "业务参数错误",
                    content = @Content(schema = @Schema(implementation = Result.class)))
    })
    @PostMapping("/submit")
    public Result<Integer> submit(
            @Parameter(description = "动画需求文本", required = true)
            @RequestParam("userInput") String userInput,
            @Parameter(description = "最大重试次数（默认 3）")
            @RequestParam(value = "maxRetry", required = false, defaultValue = "3") Integer maxRetry) {

        if (userInput == null || userInput.trim().isEmpty()) {
            throw new BusinessException("userInput 不能为空");
        }

        Integer userId = getCurrentUserId();
        Integer taskId = taskService.submitTask(userId, userInput.trim(), maxRetry);
        return Result.success(taskId);
    }

    @Operation(summary = "查询单条任务（Vue 轮询用）", description = "校验任务归属当前登录用户")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "成功，返回任务详情"),
            @ApiResponse(responseCode = "401", description = "未登录或令牌过期",
                    content = @Content(schema = @Schema(implementation = Result.class))),
            @ApiResponse(responseCode = "500", description = "任务不存在或无权访问",
                    content = @Content(schema = @Schema(implementation = Result.class)))
    })
    @GetMapping("/task/status/{id}")
    public Result<Task> getTaskStatus(
            @Parameter(description = "任务 ID", required = true)
            @PathVariable("id") Integer id) {

        Integer userId = getCurrentUserId();
        Task task = taskService.getTaskById(id);
        if (task == null) {
            throw new BusinessException("任务不存在");
        }
        if (!task.getUserId().equals(userId)) {
            throw new BusinessException("无权访问该任务");
        }
        return Result.success(task);
    }

    @Operation(summary = "查询当前用户全部历史任务", description = "按创建时间倒序返回")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "成功，返回任务列表"),
            @ApiResponse(responseCode = "401", description = "未登录或令牌过期",
                    content = @Content(schema = @Schema(implementation = Result.class)))
    })
    @GetMapping("/task/list")
    public Result<List<Task>> listTasks() {
        Integer userId = getCurrentUserId();
        List<Task> taskList = taskService.listTasksByUserId(userId);
        return Result.success(taskList);
    }
}
