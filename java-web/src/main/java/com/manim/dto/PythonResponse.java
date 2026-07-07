package com.manim.dto;

import com.fasterxml.jackson.annotation.JsonProperty;
import io.swagger.v3.oas.annotations.media.Schema;

/**
 * Python AI 服务 /generate 接口返回数据 DTO
 */
@Schema(description = "Python AI 服务响应结果")
public class PythonResponse {

    @Schema(description = "是否生成成功")
    private boolean success;

    @Schema(description = "生成的 Manim 代码")
    private String code;

    @JsonProperty("video_path")
    @Schema(description = "视频文件路径")
    private String videoPath;

    @JsonProperty("try_count")
    @Schema(description = "实际重试次数")
    private int tryCount;

    @Schema(description = "执行日志 / 错误信息")
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
