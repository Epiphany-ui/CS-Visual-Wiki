package com.manim.service;

import com.manim.pojo.KnowledgeEntry;

import java.util.List;

/**
 * 知识词条业务接口
 */
public interface KnowledgeEntryService {

    KnowledgeEntry getById(Integer id);

    List<KnowledgeEntry> listByCategory(Integer categoryId, Integer difficulty, Integer page, Integer size);

    List<KnowledgeEntry> getRecommended(Integer knowledgeId);
}
