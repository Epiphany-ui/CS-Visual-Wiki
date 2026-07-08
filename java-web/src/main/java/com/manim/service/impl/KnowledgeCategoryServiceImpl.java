package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.dto.CategoryDTO;
import com.manim.mapper.KnowledgeCategoryMapper;
import com.manim.mapper.KnowledgeEntryMapper;
import com.manim.pojo.KnowledgeCategory;
import com.manim.pojo.KnowledgeEntry;
import com.manim.service.KnowledgeCategoryService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
public class KnowledgeCategoryServiceImpl implements KnowledgeCategoryService {

    @Autowired
    private KnowledgeCategoryMapper knowledgeCategoryMapper;

    @Autowired
    private KnowledgeEntryMapper knowledgeEntryMapper;

    @Override
    public List<KnowledgeCategory> listAll() {
        return knowledgeCategoryMapper.selectList(
                new QueryWrapper<KnowledgeCategory>().orderByAsc("sort_order"));
    }

    @Override
    public KnowledgeCategory getById(Integer id) {
        return knowledgeCategoryMapper.selectById(id);
    }

    @Override
    public List<CategoryDTO> listWithEntryCount() {
        List<KnowledgeCategory> categories = listAll();
        return categories.stream().map(c -> {
            int count = knowledgeEntryMapper.selectCount(
                    new QueryWrapper<KnowledgeEntry>()
                            .eq("category_id", c.getId())
            ).intValue();
            return new CategoryDTO(c.getId(), c.getName(), c.getIcon(), count);
        }).collect(Collectors.toList());
    }
}
