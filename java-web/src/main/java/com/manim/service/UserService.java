package com.manim.service;

import com.manim.pojo.User;

/**
 * 用户业务接口
 */
public interface UserService {

    /**
     * 根据用户名查询用户
     */
    User findByUsername(String username);

    /**
     * 根据用户 ID 查询用户
     */
    User getById(Integer id);

    /**
     * 用户登录校验
     *
     * @param username 用户名
     * @param password 密码（已加密）
     * @return 登录成功返回用户对象，失败返回 null
     */
    User login(String username, String password);

    /**
     * 用户注册
     *
     * @param user 用户对象（含 username + 已加密的 password）
     */
    void register(User user);

    /**
     * 更新用户资料
     *
     * @param userId   用户 ID
     * @param nickname 昵称（可选）
     * @param avatar   头像 URL（可选）
     * @param intro    简介（可选）
     */
    void updateProfile(Integer userId, String nickname, String avatar, String intro);
}
