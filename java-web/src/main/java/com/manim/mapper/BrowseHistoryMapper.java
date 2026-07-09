package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.BrowseHistory;
import org.apache.ibatis.annotations.Mapper;

/**
 * 浏览历史数据访问接口
 */
@Mapper
public interface BrowseHistoryMapper extends BaseMapper<BrowseHistory> {

}
