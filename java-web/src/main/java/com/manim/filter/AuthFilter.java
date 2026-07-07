package com.manim.filter;

import com.manim.pojo.Result;
import com.manim.utils.JwtUtil;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Component;
import org.springframework.util.AntPathMatcher;

import javax.servlet.*;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.util.Arrays;
import java.util.List;

/**
 * JWT 认证过滤器
 * <p>
 * 拦截 /api/* 路径，对白名单内的请求放行，
 * 其余请求校验请求头中的 Bearer token。
 * </p>
 */
@Component
public class AuthFilter implements Filter {

    private static final Logger log = LoggerFactory.getLogger(AuthFilter.class);

    /** 路径匹配器，支持 Ant 风格模式 */
    private static final AntPathMatcher pathMatcher = new AntPathMatcher();

    /** 放行白名单（不需要 token 的路径） */
    private static final List<String> WHITELIST = Arrays.asList(
            "/api/auth/login",
            "/api/auth/register"
    );

    @Autowired
    private JwtUtil jwtUtil;

    @Override
    public void doFilter(ServletRequest servletRequest,
                         ServletResponse servletResponse,
                         FilterChain filterChain)
            throws IOException, ServletException {

        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;
        String requestPath = request.getRequestURI();

        // 1. 白名单路径直接放行
        if (isWhitelisted(requestPath)) {
            filterChain.doFilter(request, response);
            return;
        }

        // 2. 从请求头获取 token
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            writeUnauthorized(response, "缺少 Authorization 请求头或格式错误，需使用 Bearer <token>");
            return;
        }

        String token = authHeader.substring(7);

        // 3. 校验 token
        String userId = jwtUtil.getUserIdFromToken(token);
        if (userId == null) {
            writeUnauthorized(response, "JWT 令牌无效或已过期，请重新登录");
            return;
        }

        // 4. token 有效：将用户信息存入 request 属性，供后续 Controller 使用
        request.setAttribute("userId", userId);
        log.debug("JWT 校验通过，userId={}, path={}", userId, requestPath);
        filterChain.doFilter(request, response);
    }

    /**
     * 判断请求路径是否在白名单中
     */
    private boolean isWhitelisted(String path) {
        for (String pattern : WHITELIST) {
            if (pathMatcher.match(pattern, path)) {
                return true;
            }
        }
        return false;
    }

    /**
     * 返回 401 未授权响应
     */
    private void writeUnauthorized(HttpServletResponse response, String message) throws IOException {
        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);

        String json = String.format(
                "{\"code\":401,\"msg\":\"%s\",\"data\":null}",
                message
        );
        response.getWriter().write(json);
    }
}
