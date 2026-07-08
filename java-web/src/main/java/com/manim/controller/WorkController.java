package com.manim.controller;

import com.manim.pojo.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

/**
 * 作品详情 & 互动接口
 * <p>对应接口文档：7.2 ~ 7.8 作品详情、点赞、收藏、评论、Fork、创作者主页、关注</p>
 */
@Tag(name = "作品互动接口")
@RestController
@RequestMapping("/api/v1")
public class WorkController {

    @Operation(summary = "获取公开作品详情")
    @GetMapping("/work/public/detail")
    public Result<?> getPublicDetail(@RequestParam("workId") Integer workId) {
        // TODO: 实现作品详情查询
        return Result.success("操作成功");
    }

    @Operation(summary = "作品点赞/取消点赞")
    @PostMapping("/work/like")
    public Result<?> likeWork(@RequestParam("workId") Integer workId,
                               @RequestParam("isLike") Boolean isLike) {
        // TODO: 实现点赞逻辑
        return Result.success("操作成功");
    }

    @Operation(summary = "作品收藏/取消收藏")
    @PostMapping("/work/collect")
    public Result<?> collectWork(@RequestParam("workId") Integer workId,
                                  @RequestParam("isCollect") Boolean isCollect) {
        // TODO: 实现收藏逻辑
        return Result.success("操作成功");
    }

    @Operation(summary = "获取作品评论列表")
    @GetMapping("/work/comment/list")
    public Result<?> getCommentList(@RequestParam("workId") Integer workId) {
        // TODO: 实现评论列表查询
        return Result.success("操作成功");
    }

    @Operation(summary = "发布评论")
    @PostMapping("/work/comment/add")
    public Result<?> addComment(@RequestParam("workId") Integer workId,
                                 @RequestParam("content") String content,
                                 @RequestParam(value = "replyId", required = false) Integer replyId) {
        // TODO: 实现评论发布
        return Result.success("操作成功");
    }

    @Operation(summary = "作品 Fork 二次创作")
    @PostMapping("/work/fork")
    public Result<?> forkWork(@RequestParam("workId") Integer workId) {
        // TODO: 实现 Fork 逻辑
        return Result.success("操作成功");
    }

    @Operation(summary = "作品资源导出")
    @GetMapping("/work/export")
    public Result<?> exportWork(@RequestParam("workId") Integer workId,
                                 @RequestParam("exportType") String exportType) {
        // TODO: 实现导出逻辑
        return Result.success("操作成功");
    }

    @Operation(summary = "模板作品保存/发布")
    @PostMapping("/template/work/save")
    public Result<?> saveTemplateWork(@RequestParam("taskId") Integer taskId,
                                       @RequestParam(value = "workTitle", required = false) String workTitle,
                                       @RequestParam(value = "workDesc", required = false) String workDesc,
                                       @RequestParam(value = "isPublic", defaultValue = "false") Boolean isPublic) {
        // TODO: 实现作品保存
        return Result.success("操作成功");
    }

    @Operation(summary = "获取创作者主页数据")
    @GetMapping("/user/author/home")
    public Result<?> getAuthorHome(@RequestParam("authorId") Integer authorId) {
        // TODO: 实现创作者主页查询
        return Result.success("操作成功");
    }

    @Operation(summary = "关注/取消关注创作者")
    @PostMapping("/user/follow")
    public Result<?> followAuthor(@RequestParam("authorId") Integer authorId,
                                   @RequestParam("isFollow") Boolean isFollow) {
        // TODO: 实现关注逻辑
        return Result.success("操作成功");
    }
}
