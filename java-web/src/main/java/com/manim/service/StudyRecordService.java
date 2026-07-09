package com.manim.service;

import com.manim.pojo.StudyRecord;

import java.util.Map;

/**
 * 学习打卡记录业务接口
 */
public interface StudyRecordService {

    void checkin(Integer userId, Integer knowledgeId, Integer studyDuration);

    Map<String, Object> getStudyStat(Integer userId);
}
