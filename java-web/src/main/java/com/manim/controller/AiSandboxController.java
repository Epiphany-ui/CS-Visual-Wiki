package com.manim.controller;

import com.manim.exception.BusinessException;
import com.manim.exception.UnauthorizedException;
import com.manim.pojo.*;
import com.manim.service.*;
import com.manim.utils.UserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * AI 沙箱创作模块接口
 * <p>对应接口文档：六、AI 沙箱创作模块</p>
 */
@Tag(name = "AI 沙箱创作接口")
@RestController
@RequestMapping("/api/v1")
public class AiSandboxController {

    @Autowired
    private AiService aiService;

    @Autowired
    private TaskService taskService;

    @Autowired
    private SandboxDraftService sandboxDraftService;

    @Autowired
    private WorkService workService;

    @Autowired
    private UserService userService;

    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录");
        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("用户不存在");
        return user.getId();
    }

    // ==================== 6.1 AI 生成代码 ====================

    @Operation(summary = "AI 自然语言生成 Manim 代码")
    @PostMapping("/ai/generate/code")
    public Result<Map<String, Object>> generateCode(
            @RequestParam("userPrompt") String userPrompt,
            @RequestParam(value = "knowledgeId", required = false) Integer knowledgeId) {

        if (userPrompt == null || userPrompt.trim().isEmpty())
            throw new BusinessException("userPrompt 不能为空");

        Map<String, Object> data = aiService.generateCode(userPrompt, knowledgeId);
        return Result.success(data);
    }

    // ==================== 6.2 AI 修复代码 ====================

    @Operation(summary = "AI 代码智能修复")
    @PostMapping("/ai/fix/code")
    public Result<Map<String, Object>> fixCode(
            @RequestParam("errorLog") String errorLog,
            @RequestParam("oldCode") String oldCode) {

        if (errorLog == null || errorLog.trim().isEmpty())
            throw new BusinessException("errorLog 不能为空");
        if (oldCode == null || oldCode.trim().isEmpty())
            throw new BusinessException("oldCode 不能为空");

        Map<String, Object> data = aiService.fixCode(errorLog, oldCode);
        return Result.success(data);
    }

    // ==================== 6.3 沙箱手动渲染 ====================

    @Operation(summary = "沙箱代码手动渲染")
    @PostMapping("/sandbox/render")
    public Result<Map<String, Object>> sandboxRender(
            @RequestParam("manimCode") String manimCode) {

        if (manimCode == null || manimCode.trim().isEmpty())
            throw new BusinessException("manimCode 不能为空");

        Integer userId = getCurrentUserId();
        Integer taskId = taskService.submitTask(userId, manimCode, 3);

        Map<String, Object> data = new HashMap<>();
        data.put("taskId", taskId);
        data.put("previewUrl", null);
        data.put("errorLog", null);
        return Result.success(data);
    }

    // ==================== 6.4 版本历史查询 ====================

    @Operation(summary = "沙箱版本历史记录查询")
    @GetMapping("/sandbox/version/list")
    public Result<List<SandboxDraft>> getVersionList(
            @RequestParam("workId") Integer workId) {

        Integer userId = getCurrentUserId();
        List<SandboxDraft> list = sandboxDraftService.getVersionList(workId, userId);
        return Result.success(list);
    }

    // ==================== 6.5 沙箱草稿保存 ====================

    @Operation(summary = "沙箱草稿保存（自动版本递增）")
    @PostMapping("/sandbox/draft/save")
    public Result<Map<String, Object>> saveDraft(
            @RequestParam(value = "draftId", required = false) Integer draftId,
            @RequestParam("manimCode") String manimCode,
            @RequestParam(value = "previewUrl", required = false) String previewUrl) {

        if (manimCode == null || manimCode.trim().isEmpty())
            throw new BusinessException("manimCode 不能为空");

        Integer userId = getCurrentUserId();
        // workId 传 null：沙箱保存不涉及 Fork 来源，每次保存产生新版本
        Integer newDraftId = sandboxDraftService.saveDraft(userId, null, manimCode, previewUrl);

        // 查一下最新版本号返回给前端
        SandboxDraft draft = sandboxDraftService.getById(newDraftId);

        Map<String, Object> data = new HashMap<>();
        data.put("draftId", newDraftId);
        data.put("version", draft != null ? draft.getVersion() : 1);
        return Result.success(data);
    }

    // ==================== 6.6 作品发布提交 ====================

    @Operation(summary = "作品发布配置提交（沙箱→画廊）")
    @PostMapping("/work/publish")
    public Result<Map<String, Object>> publishWork(
            @RequestParam("workTitle") String workTitle,
            @RequestParam(value = "workDesc", required = false) String workDesc,
            @RequestParam(value = "tagList", required = false) String tagList,
            @RequestParam("isPublic") Boolean isPublic,
            @RequestParam("code") String code,
            @RequestParam(value = "previewUrl", required = false) String previewUrl) {

        if (workTitle == null || workTitle.trim().isEmpty())
            throw new BusinessException("workTitle 不能为空");
        if (code == null || code.trim().isEmpty())
            throw new BusinessException("code 不能为空");

        Integer userId = getCurrentUserId();

        Work work = new Work();
        work.setUserId(userId);
        work.setTitle(workTitle.trim());
        work.setDescription(workDesc);
        work.setTags(tagList);
        work.setIsPublic(isPublic ? 1 : 0);
        work.setManimCode(code);
        work.setVideoPath(previewUrl);
        work.setStatus(1);
        Integer workId = workService.saveWork(work);

        Map<String, Object> data = new HashMap<>();
        data.put("publishedWorkId", workId);
        return Result.success(data);
    }
}
