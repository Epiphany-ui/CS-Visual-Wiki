package com.manim.controller;

import com.manim.pojo.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

/**
 * 百科知识模块 + 学习打卡接口
 * <p>对应接口文档：四、百科知识模块</p>
 */
@Tag(name = "百科知识接口")
@RestController
@RequestMapping("/api/v1")
public class KnowledgeController {

    @Operation(summary = "获取百科分类知识点列表")
    @GetMapping("/knowledge/category/list")
    public Result<?> getCategoryList(@RequestParam(value = "categoryId", required = false) Integer categoryId,
                                      @RequestParam(value = "difficulty", required = false) Integer difficulty,
                                      @RequestParam(value = "page", defaultValue = "1") Integer page,
                                      @RequestParam(value = "size", defaultValue = "10") Integer size) {
        // TODO: 实现知识点列表查询
        return Result.success("操作成功");
    }

    @Operation(summary = "获取知识点百科详情")
    @GetMapping("/knowledge/detail")
    public Result<?> getDetail(@RequestParam("knowledgeId") Integer knowledgeId) {
        // TODO: 实现词条详情查询
        return Result.success("操作成功");
    }

    @Operation(summary = "获取知识点配套动画列表")
    @GetMapping("/knowledge/animation/list")
    public Result<?> getAnimationList(@RequestParam("knowledgeId") Integer knowledgeId) {
        // TODO: 实现动画列表查询
        return Result.success("操作成功");
    }

    @Operation(summary = "获取相关推荐知识点")
    @GetMapping("/knowledge/recommend")
    public Result<?> getRecommend(@RequestParam("knowledgeId") Integer knowledgeId) {
        // TODO: 实现关联推荐查询
        return Result.success("操作成功");
    }

    @Operation(summary = "知识点收藏/取消收藏")
    @PostMapping("/knowledge/collect")
    public Result<?> collectKnowledge(@RequestParam("knowledgeId") Integer knowledgeId,
                                       @RequestParam("isCollect") Boolean isCollect) {
        // TODO: 实现收藏逻辑
        return Result.success("操作成功");
    }

    @Operation(summary = "学习打卡 & 进度记录")
    @PostMapping("/study/checkin")
    public Result<?> checkin(@RequestParam("knowledgeId") Integer knowledgeId,
                              @RequestParam("studyDuration") Integer studyDuration) {
        // TODO: 实现学习打卡记录
        return Result.success("操作成功");
    }
}
