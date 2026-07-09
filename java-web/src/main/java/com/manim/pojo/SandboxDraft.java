package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 沙箱创作草稿实体（含版本历史）
 * <p>
 * 对应 sandbox_draft 表：
 * 每保存一次写入一条记录，version 递增标识版本号
 * </p>
 */
@TableName("sandbox_draft")
@Schema(description = "沙箱创作草稿（含版本历史）")
public class SandboxDraft {

    @TableId(type = IdType.AUTO)
    @Schema(description = "草稿 ID")
    private Integer id;

    @Schema(description = "用户 ID")
    private Integer userId;

    @Schema(description = "关联作品 ID（Fork 来源）")
    private Integer workId;

    @Schema(description = "Manim 代码")
    private String manimCode;

    @Schema(description = "预览视频 URL")
    private String previewUrl;

    @Schema(description = "版本号")
    private Integer version;

    @Schema(description = "版本备注")
    private String note;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public Integer getWorkId() { return workId; }
    public void setWorkId(Integer workId) { this.workId = workId; }

    public String getManimCode() { return manimCode; }
    public void setManimCode(String manimCode) { this.manimCode = manimCode; }

    public String getPreviewUrl() { return previewUrl; }
    public void setPreviewUrl(String previewUrl) { this.previewUrl = previewUrl; }

    public Integer getVersion() { return version; }
    public void setVersion(Integer version) { this.version = version; }

    public String getNote() { return note; }
    public void setNote(String note) { this.note = note; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
