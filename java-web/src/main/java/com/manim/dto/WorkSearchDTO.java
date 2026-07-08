package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 搜索结果 - 动画作品
 */
@Schema(description = "搜索结果-动画作品")
public class WorkSearchDTO {

    @Schema(description = "作品 ID")
    private Integer workId;

    @Schema(description = "作品标题")
    private String title;

    @Schema(description = "封面图 URL")
    private String cover;

    @Schema(description = "作者昵称")
    private String authorName;

    @Schema(description = "点赞数")
    private Integer likeCount;

    public WorkSearchDTO() {}

    public WorkSearchDTO(Integer workId, String title, String cover, String authorName, Integer likeCount) {
        this.workId = workId;
        this.title = title;
        this.cover = cover;
        this.authorName = authorName;
        this.likeCount = likeCount;
    }

    public Integer getWorkId() { return workId; }
    public void setWorkId(Integer workId) { this.workId = workId; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getCover() { return cover; }
    public void setCover(String cover) { this.cover = cover; }

    public String getAuthorName() { return authorName; }
    public void setAuthorName(String authorName) { this.authorName = authorName; }

    public Integer getLikeCount() { return likeCount; }
    public void setLikeCount(Integer likeCount) { this.likeCount = likeCount; }
}
