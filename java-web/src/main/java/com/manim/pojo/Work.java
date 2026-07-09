package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 动画作品实体（成品）
 * <p>
 * 对应 work 表：
 * 社区画廊核心实体，支持 Fork 溯源链和热度排序
 * </p>
 */
@TableName("work")
@Schema(description = "动画作品（成品）")
public class Work {

    @TableId(type = IdType.AUTO)
    @Schema(description = "作品 ID")
    private Integer id;

    @Schema(description = "作者 ID")
    private Integer userId;

    @Schema(description = "作品标题")
    private String title;

    @Schema(description = "作品描述")
    private String description;

    @Schema(description = "Manim 源码")
    private String manimCode;

    @Schema(description = "视频文件路径")
    private String videoPath;

    @Schema(description = "封面图 URL")
    private String cover;

    @Schema(description = "标签列表（逗号分隔）")
    private String tags;

    @Schema(description = "是否公开：0-私密 1-公开")
    private Integer isPublic;

    @Schema(description = "Fork 来源作品 ID（溯源）")
    private Integer sourceWorkId;

    @Schema(description = "播放/查看次数")
    private Integer viewCount;

    @Schema(description = "点赞数")
    private Integer likeCount;

    @Schema(description = "收藏数")
    private Integer collectCount;

    @Schema(description = "Fork 次数")
    private Integer forkCount;

    @Schema(description = "状态：0-草稿 1-已发布")
    private Integer status;

    @TableField(fill = FieldFill.INSERT)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Schema(description = "更新时间")
    private LocalDateTime updateTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getManimCode() { return manimCode; }
    public void setManimCode(String manimCode) { this.manimCode = manimCode; }

    public String getVideoPath() { return videoPath; }
    public void setVideoPath(String videoPath) { this.videoPath = videoPath; }

    public String getCover() { return cover; }
    public void setCover(String cover) { this.cover = cover; }

    public String getTags() { return tags; }
    public void setTags(String tags) { this.tags = tags; }

    public Integer getIsPublic() { return isPublic; }
    public void setIsPublic(Integer isPublic) { this.isPublic = isPublic; }

    public Integer getSourceWorkId() { return sourceWorkId; }
    public void setSourceWorkId(Integer sourceWorkId) { this.sourceWorkId = sourceWorkId; }

    public Integer getViewCount() { return viewCount; }
    public void setViewCount(Integer viewCount) { this.viewCount = viewCount; }

    public Integer getLikeCount() { return likeCount; }
    public void setLikeCount(Integer likeCount) { this.likeCount = likeCount; }

    public Integer getCollectCount() { return collectCount; }
    public void setCollectCount(Integer collectCount) { this.collectCount = collectCount; }

    public Integer getForkCount() { return forkCount; }
    public void setForkCount(Integer forkCount) { this.forkCount = forkCount; }

    public Integer getStatus() { return status; }
    public void setStatus(Integer status) { this.status = status; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }

    public LocalDateTime getUpdateTime() { return updateTime; }
    public void setUpdateTime(LocalDateTime updateTime) { this.updateTime = updateTime; }
}
