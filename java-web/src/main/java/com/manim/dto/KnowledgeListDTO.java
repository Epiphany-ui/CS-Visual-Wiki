package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 百科知识点列表 DTO（分类列表 + 推荐列表通用）
 */
@Schema(description = "百科知识点列表项")
public class KnowledgeListDTO {

    @Schema(description = "词条 ID")
    private Integer id;

    @Schema(description = "词条标题")
    private String title;

    @Schema(description = "简短摘要")
    private String summary;

    @Schema(description = "难度：1-入门 2-中等 3-困难")
    private Integer difficulty;

    @Schema(description = "配套动画数量")
    private Integer animationCount;

    public KnowledgeListDTO() {}

    public KnowledgeListDTO(Integer id, String title, String summary, Integer difficulty, Integer animationCount) {
        this.id = id;
        this.title = title;
        this.summary = summary;
        this.difficulty = difficulty;
        this.animationCount = animationCount;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public Integer getDifficulty() { return difficulty; }
    public void setDifficulty(Integer difficulty) { this.difficulty = difficulty; }

    public Integer getAnimationCount() { return animationCount; }
    public void setAnimationCount(Integer animationCount) { this.animationCount = animationCount; }
}
