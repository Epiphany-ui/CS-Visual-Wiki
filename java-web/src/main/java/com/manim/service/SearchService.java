package com.manim.service;

import com.manim.dto.KnowledgeSearchDTO;
import com.manim.dto.WorkSearchDTO;
import com.manim.dto.TemplateSearchDTO;
import com.manim.dto.UserSearchDTO;

import java.util.List;
import java.util.Map;

/**
 * 全局搜索业务接口
 */
public interface SearchService {

    /**
     * 全局搜索（知识点/作品/模板/用户）
     *
     * @param keyword 搜索关键词
     * @param page    页码（暂未使用，固定各取 5 条）
     * @param size    每页条数
     * @return 包含四个列表的 Map
     */
    Map<String, Object> searchAll(String keyword, Integer page, Integer size);
}
