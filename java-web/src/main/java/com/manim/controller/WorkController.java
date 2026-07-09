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

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 作品详情 & 互动接口
 * <p>对应接口文档：7.2 ~ 7.8</p>
 */
@Tag(name = "作品互动接口")
@RestController
@RequestMapping("/api/v1")
public class WorkController {

    @Autowired
    private WorkService workService;

    @Autowired
    private WorkCommentService workCommentService;

    @Autowired
    private UserFollowService userFollowService;

    @Autowired
    private UserService userService;

    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录");
        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("用户不存在");
        return user.getId();
    }

    // ==================== 7.2 公开作品详情 ====================

    @Operation(summary = "获取公开作品详情")
    @GetMapping("/work/public/detail")
    public Result<Work> getPublicDetail(@RequestParam("workId") Integer workId) {
        Work work = workService.getPublicDetail(workId);
        if (work == null) throw new BusinessException("作品不存在");
        return Result.success(work);
    }

    // ==================== 7.3 点赞/取消点赞 ====================

    @Operation(summary = "作品点赞/取消点赞")
    @PostMapping("/work/like")
    public Result<Void> likeWork(@RequestParam("workId") Integer workId,
                                  @RequestParam("isLike") Boolean isLike) {
        Integer userId = getCurrentUserId();
        workService.toggleLike(workId, userId, isLike);
        return Result.success();
    }

    // ==================== 7.4 收藏/取消收藏 ====================

    @Operation(summary = "作品收藏/取消收藏")
    @PostMapping("/work/collect")
    public Result<Void> collectWork(@RequestParam("workId") Integer workId,
                                     @RequestParam("isCollect") Boolean isCollect) {
        Integer userId = getCurrentUserId();
        workService.toggleCollect(workId, userId, isCollect);
        return Result.success();
    }

    // ==================== 7.5 评论列表 & 发布评论 ====================

    @Operation(summary = "获取作品评论列表")
    @GetMapping("/work/comment/list")
    public Result<List<WorkComment>> getCommentList(@RequestParam("workId") Integer workId) {
        List<WorkComment> list = workCommentService.listByWorkId(workId);
        return Result.success(list);
    }

    @Operation(summary = "发布评论")
    @PostMapping("/work/comment/add")
    public Result<Map<String, Object>> addComment(
            @RequestParam("workId") Integer workId,
            @RequestParam("content") String content,
            @RequestParam(value = "replyId", required = false) Integer replyId) {
        if (content == null || content.trim().isEmpty())
            throw new BusinessException("评论内容不能为空");
        Integer userId = getCurrentUserId();
        Integer commentId = workCommentService.addComment(workId, userId, content.trim(), replyId);
        Map<String, Object> data = new HashMap<>();
        data.put("commentId", commentId);
        return Result.success(data);
    }

    // ==================== 7.6 Fork 二次创作 ====================

    @Operation(summary = "作品 Fork 二次创作")
    @PostMapping("/work/fork")
    public Result<Map<String, Object>> forkWork(@RequestParam("workId") Integer workId) {
        Integer userId = getCurrentUserId();
        Work source = workService.getById(workId);
        if (source == null) throw new BusinessException("作品不存在");

        Integer newWorkId = workService.forkWork(workId, userId);
        User sourceAuthor = userService.getById(source.getUserId());

        Map<String, Object> data = new HashMap<>();
        data.put("workId", newWorkId);
        data.put("sourceCode", source.getManimCode());
        data.put("sourceAuthor", sourceAuthor != null ? sourceAuthor.getNickname() : "未知用户");
        return Result.success(data);
    }

    // ==================== 7.7 创作者主页 ====================

    @Operation(summary = "获取创作者主页数据")
    @GetMapping("/user/author/home")
    public Result<Map<String, Object>> getAuthorHome(@RequestParam("authorId") Integer authorId) {
        User author = userService.getById(authorId);
        if (author == null) throw new BusinessException("创作者不存在");

        // 获取该创作者公开作品
        List<Work> works = workService.listByUser(authorId, 1, 1, 100);
        int totalLikes = works.stream().mapToInt(w -> w.getLikeCount() != null ? w.getLikeCount() : 0).sum();
        int followerCount = userFollowService.getFollowerCount(authorId);

        Map<String, Object> data = new HashMap<>();
        Map<String, Object> authorInfo = new HashMap<>();
        authorInfo.put("userId", author.getId());
        authorInfo.put("nickname", author.getNickname());
        authorInfo.put("avatar", author.getAvatar());
        authorInfo.put("intro", author.getIntro());
        data.put("authorInfo", authorInfo);
        data.put("workCount", works.size());
        data.put("totalLikes", totalLikes);
        data.put("followerCount", followerCount);
        data.put("workList", works);
        return Result.success(data);
    }

    // ==================== 7.8 关注/取消关注 ====================

    @Operation(summary = "关注/取消关注创作者")
    @PostMapping("/user/follow")
    public Result<Void> followAuthor(@RequestParam("authorId") Integer authorId,
                                      @RequestParam("isFollow") Boolean isFollow) {
        Integer userId = getCurrentUserId();
        if (userId.equals(authorId)) throw new BusinessException("不能关注自己");
        userFollowService.toggleFollow(userId, authorId, isFollow);
        return Result.success();
    }
}
