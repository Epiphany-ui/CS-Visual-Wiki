package com.manim.filter;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.manim.pojo.Result;
import com.manim.utils.JwtUtil;
import com.manim.utils.UserContext;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
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
 * 白名单路径（/api/v1/user/register, /api/v1/user/login）直接放行；
 * 其余 /api/v1/* 请求校验 Authorization: Bearer token，
 * 校验通过后将用户名写入 {@link UserContext}，供后续 Controller 使用。
 * </p>
 */
public class AuthFilter implements Filter {

    private static final Logger log = LoggerFactory.getLogger(AuthFilter.class);

    private static final AntPathMatcher pathMatcher = new AntPathMatcher();

    private static final List<String> WHITELIST = Arrays.asList(
            "/api/v1/user/register",
            "/api/v1/user/login"
    );

    private static final ObjectMapper objectMapper = new ObjectMapper();

    @Override
    public void doFilter(ServletRequest servletRequest,
                         ServletResponse servletResponse,
                         FilterChain filterChain)
            throws IOException, ServletException {
        /*
         * 过滤流程：
         * 1. 白名单路径（登录/注册）→ 直接放行
         * 2. 校验 Authorization: Bearer <token>
         * 3. JwtUtil 解析 username → 写入 UserContext
         * 4. finally 清理 UserContext 防止内存泄漏
         */
        HttpServletRequest request = (HttpServletRequest) servletRequest;
        HttpServletResponse response = (HttpServletResponse) servletResponse;
        String requestPath = request.getRequestURI();

        try {
            // 白名单路径直接放行
            if (isWhitelisted(requestPath)) {
                filterChain.doFilter(request, response);
                return;
            }

            // 校验 Authorization 头
            String authHeader = request.getHeader("Authorization");
            if (authHeader == null || !authHeader.startsWith("Bearer ")) {
                writeJsonResponse(response, 401, "缺少 Authorization 请求头，需使用 Bearer <token> 格式");
                return;
            }

            String token = authHeader.substring(7);
            String username = JwtUtil.getUsernameFromToken(token);

            if (username == null) {
                writeJsonResponse(response, 401, "JWT 令牌无效或已过期，请重新登录");
                return;
            }

            // 将用户名写入 ThreadLocal
            UserContext.setUsername(username);
            log.debug("JWT 校验通过, username={}, path={}", username, requestPath);

            filterChain.doFilter(request, response);

        } finally {
            // 请求结束，清理 ThreadLocal 防止内存泄漏
            UserContext.remove();
        }
    }

    /**
     * 返回统一格式的 JSON 错误响应
     */
    private void writeJsonResponse(HttpServletResponse response, int code, String msg) throws IOException {
        response.setContentType("application/json;charset=UTF-8");
        response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        String json = objectMapper.writeValueAsString(Result.fail(code, msg));
        response.getWriter().write(json);
    }

    /**
     * 判断请求路径是否在白名单中
     *
     * @param path 请求 URI
     * @return true 放行，false 需 token 校验
     */
    private boolean isWhitelisted(String path) {
        for (String pattern : WHITELIST) {
            if (pathMatcher.match(pattern, path)) {
                return true;
            }
        }
        return false;
    }

    @Override
    public void init(FilterConfig filterConfig) {
        // 无需初始化
    }

    @Override
    public void destroy() {
        // 无需销毁
    }
}
