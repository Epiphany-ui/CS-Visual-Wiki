package com.manim.mapper;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.manim.pojo.StudyRecord;
import org.apache.ibatis.annotations.Mapper;

/**
 * 学习打卡记录数据访问接口
 */
@Mapper
public interface StudyRecordMapper extends BaseMapper<StudyRecord> {

}
