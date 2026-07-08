package com.manim.service;

/**
 * 用户关注关系业务接口
 */
public interface UserFollowService {

    boolean toggleFollow(Integer followerId, Integer followeeId, boolean isFollow);

    int getFollowerCount(Integer userId);

    int getFolloweeCount(Integer userId);
}
