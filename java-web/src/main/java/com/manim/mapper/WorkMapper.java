package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.Work;
import org.apache.ibatis.annotations.Mapper;

/**
 * 作品数据访问接口
 */
@Mapper
public interface WorkMapper extends BaseMapper<Work> {

}
