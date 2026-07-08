package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 浏览历史实体
 * <p>
 * 对应 browse_history 表：
 * 记录用户浏览过的词条/作品/模板，按时间倒序展示
 * </p>
 */
@TableName("browse_history")
@Schema(description = "浏览历史")
public class BrowseHistory {

    @TableId(type = IdType.AUTO)
    @Schema(description = "主键")
    private Integer id;

    @Schema(description = "用户 ID")
    private Integer userId;

    @Schema(description = "浏览类型：1-词条 2-作品 3-模板")
    private Integer targetType;

    @Schema(description = "目标资源 ID")
    private Integer targetId;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public Integer getTargetType() { return targetType; }
    public void setTargetType(Integer targetType) { this.targetType = targetType; }

    public Integer getTargetId() { return targetId; }
    public void setTargetId(Integer targetId) { this.targetId = targetId; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
