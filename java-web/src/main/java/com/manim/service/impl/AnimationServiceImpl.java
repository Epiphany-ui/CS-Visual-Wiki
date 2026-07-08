package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.AnimationMapper;
import com.manim.pojo.Animation;
import com.manim.service.AnimationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class AnimationServiceImpl implements AnimationService {

    @Autowired
    private AnimationMapper animationMapper;

    @Override
    public List<Animation> listByKnowledgeId(Integer knowledgeId) {
        return animationMapper.selectList(
                new QueryWrapper<Animation>().eq("knowledge_id", knowledgeId));
    }
}
