package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 作品评论实体
 * <p>
 * 对应 work_comment 表：
 * reply_to_id 实现楼中楼回复结构
 * </p>
 */
@TableName("work_comment")
@Schema(description = "作品评论")
public class WorkComment {

    @TableId(type = IdType.AUTO)
    @Schema(description = "评论 ID")
    private Integer id;

    @Schema(description = "所属作品 ID")
    private Integer workId;

    @Schema(description = "评论用户 ID")
    private Integer userId;

    @Schema(description = "评论内容")
    private String content;

    @Schema(description = "回复目标评论 ID（楼中楼）")
    private Integer replyToId;

    @TableField(fill = FieldFill.INSERT)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getWorkId() { return workId; }
    public void setWorkId(Integer workId) { this.workId = workId; }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public String getContent() { return content; }
    public void setContent(String content) { this.content = content; }

    public Integer getReplyToId() { return replyToId; }
    public void setReplyToId(Integer replyToId) { this.replyToId = replyToId; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
