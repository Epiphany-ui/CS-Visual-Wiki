package com.manim.service;

import com.manim.pojo.UserCollect;

import java.util.List;

/**
 * 用户收藏业务接口（多态）
 */
public interface UserCollectService {

    boolean toggleCollect(Integer userId, Integer targetType, Integer targetId, boolean isCollect);

    List<UserCollect> listByUser(Integer userId, Integer targetType, Integer page, Integer size);

    boolean isCollected(Integer userId, Integer targetType, Integer targetId);
}
