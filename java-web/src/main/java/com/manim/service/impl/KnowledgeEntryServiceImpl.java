package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.KnowledgeEntryMapper;
import com.manim.pojo.KnowledgeEntry;
import com.manim.service.KnowledgeEntryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class KnowledgeEntryServiceImpl implements KnowledgeEntryService {

    @Autowired
    private KnowledgeEntryMapper knowledgeEntryMapper;

    @Override
    public KnowledgeEntry getById(Integer id) {
        KnowledgeEntry entry = knowledgeEntryMapper.selectById(id);
        if (entry != null) {
            entry.setViewCount(entry.getViewCount() == null ? 1 : entry.getViewCount() + 1);
            knowledgeEntryMapper.updateById(entry);
        }
        return entry;
    }

    @Override
    public List<KnowledgeEntry> listByCategory(Integer categoryId, Integer difficulty, Integer page, Integer size) {
        QueryWrapper<KnowledgeEntry> qw = new QueryWrapper<>();
        if (categoryId != null) qw.eq("category_id", categoryId);
        if (difficulty != null) qw.eq("difficulty", difficulty);
        qw.orderByDesc("view_count");
        qw.last("LIMIT " + ((page - 1) * size) + "," + size);
        return knowledgeEntryMapper.selectList(qw);
    }

    @Override
    public List<KnowledgeEntry> getRecommended(Integer knowledgeId) {
        KnowledgeEntry current = knowledgeEntryMapper.selectById(knowledgeId);
        if (current == null) return List.of();
        // 推荐同分类下其他词条
        QueryWrapper<KnowledgeEntry> qw = new QueryWrapper<>();
        qw.eq("category_id", current.getCategoryId())
           .ne("id", knowledgeId)
           .orderByDesc("view_count")
           .last("LIMIT 5");
        return knowledgeEntryMapper.selectList(qw);
    }
}
