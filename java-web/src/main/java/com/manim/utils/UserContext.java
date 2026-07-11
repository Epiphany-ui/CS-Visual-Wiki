package com.manim.utils;

/**
 * 当前请求用户上下文（ThreadLocal）
 * <p>
 * 在 Filter 中将 JWT 中解析出的用户名存入此处，
 * Controller / Service 层可直接通过 {@link #getUsername()} 获取当前登录用户，
 * 避免在方法参数中层层传递。
 * </p>
 * <b>注意：</b>请求结束后必须在 Filter 中调用 {@link #remove()} 清理，防止内存泄漏。
 * </p>
 */
public class UserContext {

    private static final ThreadLocal<String> USERNAME_HOLDER = new ThreadLocal<>();

    /**
     * 设置当前请求的用户名
     */
    public static void setUsername(String username) {
        USERNAME_HOLDER.set(username);
    }

    /**
     * 获取当前请求的用户名
     */
    public static String getUsername() {
        return USERNAME_HOLDER.get();
    }

    /**
     * 清理当前请求的用户上下文（请求结束时在 Filter 中调用）
     */
    public static void remove() {
        USERNAME_HOLDER.remove();
    }
}
