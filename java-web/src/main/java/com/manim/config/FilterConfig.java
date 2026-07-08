package com.manim.config;

import com.manim.filter.AuthFilter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 过滤器注册配置
 * <p>
 * 将 {@link AuthFilter} 注册到 /api/v1/* 路径，
 * 白名单内的路径不受 token 校验。
 * </p>
 */
@Configuration
public class FilterConfig {

    /**
     * 注册 JWT 认证过滤器
     * <ul>
     *   <li>拦截路径：/api/v1/*</li>
     *   <li>执行顺序：order=1（最先执行）</li>
     *   <li>白名单：注册、登录接口（不校验 token）</li>
     * </ul>
     *
     * @return FilterRegistrationBean
     */
    @Bean
    public FilterRegistrationBean<AuthFilter> authFilterRegistration() {
        FilterRegistrationBean<AuthFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(new AuthFilter());
        registration.addUrlPatterns("/api/v1/*");
        registration.setOrder(1);
        registration.setName("authFilter");
        return registration;
    }
}
