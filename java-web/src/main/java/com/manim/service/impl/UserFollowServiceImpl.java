package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.UserFollowMapper;
import com.manim.pojo.UserFollow;
import com.manim.service.UserFollowService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class UserFollowServiceImpl implements UserFollowService {

    @Autowired
    private UserFollowMapper userFollowMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean toggleFollow(Integer followerId, Integer followeeId, boolean isFollow) {
        if (followerId.equals(followeeId)) return false;

        QueryWrapper<UserFollow> qw = new QueryWrapper<>();
        qw.eq("follower_id", followerId).eq("followee_id", followeeId);
        UserFollow existing = userFollowMapper.selectOne(qw);

        if (isFollow && existing == null) {
            UserFollow follow = new UserFollow();
            follow.setFollowerId(followerId);
            follow.setFolloweeId(followeeId);
            userFollowMapper.insert(follow);
            return true;
        } else if (!isFollow && existing != null) {
            userFollowMapper.deleteById(existing.getId());
            return true;
        }
        return false;
    }

    @Override
    public int getFollowerCount(Integer userId) {
        return userFollowMapper.selectCount(
                new QueryWrapper<UserFollow>().eq("followee_id", userId)).intValue();
    }

    @Override
    public int getFolloweeCount(Integer userId) {
        return userFollowMapper.selectCount(
                new QueryWrapper<UserFollow>().eq("follower_id", userId)).intValue();
    }
}
