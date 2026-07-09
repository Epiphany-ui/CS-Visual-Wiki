package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 作品点赞实体
 * <p>
 * 对应 work_like 表：
 * 独立表存储点赞，避免 work 表行锁，支持"我赞过的"
 * </p>
 */
@TableName("work_like")
@Schema(description = "作品点赞")
public class WorkLike {

    @TableId(type = IdType.AUTO)
    @Schema(description = "主键")
    private Integer id;

    @Schema(description = "作品 ID")
    private Integer workId;

    @Schema(description = "点赞用户 ID")
    private Integer userId;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getWorkId() { return workId; }
    public void setWorkId(Integer workId) { this.workId = workId; }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
