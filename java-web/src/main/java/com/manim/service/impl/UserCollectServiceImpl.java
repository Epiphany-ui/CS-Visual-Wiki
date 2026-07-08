package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.UserCollectMapper;
import com.manim.pojo.UserCollect;
import com.manim.service.UserCollectService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class UserCollectServiceImpl implements UserCollectService {

    @Autowired
    private UserCollectMapper userCollectMapper;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean toggleCollect(Integer userId, Integer targetType, Integer targetId, boolean isCollect) {
        QueryWrapper<UserCollect> qw = new QueryWrapper<>();
        qw.eq("user_id", userId).eq("target_type", targetType).eq("target_id", targetId);
        UserCollect existing = userCollectMapper.selectOne(qw);

        if (isCollect && existing == null) {
            UserCollect collect = new UserCollect();
            collect.setUserId(userId);
            collect.setTargetType(targetType);
            collect.setTargetId(targetId);
            userCollectMapper.insert(collect);
            return true;
        } else if (!isCollect && existing != null) {
            userCollectMapper.deleteById(existing.getId());
            return true;
        }
        return false;
    }

    @Override
    public List<UserCollect> listByUser(Integer userId, Integer targetType, Integer page, Integer size) {
        QueryWrapper<UserCollect> qw = new QueryWrapper<>();
        qw.eq("user_id", userId);
        if (targetType != null) qw.eq("target_type", targetType);
        qw.orderByDesc("create_time");
        qw.last("LIMIT " + ((page - 1) * size) + "," + size);
        return userCollectMapper.selectList(qw);
    }

    @Override
    public boolean isCollected(Integer userId, Integer targetType, Integer targetId) {
        QueryWrapper<UserCollect> qw = new QueryWrapper<>();
        qw.eq("user_id", userId).eq("target_type", targetType).eq("target_id", targetId);
        return userCollectMapper.selectCount(qw) > 0;
    }
}
