package com.manim.dto;

import com.fasterxml.jackson.annotation.JsonProperty;

/**
 * Python AI 服务 /generate 接口返回数据 DTO
 */
public class PythonResponse {

    /** 是否生成成功 */
    private boolean success;

    /** 生成的 Manim 代码 */
    private String code;

    /** 视频访问路径 */
    @JsonProperty("video_path")
    private String videoPath;

    /** 实际重试次数 */
    @JsonProperty("try_count")
    private int tryCount;

    /** 执行日志 / 错误信息 */
    private String log;

    // ===== getters & setters =====

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getVideoPath() {
        return videoPath;
    }

    public void setVideoPath(String videoPath) {
        this.videoPath = videoPath;
    }

    public int getTryCount() {
        return tryCount;
    }

    public void setTryCount(int tryCount) {
        this.tryCount = tryCount;
    }

    public String getLog() {
        return log;
    }

    public void setLog(String log) {
        this.log = log;
    }
}
