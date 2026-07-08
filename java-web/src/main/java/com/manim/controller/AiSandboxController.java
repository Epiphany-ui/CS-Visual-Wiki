package com.manim.controller;

import com.manim.pojo.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

/**
 * AI 沙箱创作模块接口
 * <p>对应接口文档：六、AI 沙箱创作模块</p>
 */
@Tag(name = "AI 沙箱创作接口")
@RestController
@RequestMapping("/api/v1")
public class AiSandboxController {

    @Operation(summary = "AI 自然语言生成 Manim 代码")
    @PostMapping("/ai/generate/code")
    public Result<?> generateCode(@RequestParam("userPrompt") String userPrompt,
                                   @RequestParam(value = "knowledgeId", required = false) Integer knowledgeId) {
        // TODO: 调用 Python AI 服务生成代码
        return Result.success("操作成功");
    }

    @Operation(summary = "AI 代码智能修复")
    @PostMapping("/ai/fix/code")
    public Result<?> fixCode(@RequestParam("errorLog") String errorLog,
                              @RequestParam("oldCode") String oldCode) {
        // TODO: 调用 Python AI 服务修复代码
        return Result.success("操作成功");
    }

    @Operation(summary = "沙箱代码手动渲染")
    @PostMapping("/sandbox/render")
    public Result<?> sandboxRender(@RequestParam("manimCode") String manimCode) {
        // TODO: 触发渲染任务
        return Result.success("操作成功");
    }

    @Operation(summary = "沙箱版本历史记录查询")
    @GetMapping("/sandbox/version/list")
    public Result<?> getVersionList(@RequestParam("workId") Integer workId) {
        // TODO: 查询版本历史
        return Result.success("操作成功");
    }

    @Operation(summary = "沙箱草稿保存")
    @PostMapping("/sandbox/draft/save")
    public Result<?> saveDraft(@RequestParam(value = "draftId", required = false) Integer draftId,
                                @RequestParam("manimCode") String manimCode,
                                @RequestParam(value = "previewUrl", required = false) String previewUrl) {
        // TODO: 保存沙箱草稿
        return Result.success("操作成功");
    }

    @Operation(summary = "作品发布配置提交")
    @PostMapping("/work/publish")
    public Result<?> publishWork(@RequestParam("workTitle") String workTitle,
                                  @RequestParam(value = "workDesc", required = false) String workDesc,
                                  @RequestParam(value = "tagList", required = false) String tagList,
                                  @RequestParam("isPublic") Boolean isPublic,
                                  @RequestParam("code") String code,
                                  @RequestParam(value = "previewUrl", required = false) String previewUrl) {
        // TODO: 发布作品
        return Result.success("操作成功");
    }
}
