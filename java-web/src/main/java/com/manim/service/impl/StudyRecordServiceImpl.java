package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.StudyRecordMapper;
import com.manim.pojo.StudyRecord;
import com.manim.service.StudyRecordService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.HashMap;
import java.util.Map;

@Service
public class StudyRecordServiceImpl implements StudyRecordService {

    @Autowired
    private StudyRecordMapper studyRecordMapper;

    @Override
    public void checkin(Integer userId, Integer knowledgeId, Integer studyDuration) {
        StudyRecord record = new StudyRecord();
        record.setUserId(userId);
        record.setKnowledgeId(knowledgeId);
        record.setStudyDuration(studyDuration);
        record.setCheckinDate(LocalDate.now());
        studyRecordMapper.insert(record);
    }

    @Override
    public Map<String, Object> getStudyStat(Integer userId) {
        Map<String, Object> stat = new HashMap<>();

        // 总学习时长
        Long totalDuration = studyRecordMapper.selectList(
                new QueryWrapper<StudyRecord>().eq("user_id", userId))
                .stream().mapToLong(StudyRecord::getStudyDuration).sum();

        // 打卡天数（去重）
        Long checkinDays = studyRecordMapper.selectList(
                new QueryWrapper<StudyRecord>().eq("user_id", userId)
                        .select("DISTINCT checkin_date")).stream().count();

        stat.put("totalStudyMinutes", totalDuration / 60);
        stat.put("checkinDays", checkinDays);
        return stat;
    }
}
