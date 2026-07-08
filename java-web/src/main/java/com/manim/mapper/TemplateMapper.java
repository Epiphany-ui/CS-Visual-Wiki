package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.Template;
import org.apache.ibatis.annotations.Mapper;

/**
 * 创作模板数据访问接口
 */
@Mapper
public interface TemplateMapper extends BaseMapper<Template> {

}
