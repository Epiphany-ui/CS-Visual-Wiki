package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 用户关注关系实体
 * <p>
 * 对应 user_follow 表：
 * 关注/粉丝关系，follower_id → followee_id 单向关系
 * </p>
 */
@TableName("user_follow")
@Schema(description = "用户关注关系")
public class UserFollow {

    @TableId(type = IdType.AUTO)
    @Schema(description = "主键")
    private Integer id;

    @Schema(description = "关注者 ID")
    private Integer followerId;

    @Schema(description = "被关注者 ID")
    private Integer followeeId;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getFollowerId() { return followerId; }
    public void setFollowerId(Integer followerId) { this.followerId = followerId; }

    public Integer getFolloweeId() { return followeeId; }
    public void setFolloweeId(Integer followeeId) { this.followeeId = followeeId; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
