USE `manim_ai`;

DROP TABLE IF EXISTS `knowledge_category`;
CREATE TABLE `knowledge_category` (
    `id`          INT          NOT NULL AUTO_INCREMENT COMMENT '分类ID',
    `name`        VARCHAR(50)  NOT NULL                COMMENT '分类名称（如：算法、数据结构）',
    `icon`        VARCHAR(500) DEFAULT NULL            COMMENT '分类图标URL',
    `description` VARCHAR(200) DEFAULT NULL            COMMENT '分类描述',
    `sort_order`  INT          NOT NULL DEFAULT 0      COMMENT '排序权重（越小越靠前）',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='百科知识分类表';

-- ============================================================
-- 4. 知识词条表：百科详情核心内容
-- 对应接口：4.1 ~ 4.5（knowledge.*）
-- 设计原因：百科详情页的核心数据——标准五段式内容结构
-- （定义→原理→示例→复杂度→误区），关联分类，支持难度分级。
-- ============================================================
DROP TABLE IF EXISTS `knowledge_entry`;
CREATE TABLE `knowledge_entry` (
    `id`            INT           NOT NULL AUTO_INCREMENT COMMENT '词条ID',
    `category_id`   INT           NOT NULL                COMMENT '所属分类ID',
    `title`         VARCHAR(100)  NOT NULL                COMMENT '词条标题',
    `summary`       VARCHAR(500)  DEFAULT NULL            COMMENT '简短摘要',
    `definition`    TEXT          DEFAULT NULL            COMMENT '定义',
    `principle`     TEXT          DEFAULT NULL            COMMENT '核心原理',
    `example`       TEXT          DEFAULT NULL            COMMENT '过程示例',
    `complexity`    VARCHAR(200)  DEFAULT NULL            COMMENT '复杂度分析',
    `misconception` TEXT          DEFAULT NULL            COMMENT '常见误区',
    `source`        VARCHAR(200)  DEFAULT NULL            COMMENT '来源/参考文献',
    `difficulty`    TINYINT       NOT NULL DEFAULT 1      COMMENT '难度：1-入门 2-中等 3-困难',
    `view_count`    INT           NOT NULL DEFAULT 0      COMMENT '浏览次数',
    `create_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_category` (`category_id`),
    KEY `idx_difficulty` (`difficulty`),
    KEY `idx_view_count` (`view_count`),
    CONSTRAINT `fk_entry_category` FOREIGN KEY (`category_id`) REFERENCES `knowledge_category` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='百科知识词条表';

-- ============================================================
-- 5. 动画资源表：词条绑定的演示动画
-- 对应接口：4.3（knowledge.animation.list）
-- 设计原因：每个知识词条可绑定 N 个演示动画，
-- 独立存储便于播放统计和后续扩展。
-- ============================================================
DROP TABLE IF EXISTS `animation`;
CREATE TABLE `animation` (
    `id`            INT           NOT NULL AUTO_INCREMENT COMMENT '动画ID',
    `knowledge_id`  INT           NOT NULL                COMMENT '关联词条ID',
    `title`         VARCHAR(100)  NOT NULL                COMMENT '动画标题',
    `video_path`    VARCHAR(1000) DEFAULT NULL            COMMENT '视频文件路径',
    `duration`      INT           NOT NULL DEFAULT 0      COMMENT '时长（秒）',
    `play_count`    INT           NOT NULL DEFAULT 0      COMMENT '播放次数',
    `create_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_knowledge` (`knowledge_id`),
    CONSTRAINT `fk_animation_knowledge` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_entry` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='动画资源表';

-- ============================================================
-- 6. 创作模板表：零代码模板
-- 对应接口：5.1 ~ 5.3（template.*）
-- 设计原因：模板是零代码创作的核心——config_schema 存 JSON
-- 描述参数表单结构（字段名、类型、默认值、校验规则），
-- use_count 记录使用热度。首批官方模板包含排序算法可视化、
-- 函数图像绘制、二叉树遍历、正态分布、傅里叶级数。
-- ============================================================
DROP TABLE IF EXISTS `template`;
CREATE TABLE `template` (
    `id`            INT           NOT NULL AUTO_INCREMENT COMMENT '模板ID',
    `name`          VARCHAR(100)  NOT NULL                COMMENT '模板名称',
    `description`   VARCHAR(500)  DEFAULT NULL            COMMENT '模板简介',
    `cover`         VARCHAR(500)  DEFAULT NULL            COMMENT '封面图片URL',
    `category`      VARCHAR(50)   DEFAULT NULL            COMMENT '模板分类（排序/树/函数/概率）',
    `config_schema` JSON         DEFAULT NULL            COMMENT '参数配置JSON Schema',
    `preview_video` VARCHAR(500)  DEFAULT NULL            COMMENT '预览视频路径',
    `default_code`  TEXT         DEFAULT NULL            COMMENT '默认Manim代码模板',
    `use_count`     INT           NOT NULL DEFAULT 0      COMMENT '使用次数',
    `create_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_category` (`category`),
    KEY `idx_use_count` (`use_count`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='创作模板表';

-- ============================================================
-- 7. 作品表：用户发布的动画作品（成品）
-- 对应接口：5.5 / 6.6 / 7.1 ~ 7.7（work.* / gallery.*）
-- 设计原因：社区画廊的核心实体。
-- source_work_id 实现 Fork 溯源链（类似 GitHub）；
-- like/fork/collect/view_count 做排行榜和热度排序；
-- is_public 控制私密/公开。
-- ============================================================
DROP TABLE IF EXISTS `work`;
CREATE TABLE `work` (
    `id`              INT           NOT NULL AUTO_INCREMENT COMMENT '作品ID',
    `user_id`         INT           NOT NULL                COMMENT '作者ID',
    `title`           VARCHAR(100)  NOT NULL                COMMENT '作品标题',
    `description`     VARCHAR(500)  DEFAULT NULL            COMMENT '作品描述',
    `manim_code`      TEXT          DEFAULT NULL            COMMENT 'Manim源码',
    `video_path`      VARCHAR(1000) DEFAULT NULL            COMMENT '视频文件路径',
    `cover`           VARCHAR(500)  DEFAULT NULL            COMMENT '封面图URL',
    `tags`            VARCHAR(500)  DEFAULT NULL            COMMENT '标签列表（逗号分隔）',
    `is_public`       TINYINT       NOT NULL DEFAULT 0      COMMENT '是否公开：0-私密 1-公开',
    `source_work_id`  INT           DEFAULT NULL            COMMENT 'Fork来源作品ID（溯源）',
    `view_count`      INT           NOT NULL DEFAULT 0      COMMENT '播放/查看次数',
    `like_count`      INT           NOT NULL DEFAULT 0      COMMENT '点赞数',
    `collect_count`   INT           NOT NULL DEFAULT 0      COMMENT '收藏数',
    `fork_count`      INT           NOT NULL DEFAULT 0      COMMENT 'Fork次数',
    `status`          TINYINT       NOT NULL DEFAULT 1      COMMENT '状态：0-草稿 1-已发布',
    `create_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time`     DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_public` (`is_public`, `status`),
    KEY `idx_view_count` (`view_count`),
    KEY `idx_like_count` (`like_count`),
    KEY `idx_source` (`source_work_id`),
    CONSTRAINT `fk_work_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_work_source` FOREIGN KEY (`source_work_id`) REFERENCES `work` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='动画作品表';

-- ============================================================
-- 8. 作品点赞表
-- 对应接口：7.3（work.like）
-- 设计原因：点赞是高频操作，独立表存储避免 work 表行锁，
-- 同时支持"我赞过的"功能。联合唯一约束防止重复点赞。
-- ============================================================
DROP TABLE IF EXISTS `work_like`;
CREATE TABLE `work_like` (
    `id`          INT      NOT NULL AUTO_INCREMENT COMMENT '主键',
    `work_id`     INT      NOT NULL                COMMENT '作品ID',
    `user_id`     INT      NOT NULL                COMMENT '点赞用户ID',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_work_user` (`work_id`, `user_id`),
    KEY `idx_user` (`user_id`),
    CONSTRAINT `fk_like_work` FOREIGN KEY (`work_id`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_like_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品点赞表';

-- ============================================================
-- 9. 作品评论表（支持楼中楼回复）
-- 对应接口：7.5（work.comment）
-- 设计原因：reply_to_id 实现"楼中楼"回复结构，
-- 无需递归查询，前端按 parentId 做树形渲染。
-- ============================================================
DROP TABLE IF EXISTS `work_comment`;
CREATE TABLE `work_comment` (
    `id`          INT           NOT NULL AUTO_INCREMENT COMMENT '评论ID',
    `work_id`     INT           NOT NULL                COMMENT '所属作品ID',
    `user_id`     INT           NOT NULL                COMMENT '评论用户ID',
    `content`     VARCHAR(2000) NOT NULL                COMMENT '评论内容',
    `reply_to_id` INT           DEFAULT NULL            COMMENT '回复目标评论ID（楼中楼）',
    `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_work` (`work_id`),
    KEY `idx_user` (`user_id`),
    CONSTRAINT `fk_comment_work` FOREIGN KEY (`work_id`) REFERENCES `work` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_comment_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='作品评论表';

-- ============================================================
-- 10. 用户收藏表（多态设计：可收藏词条/作品/模板）
-- 对应接口：4.5 / 7.4 / 8.3（knowledge.collect / work.collect / user.collect）
-- 设计原因：target_type + target_id 多态设计，
-- 一张表统一管理对"词条/作品/模板"三类资源的收藏，
-- 避免为每种资源建独立的收藏表。
-- ============================================================
DROP TABLE IF EXISTS `user_collect`;
CREATE TABLE `user_collect` (
    `id`          INT          NOT NULL AUTO_INCREMENT COMMENT '主键',
    `user_id`     INT          NOT NULL                COMMENT '用户ID',
    `target_type` TINYINT      NOT NULL                COMMENT '收藏类型：1-词条 2-作品 3-模板',
    `target_id`   INT          NOT NULL                COMMENT '目标资源ID',
    `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_user_target` (`user_id`, `target_type`, `target_id`),
    KEY `idx_target` (`target_type`, `target_id`),
    CONSTRAINT `fk_collect_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户收藏表（多态）';

-- ============================================================
-- 11. 用户关注关系表
-- 对应接口：7.8（user.follow）
-- 设计原因：关注/粉丝关系是完全对称的关联关系，
-- follower_id→followee_id 单向，查询粉丝时反向联表。
-- 联合唯一约束防止重复关注。
-- ============================================================
DROP TABLE IF EXISTS `user_follow`;
CREATE TABLE `user_follow` (
    `id`          INT      NOT NULL AUTO_INCREMENT COMMENT '主键',
    `follower_id` INT      NOT NULL                COMMENT '关注者ID',
    `followee_id` INT      NOT NULL                COMMENT '被关注者ID',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_follow` (`follower_id`, `followee_id`),
    KEY `idx_follower` (`follower_id`),
    KEY `idx_followee` (`followee_id`),
    CONSTRAINT `fk_follow_follower` FOREIGN KEY (`follower_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_follow_followee` FOREIGN KEY (`followee_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户关注关系表';

-- ============================================================
-- 12. 学习打卡记录表
-- 对应接口：4.6（study.checkin）
-- 设计原因：记录用户每次学习知识点后的打卡行为，
-- 累计 learning_days 和 study_minutes 做学习统计。
-- 每次打卡独立记录，支持按日期聚合统计。
-- ============================================================
DROP TABLE IF EXISTS `study_record`;
CREATE TABLE `study_record` (
    `id`             INT      NOT NULL AUTO_INCREMENT COMMENT '主键',
    `user_id`        INT      NOT NULL                COMMENT '用户ID',
    `knowledge_id`   INT      DEFAULT NULL            COMMENT '学习知识点ID（可为空）',
    `study_duration` INT      NOT NULL DEFAULT 0      COMMENT '学习时长（秒）',
    `checkin_date`   DATE     NOT NULL                COMMENT '打卡日期',
    `create_time`    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_date` (`user_id`, `checkin_date`),
    KEY `idx_knowledge` (`knowledge_id`),
    CONSTRAINT `fk_study_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_study_knowledge` FOREIGN KEY (`knowledge_id`) REFERENCES `knowledge_entry` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='学习打卡记录表';

-- ============================================================
-- 13. 浏览历史表
-- 对应接口：8.4（user.history.list）
-- 设计原因：记录用户浏览过的词条/作品/模板，
-- 按时间倒序展示"最近浏览"，每次浏览 insert 一条，
-- 查询时 GROUP BY target + MAX(create_time) 去重。
-- ============================================================
DROP TABLE IF EXISTS `browse_history`;
CREATE TABLE `browse_history` (
    `id`          INT      NOT NULL AUTO_INCREMENT COMMENT '主键',
    `user_id`     INT      NOT NULL                COMMENT '用户ID',
    `target_type` TINYINT  NOT NULL                COMMENT '浏览类型：1-词条 2-作品 3-模板',
    `target_id`   INT      NOT NULL                COMMENT '目标资源ID',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user_time` (`user_id`, `create_time` DESC),
    KEY `idx_target` (`target_type`, `target_id`),
    CONSTRAINT `fk_history_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='浏览历史表';

-- ============================================================
-- 14. 沙箱草稿表（含版本历史）
-- 对应接口：6.4 / 6.5（sandbox.version.list / sandbox.draft.save）
-- 设计原因：沙箱创作需要自动保存+版本回退，
-- 每保存一次写入一条记录，version 递增标识版本号，
-- work_id 非空表示此草稿已关联到某作品（从作品Fork而来）。
-- ============================================================
DROP TABLE IF EXISTS `sandbox_draft`;
CREATE TABLE `sandbox_draft` (
    `id`           INT           NOT NULL AUTO_INCREMENT COMMENT '草稿ID',
    `user_id`      INT           NOT NULL                COMMENT '用户ID',
    `work_id`      INT           DEFAULT NULL            COMMENT '关联作品ID（Fork来源）',
    `manim_code`   TEXT          DEFAULT NULL            COMMENT 'Manim代码',
    `preview_url`  VARCHAR(1000) DEFAULT NULL            COMMENT '预览视频URL',
    `version`      INT           NOT NULL DEFAULT 1      COMMENT '版本号',
    `note`         VARCHAR(200)  DEFAULT NULL            COMMENT '版本备注',
    `create_time`  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_user` (`user_id`),
    KEY `idx_work` (`work_id`),
    KEY `idx_user_time` (`user_id`, `create_time` DESC),
    CONSTRAINT `fk_draft_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_draft_work` FOREIGN KEY (`work_id`) REFERENCES `work` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='沙箱创作草稿表（含版本历史）';
