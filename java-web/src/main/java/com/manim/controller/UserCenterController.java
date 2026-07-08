package com.manim.controller;

import com.manim.exception.UnauthorizedException;
import com.manim.pojo.Result;
import com.manim.pojo.User;
import com.manim.service.UserService;
import com.manim.utils.UserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
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

    private Integer getCurrentUserId() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录");
        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("用户不存在");
        return user.getId();
    }

    @Operation(summary = "获取个人中心首页数据")
    @GetMapping("/home/data")
    public Result<?> getHomeData() {
        Integer userId = getCurrentUserId();
        // TODO: 实现个人中心统计数据查询
        Map<String, Object> data = new HashMap<>();
        data.put("userId", userId);
        return Result.success(data);
    }

    @Operation(summary = "获取我的作品列表")
    @GetMapping("/work/list")
    public Result<?> getMyWorks(@RequestParam(value = "status", required = false) Integer status,
                                 @RequestParam(value = "page", defaultValue = "1") Integer page,
                                 @RequestParam(value = "size", defaultValue = "10") Integer size) {
        getCurrentUserId();
        // TODO: 实现作品列表查询
        return Result.success("操作成功");
    }

    @Operation(summary = "获取我的收藏列表")
    @GetMapping("/collect/list")
    public Result<?> getMyCollects(@RequestParam(value = "type", required = false) Integer type,
                                    @RequestParam(value = "page", defaultValue = "1") Integer page,
                                    @RequestParam(value = "size", defaultValue = "10") Integer size) {
        getCurrentUserId();
        // TODO: 实现收藏列表查询
        return Result.success("操作成功");
    }

    @Operation(summary = "获取浏览历史记录")
    @GetMapping("/history/list")
    public Result<?> getBrowseHistory(@RequestParam(value = "page", defaultValue = "1") Integer page,
                                       @RequestParam(value = "size", defaultValue = "10") Integer size) {
        getCurrentUserId();
        // TODO: 实现浏览历史查询
        return Result.success("操作成功");
    }

    @Operation(summary = "获取个人学习统计数据")
    @GetMapping("/study/stat")
    public Result<?> getStudyStat() {
        getCurrentUserId();
        // TODO: 实现学习统计查询
        return Result.success("操作成功");
    }

    @Operation(summary = "获取创作者作品数据统计")
    @GetMapping("/author/stat")
    public Result<?> getAuthorStat() {
        getCurrentUserId();
        // TODO: 实现创作者数据统计
        return Result.success("操作成功");
    }

    @Operation(summary = "更新个人账号资料")
    @PutMapping("/profile/update")
    public Result<?> updateProfile(@RequestParam(value = "nickname", required = false) String nickname,
                                    @RequestParam(value = "avatar", required = false) String avatar,
                                    @RequestParam(value = "intro", required = false) String intro) {
        Integer userId = getCurrentUserId();
        // TODO: 实现资料更新逻辑
        return Result.success("操作成功");
    }
}
