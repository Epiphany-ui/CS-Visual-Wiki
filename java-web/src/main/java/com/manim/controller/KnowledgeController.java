package com.manim.controller;

import com.manim.dto.KnowledgeListDTO;
import com.manim.exception.BusinessException;
import com.manim.exception.UnauthorizedException;
import com.manim.pojo.Animation;
import com.manim.pojo.KnowledgeEntry;
import com.manim.pojo.Result;
import com.manim.pojo.User;
import com.manim.service.*;
import com.manim.utils.UserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

/**
 * 百科知识模块 + 学习打卡接口
 * <p>对应接口文档：四、百科知识模块</p>
 */
@Tag(name = "百科知识接口")
@RestController
@RequestMapping("/api/v1")
public class KnowledgeController {

    @Autowired
    private KnowledgeEntryService knowledgeEntryService;

    @Autowired
    private AnimationService animationService;

    @Autowired
    private UserCollectService userCollectService;

    @Autowired
    private StudyRecordService studyRecordService;

    @Autowired
    private UserService userService;

    /**
     * 从 UserContext 获取当前登录用户的 ID
     */
    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录");
        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("用户不存在");
        return user.getId();
    }

    // ==================== 4.1 获取分类知识点列表 ====================

    @Operation(summary = "获取百科分类知识点列表")
    @GetMapping("/knowledge/category/list")
    public Result<List<KnowledgeListDTO>> getCategoryList(
            @RequestParam(value = "categoryId", required = false) Integer categoryId,
            @RequestParam(value = "difficulty", required = false) Integer difficulty,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {

        List<KnowledgeEntry> entries = knowledgeEntryService.listByCategory(categoryId, difficulty, page, size);
        List<KnowledgeListDTO> list = entries.stream().map(e -> {
            int animCount = animationService.countByKnowledgeId(e.getId());
            return new KnowledgeListDTO(e.getId(), e.getTitle(), e.getSummary(),
                    e.getDifficulty(), animCount);
        }).collect(Collectors.toList());
        return Result.success(list);
    }

    // ==================== 4.2 获取词条详情 ====================

    @Operation(summary = "获取知识点百科详情")
    @GetMapping("/knowledge/detail")
    public Result<KnowledgeEntry> getDetail(@RequestParam("knowledgeId") Integer knowledgeId) {
        KnowledgeEntry entry = knowledgeEntryService.getById(knowledgeId);
        if (entry == null) throw new BusinessException("词条不存在");
        return Result.success(entry);
    }

    // ==================== 4.3 获取配套动画列表 ====================

    @Operation(summary = "获取知识点配套动画列表")
    @GetMapping("/knowledge/animation/list")
    public Result<List<Animation>> getAnimationList(@RequestParam("knowledgeId") Integer knowledgeId) {
        List<Animation> list = animationService.listByKnowledgeId(knowledgeId);
        return Result.success(list);
    }

    // ==================== 4.4 获取相关推荐 ====================

    @Operation(summary = "获取相关推荐知识点")
    @GetMapping("/knowledge/recommend")
    public Result<List<KnowledgeListDTO>> getRecommend(@RequestParam("knowledgeId") Integer knowledgeId) {
        List<KnowledgeEntry> entries = knowledgeEntryService.getRecommended(knowledgeId);
        List<KnowledgeListDTO> list = entries.stream().map(e ->
                new KnowledgeListDTO(e.getId(), e.getTitle(), e.getSummary(),
                        e.getDifficulty(), 0)
        ).collect(Collectors.toList());
        return Result.success(list);
    }

    // ==================== 4.5 收藏/取消收藏 ====================

    @Operation(summary = "知识点收藏/取消收藏")
    @PostMapping("/knowledge/collect")
    public Result<Void> collectKnowledge(
            @RequestParam("knowledgeId") Integer knowledgeId,
            @RequestParam("isCollect") Boolean isCollect) {
        Integer userId = getCurrentUserId();
        userCollectService.toggleCollect(userId, 1, knowledgeId, isCollect);
        return Result.success();
    }

    // ==================== 4.6 学习打卡 ====================

    @Operation(summary = "学习打卡 & 进度记录")
    @PostMapping("/study/checkin")
    public Result<Void> checkin(
            @RequestParam("knowledgeId") Integer knowledgeId,
            @RequestParam("studyDuration") Integer studyDuration) {
        Integer userId = getCurrentUserId();
        studyRecordService.checkin(userId, knowledgeId, studyDuration);
        return Result.success();
    }
}
