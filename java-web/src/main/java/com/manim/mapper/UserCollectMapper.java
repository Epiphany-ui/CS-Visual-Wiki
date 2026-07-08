package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.UserCollect;
import org.apache.ibatis.annotations.Mapper;

/**
 * 用户收藏数据访问接口
 */
@Mapper
public interface UserCollectMapper extends BaseMapper<UserCollect> {

}
