package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 首页作品列表 DTO（精选/最新）
 * <p>展示作品卡片所需字段，不含 manim_code 等敏感/冗余字段</p>
 */
@Schema(description = "首页作品列表项")
public class WorkListDTO {

    @Schema(description = "作品 ID")
    private Integer workId;

    @Schema(description = "作者 ID")
    private Integer authorId;

    @Schema(description = "封面图 URL")
    private String cover;

    @Schema(description = "作品标题")
    private String title;

    @Schema(description = "作品描述")
    private String description;

    @Schema(description = "作者昵称")
    private String authorName;

    @Schema(description = "作者头像 URL")
    private String authorAvatar;

    @Schema(description = "点赞数")
    private Integer likeCount;

    @Schema(description = "播放量")
    private Integer viewCount;

    @Schema(description = "Fork 来源作品 ID")
    private Integer sourceWorkId;

    @Schema(description = "Fork 来源作者名")
    private String sourceAuthorName;

    @Schema(description = "Fork 来源作者 ID")
    private Integer sourceAuthorId;

    @Schema(description = "Fork 次数")
    private Integer forkCount;

    @Schema(description = "视频路径")
    private String videoPath;

    @Schema(description = "发布时间")
    private String createTime;

    public WorkListDTO() {}

    public WorkListDTO(Integer workId, Integer authorId, String cover, String title, String description,
                       String authorName, String authorAvatar, Integer likeCount,
                       Integer viewCount, Integer sourceWorkId, String sourceAuthorName,
                       Integer sourceAuthorId, Integer forkCount, String videoPath, String createTime) {
        this.workId = workId;
        this.authorId = authorId;
        this.cover = cover;
        this.title = title;
        this.description = description;
        this.authorName = authorName;
        this.authorAvatar = authorAvatar;
        this.likeCount = likeCount;
        this.viewCount = viewCount;
        this.sourceWorkId = sourceWorkId;
        this.sourceAuthorName = sourceAuthorName;
        this.sourceAuthorId = sourceAuthorId;
        this.forkCount = forkCount;
        this.videoPath = videoPath;
        this.createTime = createTime;
    }

    public Integer getWorkId() { return workId; }
    public void setWorkId(Integer workId) { this.workId = workId; }

    public Integer getAuthorId() { return authorId; }
    public void setAuthorId(Integer authorId) { this.authorId = authorId; }

    public String getCover() { return cover; }
    public void setCover(String cover) { this.cover = cover; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public String getDescription() { return description; }
    public void setDescription(String description) { this.description = description; }

    public String getAuthorName() { return authorName; }
    public void setAuthorName(String authorName) { this.authorName = authorName; }

    public String getAuthorAvatar() { return authorAvatar; }
    public void setAuthorAvatar(String authorAvatar) { this.authorAvatar = authorAvatar; }

    public Integer getLikeCount() { return likeCount; }
    public void setLikeCount(Integer likeCount) { this.likeCount = likeCount; }

    public Integer getViewCount() { return viewCount; }
    public void setViewCount(Integer viewCount) { this.viewCount = viewCount; }

    public Integer getSourceWorkId() { return sourceWorkId; }
    public void setSourceWorkId(Integer sourceWorkId) { this.sourceWorkId = sourceWorkId; }

    public String getSourceAuthorName() { return sourceAuthorName; }
    public void setSourceAuthorName(String sourceAuthorName) { this.sourceAuthorName = sourceAuthorName; }

    public Integer getSourceAuthorId() { return sourceAuthorId; }
    public void setSourceAuthorId(Integer sourceAuthorId) { this.sourceAuthorId = sourceAuthorId; }

    public Integer getForkCount() { return forkCount; }
    public void setForkCount(Integer forkCount) { this.forkCount = forkCount; }

    public String getVideoPath() { return videoPath; }
    public void setVideoPath(String videoPath) { this.videoPath = videoPath; }

    public String getCreateTime() { return createTime; }
    public void setCreateTime(String createTime) { this.createTime = createTime; }
}
