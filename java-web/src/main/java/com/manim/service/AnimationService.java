package com.manim.service;

import com.manim.pojo.Animation;

import java.util.List;

/**
 * 动画资源业务接口
 */
public interface AnimationService {

    List<Animation> listByKnowledgeId(Integer knowledgeId);
}
