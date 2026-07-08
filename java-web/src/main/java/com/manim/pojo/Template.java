package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 创作模板实体
 * <p>
 * 对应 template 表：
 * 零代码创作的核心，config_schema 存 JSON 参数表单描述
 * </p>
 */
@TableName("template")
@Schema(description = "创作模板")
public class Template {

    @TableId(type = IdType.AUTO)
    @Schema(description = "模板 ID")
    private Integer id;

    @Schema(description = "模板名称")
    private String name;

    @Schema(description = "模板简介")
    private String description;

    @Schema(description = "封面图片 URL")
    private String cover;

    @Schema(description = "模板分类（排序/树/函数/概率）")
    private String category;

    @Schema(description = "参数配置 JSON Schema")
    private String configSchema;

    @Schema(description = "预览视频路径")
    private String previewVideo;

    @Schema(description = "默认 Manim 代码模板")
    private String defaultCode;

    @Schema(description = "使用次数")
    private Integer useCount;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    @Schema(description = "更新时间")
    private LocalDateTime updateTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getCover() { return cover; }
    public void setCover(String cover) { this.cover = cover; }

    public String getCategory() { return category; }
    public void setCategory(String category) { this.category = category; }

    public String getConfigSchema() { return configSchema; }
    public void setConfigSchema(String configSchema) { this.configSchema = configSchema; }

    public String getPreviewVideo() { return previewVideo; }
    public void setPreviewVideo(String previewVideo) { this.previewVideo = previewVideo; }

    public String getDefaultCode() { return defaultCode; }
    public void setDefaultCode(String defaultCode) { this.defaultCode = defaultCode; }

    public Integer getUseCount() { return useCount; }
    public void setUseCount(Integer useCount) { this.useCount = useCount; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }

    public LocalDateTime getUpdateTime() { return updateTime; }
    public void setUpdateTime(LocalDateTime updateTime) { this.updateTime = updateTime; }
}
