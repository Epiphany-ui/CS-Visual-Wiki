package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 搜索结果 - 知识词条
 */
@Schema(description = "搜索结果-知识词条")
public class KnowledgeSearchDTO {

    @Schema(description = "词条 ID")
    private Integer id;

    @Schema(description = "词条标题")
    private String title;

    @Schema(description = "简短摘要")
    private String summary;

    @Schema(description = "难度：1-入门 2-中等 3-困难")
    private Integer difficulty;

    public KnowledgeSearchDTO() {}

    public KnowledgeSearchDTO(Integer id, String title, String summary, Integer difficulty) {
        this.id = id;
        this.title = title;
        this.summary = summary;
        this.difficulty = difficulty;
    }

    public Integer getId() { return id; }
    public void setId(Integer id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getSummary() { return summary; }
    public void setSummary(String summary) { this.summary = summary; }

    public Integer getDifficulty() { return difficulty; }
    public void setDifficulty(Integer difficulty) { this.difficulty = difficulty; }
}
