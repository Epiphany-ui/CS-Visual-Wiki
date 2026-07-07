package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.Task;
import org.apache.ibatis.annotations.Mapper;

/**
 * 任务数据访问接口
 */
@Mapper
public interface TaskMapper extends BaseMapper<Task> {

}
