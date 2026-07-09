package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.WorkComment;
import org.apache.ibatis.annotations.Mapper;

/**
 * 作品评论数据访问接口
 */
@Mapper
public interface WorkCommentMapper extends BaseMapper<WorkComment> {

}
