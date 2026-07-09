package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 用户收藏实体（多态）
 * <p>
 * 对应 user_collect 表：
 * target_type + target_id 多态设计，统一管理词条/作品/模板收藏
 * </p>
 */
@TableName("user_collect")
@Schema(description = "用户收藏（多态）")
public class UserCollect {

    @TableId(type = IdType.AUTO)
    @Schema(description = "主键")
    private Integer id;

    @Schema(description = "用户 ID")
    private Integer userId;

    @Schema(description = "收藏类型：1-词条 2-作品 3-模板")
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
