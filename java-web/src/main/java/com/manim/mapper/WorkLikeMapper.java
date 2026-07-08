package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.WorkLike;
import org.apache.ibatis.annotations.Mapper;

/**
 * 作品点赞数据访问接口
 */
@Mapper
public interface WorkLikeMapper extends BaseMapper<WorkLike> {

}
