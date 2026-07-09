package com.manim.service;

import com.manim.dto.CategoryDTO;
import com.manim.pojo.KnowledgeCategory;

import java.util.List;

/**
 * 百科分类业务接口
 */
public interface KnowledgeCategoryService {

    List<KnowledgeCategory> listAll();

    KnowledgeCategory getById(Integer id);

    /** 获取分类及其知识点数量（首页分类导航用） */
    List<CategoryDTO> listWithEntryCount();
}
