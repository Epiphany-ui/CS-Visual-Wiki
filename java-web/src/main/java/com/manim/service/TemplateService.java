package com.manim.service;

import com.manim.pojo.Template;

import java.util.List;

/**
 * 创作模板业务接口
 */
public interface TemplateService {

    Template getById(Integer id);

    List<Template> listByCategory(String category, Integer page, Integer size);
}
