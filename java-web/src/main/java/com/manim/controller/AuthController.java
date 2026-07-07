package com.manim.controller;

import com.manim.exception.BusinessException;
import com.manim.pojo.Result;
import com.manim.pojo.User;
import com.manim.service.UserService;
import com.manim.utils.JwtUtil;
import com.manim.utils.Md5Util;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 用户账号接口（白名单，无须 token）
 */
@Tag(name = "用户账号接口")
@RestController
@RequestMapping("/api")
public class AuthController {

    @Autowired
    private UserService userService;

    @Operation(summary = "用户注册", description = "校验账号唯一性，MD5 加密密码入库，返回 JWT 令牌")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "注册成功，返回 token/username/userId"),
            @ApiResponse(responseCode = "500", description = "业务失败（用户名重复、密码过短等）",
                    content = @Content(schema = @Schema(implementation = Result.class)))
    })
    @PostMapping("/register")
    public Result<Map<String, Object>> register(
            @Parameter(description = "用户名（唯一，不可重复）", required = true)
            @RequestParam("username") String username,
            @Parameter(description = "登录密码（不少于 6 位）", required = true)
            @RequestParam("password") String password) {

        if (username == null || username.trim().isEmpty()) {
            throw new BusinessException("用户名不能为空");
        }
        if (password == null || password.length() < 6) {
            throw new BusinessException("密码不能少于6位");
        }

        // 校验账号是否重复
        User exist = userService.findByUsername(username.trim());
        if (exist != null) {
            throw new BusinessException("账号已存在");
        }

        // MD5 加密 + 创建用户
        String encryptedPwd = Md5Util.md5(password);
        User user = new User();
        user.setUsername(username.trim());
        user.setPassword(encryptedPwd);
        userService.register(user);

        // 生成 JWT 令牌（claim 中是用户名）
        String token = JwtUtil.generateToken(user.getUsername());

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("username", user.getUsername());
        data.put("userId", user.getId());

        return Result.success("注册成功", data);
    }

    @Operation(summary = "用户登录", description = "校验用户名密码，成功返回 JWT 令牌")
    @ApiResponses({
            @ApiResponse(responseCode = "200", description = "登录成功，返回 token/username/userId"),
            @ApiResponse(responseCode = "500", description = "用户名或密码错误",
                    content = @Content(schema = @Schema(implementation = Result.class)))
    })
    @PostMapping("/login")
    public Result<Map<String, Object>> login(
            @Parameter(description = "用户名", required = true)
            @RequestParam("username") String username,
            @Parameter(description = "登录密码", required = true)
            @RequestParam("password") String password) {

        if (username == null || username.trim().isEmpty()) {
            throw new BusinessException("用户名不能为空");
        }
        if (password == null || password.isEmpty()) {
            throw new BusinessException("密码不能为空");
        }

        // 查询用户 + MD5 密码匹配
        User user = userService.login(username.trim(), Md5Util.md5(password));
        if (user == null) {
            throw new BusinessException("用户名或密码错误");
        }

        // 生成 JWT 令牌（claim 中是用户名）
        String token = JwtUtil.generateToken(user.getUsername());

        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("username", user.getUsername());
        data.put("userId", user.getId());

        return Result.success("登录成功", data);
    }
}
