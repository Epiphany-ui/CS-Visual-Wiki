package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.Animation;
import org.apache.ibatis.annotations.Mapper;

/**
 * 动画资源数据访问接口
 */
@Mapper
public interface AnimationMapper extends BaseMapper<Animation> {

}
