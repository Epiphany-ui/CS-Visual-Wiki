package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 首页分类导航 DTO
 * <p>展示分类名称、图标和该分类下的知识点数量</p>
 */
@Schema(description = "首页分类导航")
public class CategoryDTO {

    @Schema(description = "分类 ID")
    private Integer id;

    @Schema(description = "分类名称（如：算法、数据结构）")
    private String name;

    @Schema(description = "分类图标 URL")
    private String icon;

    @Schema(description = "该分类下的知识点数量")
    private Integer entryCount;

    public CategoryDTO() {}

    public CategoryDTO(Integer id, String name, String icon, Integer entryCount) {
        this.id = id;
        this.name = name;
        this.icon = icon;
        this.entryCount = entryCount;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getIcon() { return icon; }
    public void setIcon(String icon) { this.icon = icon; }

    public Integer getEntryCount() { return entryCount; }
    public void setEntryCount(Integer entryCount) { this.entryCount = entryCount; }
}
