package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.LambdaQueryWrapper;
import com.manim.mapper.UserMapper;
import com.manim.pojo.User;
import com.manim.service.UserService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

/**
 * 用户业务实现
 */
@Service
public class UserServiceImpl implements UserService {

    @Autowired
    private UserMapper userMapper;

    /**
     * 根据用户名查询用户
     *
     * @param username 登录账号（唯一）
     * @return 用户对象；不存在返回 null
     */
    @Override
    public User findByUsername(String username) {
        return userMapper.selectOne(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, username)
        );
    }

    @Override
    public User getById(Integer id) {
        return userMapper.selectById(id);
    }

    /**
     * 用户登录校验
     * <p>密码比对采用 MD5 密文比对（存入时已是加密状态）。</p>
     *
     * @param username          用户名
     * @param encryptedPassword 已加密的密码（MD5）
     * @return 匹配成功返回用户对象；失败返回 null
     */
    @Override
    public User login(String username, String encryptedPassword) {
        if (username == null || encryptedPassword == null) {
            return null;
        }
        User user = userMapper.selectOne(
                new LambdaQueryWrapper<User>()
                        .eq(User::getUsername, username.trim())
        );
        if (user == null) {
            return null;
        }
        // 密码比对（存入时已是 MD5，此处直接比对密文）
        if (!encryptedPassword.equals(user.getPassword())) {
            return null;
        }
        return user;
    }

    /**
     * 用户注册
     * <p>调用前需确保 username 未重复，password 已 MD5 加密。</p>
     *
     * @param user 用户对象（含 username + 已加密的 password）
     */
    @Override
    public void register(User user) {
        userMapper.insert(user);
    }

    @Override
    public void updateProfile(Integer userId, String nickname, String avatar, String intro) {
        User user = userMapper.selectById(userId);
        if (user == null) return;
        if (nickname != null) user.setNickname(nickname);
        if (avatar != null) user.setAvatar(avatar);
        if (intro != null) user.setIntro(intro);
        userMapper.updateById(user);
    }
}
