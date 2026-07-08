package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.KnowledgeEntry;
import org.apache.ibatis.annotations.Mapper;

/**
 * 知识词条数据访问接口
 */
@Mapper
public interface KnowledgeEntryMapper extends BaseMapper<KnowledgeEntry> {

}
