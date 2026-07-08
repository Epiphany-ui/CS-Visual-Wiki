package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 首页轮播展示作品 DTO
 * <p>只暴露前端需要的字段，不返回 Work 实体的全部 17 个字段</p>
 */
@Schema(description = "首页轮播作品")
public class CarouselDTO {

    @Schema(description = "作品 ID")
    private Integer workId;

    @Schema(description = "封面图 URL")
    private String cover;

    @Schema(description = "作品标题")
    private String title;

    @Schema(description = "播放量")
    private Integer viewCount;

    @Schema(description = "作者昵称")
    private String authorName;

    public CarouselDTO() {}

    public CarouselDTO(Integer workId, String cover, String title, Integer viewCount, String authorName) {
        this.workId = workId;
        this.cover = cover;
        this.title = title;
        this.viewCount = viewCount;
        this.authorName = authorName;
    }

    public Integer getWorkId() { return workId; }
    public void setWorkId(Integer workId) { this.workId = workId; }

    public String getCover() { return cover; }
    public void setCover(String cover) { this.cover = cover; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public Integer getViewCount() { return viewCount; }
    public void setViewCount(Integer viewCount) { this.viewCount = viewCount; }

    public String getAuthorName() { return authorName; }
    public void setAuthorName(String authorName) { this.authorName = authorName; }
}
