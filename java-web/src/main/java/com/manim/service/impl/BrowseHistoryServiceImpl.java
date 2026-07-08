package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.BrowseHistoryMapper;
import com.manim.pojo.BrowseHistory;
import com.manim.service.BrowseHistoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class BrowseHistoryServiceImpl implements BrowseHistoryService {

    @Autowired
    private BrowseHistoryMapper browseHistoryMapper;

    @Override
    public void record(Integer userId, Integer targetType, Integer targetId) {
        BrowseHistory history = new BrowseHistory();
        history.setUserId(userId);
        history.setTargetType(targetType);
        history.setTargetId(targetId);
        browseHistoryMapper.insert(history);
    }

    @Override
    public List<BrowseHistory> listByUser(Integer userId, Integer page, Integer size) {
        QueryWrapper<BrowseHistory> qw = new QueryWrapper<>();
        qw.eq("user_id", userId);
        qw.orderByDesc("create_time");
        qw.last("LIMIT " + ((page - 1) * size) + "," + size);
        return browseHistoryMapper.selectList(qw);
    }
}
