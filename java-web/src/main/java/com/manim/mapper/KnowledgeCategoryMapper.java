package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.KnowledgeCategory;
import org.apache.ibatis.annotations.Mapper;

/**
 * 百科分类数据访问接口
 */
@Mapper
public interface KnowledgeCategoryMapper extends BaseMapper<KnowledgeCategory> {

}
