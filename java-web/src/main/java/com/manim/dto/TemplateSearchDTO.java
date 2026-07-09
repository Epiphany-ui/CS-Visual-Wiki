package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 搜索结果 - 创作模板
 */
@Schema(description = "搜索结果-创作模板")
public class TemplateSearchDTO {

    @Schema(description = "模板 ID")
    private Integer id;

    @Schema(description = "模板名称")
    private String name;

    @Schema(description = "模板简介")
    private String description;

    @Schema(description = "使用次数")
    private Integer useCount;

    public TemplateSearchDTO() {}

    public TemplateSearchDTO(Integer id, String name, String description, Integer useCount) {
        this.id = id;
        this.name = name;
        this.description = description;
        this.useCount = useCount;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public Integer getUseCount() { return useCount; }
    public void setUseCount(Integer useCount) { this.useCount = useCount; }
}
