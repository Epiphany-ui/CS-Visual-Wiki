package com.manim.dto;

import io.swagger.v3.oas.annotations.media.Schema;

/**
 * 搜索结果 - 用户
 */
@Schema(description = "搜索结果-用户")
public class UserSearchDTO {

    @Schema(description = "用户 ID")
    private Integer userId;

    @Schema(description = "登录账号")
    private String username;

    @Schema(description = "用户昵称")
    private String nickname;

    @Schema(description = "头像 URL")
    private String avatar;

    public UserSearchDTO() {}

    public UserSearchDTO(Integer userId, String username, String nickname, String avatar) {
        this.userId = userId;
        this.username = username;
        this.nickname = nickname;
        this.avatar = avatar;
    }

    public Integer getUserId() { return userId; }
    public void setUserId(Integer userId) { this.userId = userId; }

    public String getUsername() { return username; }
    public void setUsername(String username) { this.username = username; }

    public String getNickname() { return nickname; }
    public void setNickname(String nickname) { this.nickname = nickname; }

    public String getAvatar() { return avatar; }
    public void setAvatar(String avatar) { this.avatar = avatar; }
}
