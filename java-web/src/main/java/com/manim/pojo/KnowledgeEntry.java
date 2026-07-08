package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 百科知识词条实体
 * <p>
 * 对应 knowledge_entry 表：
 * 百科详情页五段式内容（定义→原理→示例→复杂度→误区）
 * </p>
 */
@TableName("knowledge_entry")
@Schema(description = "百科知识词条")
public class KnowledgeEntry {

    @TableId(type = IdType.AUTO)
    @Schema(description = "词条 ID")
    private Integer id;

    @Schema(description = "所属分类 ID")
    private Integer categoryId;

    @Schema(description = "词条标题")
    private String title;

    @Schema(description = "简短摘要")
    private String summary;

    @Schema(description = "定义")
    private String definition;

    @Schema(description = "核心原理")
    private String principle;

    @Schema(description = "过程示例")
    private String example;

    @Schema(description = "复杂度分析")
    private String complexity;

    @Schema(description = "常见误区")
    private String misconception;

    @Schema(description = "来源/参考文献")
    private String source;

    @Schema(description = "难度：1-入门 2-中等 3-困难")
    private Integer difficulty;

    @Schema(description = "浏览次数")
    private Integer viewCount;

    @TableField(fill = FieldFill.INSERT)
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    @TableField(fill = FieldFill.INSERT_UPDATE)
    @Schema(description = "更新时间")
    private LocalDateTime updateTime;

    // ===== getters & setters =====

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public Integer getCategoryId() { return categoryId; }
    public void setCategoryId(Integer categoryId) { this.categoryId = categoryId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public String getDefinition() { return definition; }
    public void setDefinition(String definition) { this.definition = definition; }

    public String getPrinciple() { return principle; }
    public void setPrinciple(String principle) { this.principle = principle; }

    public String getExample() { return example; }
    public void setExample(String example) { this.example = example; }

    public String getComplexity() { return complexity; }
    public void setComplexity(String complexity) { this.complexity = complexity; }

    public String getMisconception() { return misconception; }
    public void setMisconception(String misconception) { this.misconception = misconception; }

    public String getSource() { return source; }
    public void setSource(String source) { this.source = source; }

    public Integer getDifficulty() { return difficulty; }
    public void setDifficulty(Integer difficulty) { this.difficulty = difficulty; }

    public Integer getViewCount() { return viewCount; }
    public void setViewCount(Integer viewCount) { this.viewCount = viewCount; }

    public LocalDateTime getCreateTime() { return createTime; }
    public void setCreateTime(LocalDateTime createTime) { this.createTime = createTime; }

    public LocalDateTime getUpdateTime() { return updateTime; }
    public void setUpdateTime(LocalDateTime updateTime) { this.updateTime = updateTime; }
}
