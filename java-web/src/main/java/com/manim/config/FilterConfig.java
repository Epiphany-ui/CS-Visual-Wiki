package com.manim.config;

import com.manim.filter.AuthFilter;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 过滤器注册配置
 * <p>
 * 将 AuthFilter 注册到容器，仅拦截 /api/* 路径，
 * 页面跳转接口（/、/tasks、/task/*）不受影响。
 * </p>
 */
@Configuration
public class FilterConfig {

    @Bean
    public FilterRegistrationBean<AuthFilter> authFilterRegistration(AuthFilter authFilter) {
        FilterRegistrationBean<AuthFilter> registration = new FilterRegistrationBean<>();
        registration.setFilter(authFilter);
        // 仅拦截 /api/* 路径，避免对静态资源和页面请求做无谓的 token 校验
        registration.addUrlPatterns("/api/*");
        // 多个过滤器时的执行顺序，数值越小越优先
        registration.setOrder(1);
        registration.setName("authFilter");
        return registration;
    }
}
