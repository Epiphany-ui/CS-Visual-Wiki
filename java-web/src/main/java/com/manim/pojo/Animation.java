package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 动画资源实体（词条配套演示动画）
 * <p>
 * 对应 animation 表：
 * 每个知识词条可绑定 N 个演示动画
 * </p>
 */
@TableName("animation")
@Schema(description = "动画资源（词条配套）")
public class Animation {

    @TableId(type = IdType.AUTO)
    @Schema(description = "动画 ID")
    private Integer id;

    @Schema(description = "关联词条 ID")
    private Integer knowledgeId;

    @Schema(description = "动画标题")
    private String title;

    @Schema(description = "视频文件路径")
    private String videoPath;

    @Schema(description = "时长（秒）")
    private Integer duration;

    @Schema(description = "播放次数")
    private Integer playCount;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getKnowledgeId() { return knowledgeId; }
    public void setKnowledgeId(Integer knowledgeId) { this.knowledgeId = knowledgeId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getVideoPath() { return videoPath; }
    public void setVideoPath(String videoPath) { this.videoPath = videoPath; }

    public Integer getDuration() { return duration; }
    public void setDuration(Integer duration) { this.duration = duration; }

    public Integer getPlayCount() { return playCount; }
    public void setPlayCount(Integer playCount) { this.playCount = playCount; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
