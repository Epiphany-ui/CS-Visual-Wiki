package com.manim.pojo;

import com.baomidou.mybatisplus.annotation.*;
import com.fasterxml.jackson.annotation.JsonIgnore;
import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.v3.oas.annotations.media.Schema;

import java.time.LocalDateTime;

/**
 * 系统登录用户实体
 * <p>
 * 对应 database.sql 中 user 表结构：
 * id, username, password, create_time
 * </p>
 */
@TableName("user")
@Schema(description = "系统登录用户")
public class User {

    @TableId(type = IdType.AUTO)
    @Schema(description = "用户 ID")
    private Integer id;

    @Schema(description = "登录账号（唯一不可重复）")
    private String username;

    @JsonIgnore
    @Schema(description = "登录密码（写入/校验用，响应不返回）")
    private String password;

    @TableField(fill = FieldFill.INSERT)
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss")
    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    // ===== getters & setters =====

    public Integer getId() {
        return id;
    }

    public void setId(Integer id) {
        this.id = id;
    }

    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public LocalDateTime getCreateTime() {
        return createTime;
    }

    public void setCreateTime(LocalDateTime createTime) {
        this.createTime = createTime;
    }
}
