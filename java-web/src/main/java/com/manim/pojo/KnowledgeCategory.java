package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 百科知识分类实体
 * <p>
 * 对应 knowledge_category 表：
 * 首页分类导航 + 百科分类列表的数据基础
 * </p>
 */
@TableName("knowledge_category")
@Schema(description = "百科知识分类")
public class KnowledgeCategory {

    @TableId(type = IdType.AUTO)
    @Schema(description = "分类 ID")
    private Integer id;

    @Schema(description = "分类名称（如：算法、数据结构）")
    private String name;

    @Schema(description = "分类图标 URL")
    private String icon;

    @Schema(description = "分类描述")
    private String description;

    @Schema(description = "排序权重（越小越靠前）")
    private Integer sortOrder;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getName() { return name; }
    public void setName(String name) { this.name = name; }

    public String getIcon() { return icon; }
    public void setIcon(String icon) { this.icon = icon; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public Integer getSortOrder() { return sortOrder; }
    public void setSortOrder(Integer sortOrder) { this.sortOrder = sortOrder; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }
}
