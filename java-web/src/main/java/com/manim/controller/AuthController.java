package com.manim.controller;

import com.manim.exception.BusinessException;
import com.manim.exception.UnauthorizedException;
import com.manim.pojo.Result;
import com.manim.pojo.User;
import com.manim.service.UserService;
import com.manim.utils.JwtUtil;
import com.manim.utils.Md5Util;
import com.manim.utils.UserContext;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 用户账号接口（白名单：登录/注册不校验 token，其他需认证）
 * <p>对应接口文档：一、登入注册模块</p>
 */
@Tag(name = "用户账号接口")
@RestController
@RequestMapping("/api/v1/user")
public class AuthController {

    @Autowired
    private UserService userService;

    @Operation(summary = "用户注册")
    @PostMapping("/register")
    public Result<Map<String, Object>> register(
            @Parameter(description = "用户名（唯一）") @RequestParam("username") String username,
            @Parameter(description = "密码（不少于 6 位）") @RequestParam("password") String password,
            @Parameter(description = "昵称（选填）") @RequestParam(value = "nickname", required = false) String nickname) {

        if (username == null || username.trim().isEmpty()) throw new BusinessException("用户名不能为空");
        if (password == null || password.length() < 6) throw new BusinessException("密码不能少于6位");

        User exist = userService.findByUsername(username.trim());
        if (exist != null) throw new BusinessException("账号已存在");

        String encryptedPwd = Md5Util.md5(password);
        User user = new User();
        user.setUsername(username.trim());
        user.setPassword(encryptedPwd);
        user.setNickname(nickname != null ? nickname.trim() : username.trim());
        userService.register(user);

        String token = JwtUtil.generateToken(user.getUsername());
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("userId", user.getId());
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname());
        return Result.success("注册成功", data);
    }

    @Operation(summary = "用户登录")
    @PostMapping("/login")
    public Result<Map<String, Object>> login(
            @Parameter(description = "用户名") @RequestParam("username") String username,
            @Parameter(description = "密码") @RequestParam("password") String password) {

        if (username == null || username.trim().isEmpty()) throw new BusinessException("用户名不能为空");
        if (password == null || password.isEmpty()) throw new BusinessException("密码不能为空");

        User user = userService.login(username.trim(), Md5Util.md5(password));
        if (user == null) throw new BusinessException("用户名或密码错误");

        String token = JwtUtil.generateToken(user.getUsername());
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("userId", user.getId());
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname());
        data.put("avatar", user.getAvatar());
        return Result.success("登录成功", data);
    }

    @Operation(summary = "获取当前登录用户信息")
    @GetMapping("/info")
    public Result<Map<String, Object>> info() {
        String username = UserContext.getUsername();
        if (username == null) throw new UnauthorizedException("未登录");

        User user = userService.findByUsername(username);
        if (user == null) throw new UnauthorizedException("用户不存在");

        Map<String, Object> data = new HashMap<>();
        data.put("userId", user.getId());
        data.put("username", user.getUsername());
        data.put("nickname", user.getNickname());
        data.put("avatar", user.getAvatar());
        data.put("intro", user.getIntro());
        data.put("createTime", user.getCreateTime());
        return Result.success(data);
    }

    @Operation(summary = "用户退出登录")
    @PostMapping("/logout")
    public Result<Void> logout() {
        // JWT 无状态，前端清除 token 即可，此处仅做会话标记清理
        UserContext.remove();
        return Result.success();
    }
}
