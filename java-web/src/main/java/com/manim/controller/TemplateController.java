package com.manim.controller;

import com.manim.exception.BusinessException;
import com.manim.exception.UnauthorizedException;
import com.manim.pojo.*;
import com.manim.service.TaskService;
import com.manim.service.TemplateService;
import com.manim.service.UserService;
import com.manim.service.WorkService;
import com.manim.utils.UserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 模板创作 & 渲染任务接口
 * <p>对应接口文档：五、模板创作模块</p>
 */
@Tag(name = "模板创作接口")
@RestController
@RequestMapping("/api/v1")
public class TemplateController {

    @Autowired
    private TemplateService templateService;

    @Autowired
    private TaskService taskService;

    @Autowired
    private WorkService workService;

    @Autowired
    private UserService userService;

    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录或登录已过期");
        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("当前用户不存在");
        return user.getId();
    }

    // ==================== 5.1 获取模板列表 ====================

    @Operation(summary = "获取模板分类列表")
    @GetMapping("/template/list")
    public Result<List<Template>> getTemplateList(
            @RequestParam(value = "category", required = false) String category,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {
        List<Template> list = templateService.listByCategory(category, page, size);
        return Result.success(list);
    }

    // ==================== 5.2 获取模板详情 ====================

    @Operation(summary = "获取模板详情及参数配置 Schema")
    @GetMapping("/template/detail")
    public Result<Template> getTemplateDetail(
            @Parameter(description = "模板 ID") @RequestParam("templateId") Integer templateId) {
        Template template = templateService.getById(templateId);
        if (template == null) throw new BusinessException("模板不存在");
        return Result.success(template);
    }

    // ==================== 5.3 模板生成动画 ====================

    @Operation(summary = "模板参数生成动画（核心渲染接口）")
    @PostMapping("/template/generate")
    public Result<Map<String, Object>> generate(
            @Parameter(description = "动画需求文本") @RequestParam("userInput") String userInput,
            @Parameter(description = "最大重试次数（默认 3）")
            @RequestParam(value = "maxRetry", required = false, defaultValue = "3") Integer maxRetry) {

        if (userInput == null || userInput.trim().isEmpty())
            throw new BusinessException("userInput 不能为空");
        Integer userId = getCurrentUserId();
        Integer taskId = taskService.submitTask(userId, userInput.trim(), maxRetry);
        Map<String, Object> data = new HashMap<>();
        data.put("taskId", taskId);
        return Result.success(data);
    }

    // ==================== 5.4 查询渲染状态 ====================

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

    // ==================== 5.5 模板作品保存/发布 ====================

    @Operation(summary = "模板作品保存/发布")
    @PostMapping("/template/work/save")
    public Result<Map<String, Object>> saveTemplateWork(
            @Parameter(description = "渲染任务 ID") @RequestParam("taskId") Integer taskId,
            @Parameter(description = "作品标题") @RequestParam(value = "workTitle", required = false) String workTitle,
            @Parameter(description = "作品描述") @RequestParam(value = "workDesc", required = false) String workDesc,
            @Parameter(description = "是否公开") @RequestParam(value = "isPublic", defaultValue = "false") Boolean isPublic) {

        Integer userId = getCurrentUserId();

        // 查询渲染任务
        Task task = taskService.getTaskById(taskId);
        if (task == null) throw new BusinessException("任务不存在");
        if (!task.getUserId().equals(userId)) throw new BusinessException("无权操作该任务");

        // 创建作品
        Work work = new Work();
        work.setUserId(userId);
        work.setTitle(workTitle != null ? workTitle : "未命名作品");
        work.setDescription(workDesc);
        work.setVideoPath(task.getVideoPath());
        work.setManimCode(task.getUserInput());
        work.setIsPublic(isPublic ? 1 : 0);
        work.setStatus(1);
        Integer workId = workService.saveWork(work);

        Map<String, Object> data = new HashMap<>();
        data.put("workId", workId);
        return Result.success(data);
    }

    // ==================== 5.6 作品资源导出 ====================

    @Operation(summary = "作品资源导出（MP4/GIF/源码）")
    @GetMapping("/work/export")
    public Result<Map<String, Object>> exportWork(
            @Parameter(description = "作品 ID") @RequestParam("workId") Integer workId,
            @Parameter(description = "导出类型：mp4/gif/code") @RequestParam("exportType") String exportType) {

        Work work = workService.getById(workId);
        if (work == null) throw new BusinessException("作品不存在");

        String downloadUrl;
        switch (exportType) {
            case "mp4":
            case "gif":
                downloadUrl = work.getVideoPath();
                break;
            case "code":
                downloadUrl = "/api/v1/work/code/" + workId;
                break;
            default:
                throw new BusinessException("不支持的导出类型: " + exportType);
        }

        Map<String, Object> data = new HashMap<>();
        data.put("downloadUrl", downloadUrl);
        return Result.success(data);
    }

    // ==================== 补充：历史任务列表 ====================

    @Operation(summary = "查询当前用户全部历史任务")
    @GetMapping("/task/list")
    public Result<List<Task>> listTasks() {
        Integer userId = getCurrentUserId();
        return Result.success(taskService.listTasksByUserId(userId));
    }
}
