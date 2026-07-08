package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.SandboxDraft;
import org.apache.ibatis.annotations.Mapper;

/**
 * 沙箱草稿数据访问接口
 */
@Mapper
public interface SandboxDraftMapper extends BaseMapper<SandboxDraft> {

}
