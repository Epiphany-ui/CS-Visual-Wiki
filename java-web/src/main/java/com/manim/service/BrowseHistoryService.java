package com.manim.service;

import com.manim.pojo.BrowseHistory;

import java.util.List;

/**
 * 浏览历史业务接口
 */
public interface BrowseHistoryService {

    void record(Integer userId, Integer targetType, Integer targetId);

    List<BrowseHistory> listByUser(Integer userId, Integer page, Integer size);
}
