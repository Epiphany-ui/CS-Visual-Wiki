package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.TemplateMapper;
import com.manim.pojo.Template;
import com.manim.service.TemplateService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class TemplateServiceImpl implements TemplateService {

    @Autowired
    private TemplateMapper templateMapper;

    @Override
    public Template getById(Integer id) {
        return templateMapper.selectById(id);
    }

    @Override
    public List<Template> listByCategory(String category, Integer page, Integer size) {
        QueryWrapper<Template> qw = new QueryWrapper<>();
        if (category != null && !category.isEmpty()) qw.eq("category", category);
        qw.orderByDesc("use_count");
        qw.last("LIMIT " + ((page - 1) * size) + "," + size);
        return templateMapper.selectList(qw);
    }
}
