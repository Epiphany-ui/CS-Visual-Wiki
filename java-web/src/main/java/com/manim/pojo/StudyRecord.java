package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * 学习打卡记录实体
 * <p>
 * 对应 study_record 表：
 * 记录每次学习打卡行为，用于学习统计
 * </p>
 */
@TableName("study_record")
@Schema(description = "学习打卡记录")
public class StudyRecord {

    @TableId(type = IdType.AUTO)
    @Schema(description = "主键")
    private Integer id;

    @Schema(description = "用户 ID")
    private Integer userId;

    @Schema(description = "学习知识点 ID（可为空）")
    private Integer knowledgeId;

    @Schema(description = "学习时长（秒）")
    private Integer studyDuration;

    @Schema(description = "打卡日期")
    private LocalDate checkinDate;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public Integer getKnowledgeId() { return knowledgeId; }
    public void setKnowledgeId(Integer knowledgeId) { this.knowledgeId = knowledgeId; }

    public Integer getStudyDuration() { return studyDuration; }
    public void setStudyDuration(Integer studyDuration) { this.studyDuration = studyDuration; }

    public LocalDate getCheckinDate() { return checkinDate; }
    public void setCheckinDate(LocalDate checkinDate) { this.checkinDate = checkinDate; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
