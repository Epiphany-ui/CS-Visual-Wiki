package com.manim.controller;

import com.manim.pojo.Result;
import com.manim.utils.JwtUtil;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;

/**
 * 认证控制器（登录/注册，无需 token 即可访问）
 */
@Tag(name = "认证接口")
@RestController
@RequestMapping("/api/auth")
public class AuthController {

    @Autowired
    private JwtUtil jwtUtil;

    /**
     * 登录接口
     * <p>
     * 接收用户名和密码，校验通过后返回 JWT 令牌。
     * （当前为简易实现，密码校验逻辑可后续扩展）
     * </p>
     */
    @Operation(summary = "用户登录", description = "用户登录获取 JWT 令牌")
    @PostMapping("/login")
    public Result<Map<String, Object>> login(
            @RequestParam("username") String username,
            @RequestParam("password") String password) {

        // 参数校验
        if (username == null || username.trim().isEmpty()) {
            return Result.fail("用户名不能为空");
        }

        // TODO: 后续可扩展为从数据库查询用户信息并校验密码
        // 当前简化为：只要用户名不为空，登录成功（生产环境请替换为真实校验）

        // 生成 JWT 令牌
        String token = jwtUtil.generateToken(username.trim());

        // 组装返回数据
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("username", username.trim());

        return Result.success("登录成功", data);
    }
}
