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
 * 个人中心模块接口
 * <p>对应接口文档：八、个人中心模块</p>
 */
@Tag(name = "个人中心接口")
@RestController
@RequestMapping("/api/v1/user")
public class UserCenterController {

    @Autowired
    private UserService userService;

    @Autowired
    private WorkService workService;

    @Autowired
    private UserCollectService userCollectService;

    @Autowired
    private BrowseHistoryService browseHistoryService;

    @Autowired
    private StudyRecordService studyRecordService;

    @Autowired
    private UserFollowService userFollowService;

    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录");
        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("用户不存在");
        return user.getId();
    }

    // ==================== 8.1 个人中心首页 ====================

    @Operation(summary = "获取个人中心首页数据")
    @GetMapping("/home/data")
    public Result<Map<String, Object>> getHomeData() {
        Integer userId = getCurrentUserId();
        User user = userService.getById(userId);

        List<Work> works = workService.listByUser(userId, null, 1, 1000);
        int workCount = works.size();
        Map<String, Object> studyStat = studyRecordService.getStudyStat(userId);
        int followerCount = userFollowService.getFollowerCount(userId);
        int followeeCount = userFollowService.getFolloweeCount(userId);

        Map<String, Object> data = new HashMap<>();
        Map<String, Object> userInfo = new HashMap<>();
        userInfo.put("userId", userId);
        userInfo.put("nickname", user != null ? user.getNickname() : "");
        userInfo.put("avatar", user != null ? user.getAvatar() : "");
        data.put("userInfo", userInfo);
        data.put("workCount", workCount);
        data.put("totalStudyMinutes", studyStat.getOrDefault("totalStudyMinutes", 0));
        data.put("checkinDays", studyStat.getOrDefault("checkinDays", 0));
        data.put("followerCount", followerCount);
        data.put("followeeCount", followeeCount);
        return Result.success(data);
    }

    // ==================== 8.2 我的作品列表 ====================

    @Operation(summary = "获取我的作品列表")
    @GetMapping("/work/list")
    public Result<Map<String, Object>> getMyWorks(
            @RequestParam(value = "status", required = false) Integer status,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {
        Integer userId = getCurrentUserId();
        List<Work> list = workService.listByUser(userId, status, page, size);
        Map<String, Object> data = new HashMap<>();
        data.put("list", list);
        data.put("total", list.size());
        return Result.success(data);
    }

    // ==================== 8.3 我的收藏列表 ====================

    @Operation(summary = "获取我的收藏列表")
    @GetMapping("/collect/list")
    public Result<List<UserCollect>> getMyCollects(
            @RequestParam(value = "type", required = false) Integer type,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {
        Integer userId = getCurrentUserId();
        List<UserCollect> list = userCollectService.listByUser(userId, type, page, size);
        return Result.success(list);
    }

    // ==================== 8.4 浏览历史 ====================

    @Operation(summary = "获取浏览历史记录")
    @GetMapping("/history/list")
    public Result<List<BrowseHistory>> getBrowseHistory(
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {
        Integer userId = getCurrentUserId();
        List<BrowseHistory> list = browseHistoryService.listByUser(userId, page, size);
        return Result.success(list);
    }

    // ==================== 8.5 学习统计 ====================

    @Operation(summary = "获取个人学习统计数据")
    @GetMapping("/study/stat")
    public Result<Map<String, Object>> getStudyStat() {
        Integer userId = getCurrentUserId();
        Map<String, Object> stat = studyRecordService.getStudyStat(userId);
        return Result.success(stat);
    }

    // ==================== 8.6 创作者数据统计 ====================

    @Operation(summary = "获取创作者作品数据统计")
    @GetMapping("/author/stat")
    public Result<Map<String, Object>> getAuthorStat() {
        Integer userId = getCurrentUserId();
        List<Work> works = workService.listByUser(userId, 1, 1, 1000);

        int totalViews = works.stream().mapToInt(w -> w.getViewCount() != null ? w.getViewCount() : 0).sum();
        int totalLikes = works.stream().mapToInt(w -> w.getLikeCount() != null ? w.getLikeCount() : 0).sum();
        int totalCollects = works.stream().mapToInt(w -> w.getCollectCount() != null ? w.getCollectCount() : 0).sum();
        int totalForks = works.stream().mapToInt(w -> w.getForkCount() != null ? w.getForkCount() : 0).sum();

        Map<String, Object> data = new HashMap<>();
        data.put("totalViews", totalViews);
        data.put("totalLikes", totalLikes);
        data.put("totalCollects", totalCollects);
        data.put("totalForks", totalForks);
        data.put("workDetails", works);
        return Result.success(data);
    }

    // ==================== 8.7 更新个人资料 ====================

    @Operation(summary = "更新个人账号资料")
    @PutMapping("/profile/update")
    public Result<Void> updateProfile(
            @RequestParam(value = "nickname", required = false) String nickname,
            @RequestParam(value = "avatar", required = false) String avatar,
            @RequestParam(value = "intro", required = false) String intro) {
        Integer userId = getCurrentUserId();
        userService.updateProfile(userId, nickname, avatar, intro);
        return Result.success();
    }
}
