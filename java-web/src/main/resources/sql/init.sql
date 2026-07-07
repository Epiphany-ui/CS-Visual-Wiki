-- ============================================================
-- Manim 动画生成系统 - 数据库初始化脚本
-- 数据库：manim_ai
-- ============================================================

CREATE DATABASE IF NOT EXISTS `manim_ai`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `manim_ai`;

-- 任务表
CREATE TABLE IF NOT EXISTS `task` (
    `id`             BIGINT       NOT NULL AUTO_INCREMENT COMMENT '主键自增',
    `user_input`     VARCHAR(2000) NOT NULL               COMMENT '用户需求文本',
    `max_retry`      INT          NOT NULL DEFAULT 3      COMMENT '最大重试次数',
    `status`         INT          NOT NULL DEFAULT 0      COMMENT '任务状态：0-等待中，1-生成中，2-成功，3-失败',
    `generated_code` TEXT                                 COMMENT '生成的 Manim 代码',
    `video_url`      VARCHAR(500)                         COMMENT '视频访问路径',
    `try_count`      INT          NOT NULL DEFAULT 0      COMMENT '实际重试次数',
    `error_log`      TEXT                                 COMMENT '错误日志',
    `create_time`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    INDEX `idx_status` (`status`),
    INDEX `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='动画生成任务表';
