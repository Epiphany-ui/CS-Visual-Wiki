-- ============================================================
-- Manim AI 智能动画生成系统 - 字段中文注释补充脚本
-- 说明：为每张表的每个非主键字段添加中文 COMMENT 注释
-- 使用方式：在已运行 database.sql 建表后，在 DataGrip 中直接运行此文件
-- 注意：ALTER TABLE MODIFY COLUMN 不改变数据类型/约束，只更新注释
-- ============================================================

USE manim_ai;

ALTER TABLE `user` MODIFY COLUMN `username` VARCHAR(50)  NOT NULL COMMENT '登录账号（唯一，不可重复）';
ALTER TABLE `user` MODIFY COLUMN `password` VARCHAR(100) NOT NULL COMMENT '登录密码（MD5 加密存储）';
ALTER TABLE `user` MODIFY COLUMN `nickname` VARCHAR(50)  DEFAULT NULL COMMENT '用户昵称（显示用，默认取 username）';
ALTER TABLE `user` MODIFY COLUMN `avatar` VARCHAR(500) DEFAULT NULL COMMENT '头像图片 URL';
ALTER TABLE `user` MODIFY COLUMN `intro` VARCHAR(200) DEFAULT NULL COMMENT '个人简介';
ALTER TABLE `user` MODIFY COLUMN `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间';

ALTER TABLE `task` MODIFY COLUMN `user_id` INT            NOT NULL COMMENT '所属用户 ID，关联 user 表';
ALTER TABLE `task` MODIFY COLUMN `user_input` VARCHAR(2000)  NOT NULL COMMENT '用户输入的动画需求文本';
ALTER TABLE `task` MODIFY COLUMN `status` TINYINT        NOT NULL DEFAULT 0 COMMENT '任务状态：0-处理中 1-成功 2-失败';
ALTER TABLE `task` MODIFY COLUMN `video_path` VARCHAR(1000)  DEFAULT NULL COMMENT '渲染成功的视频文件绝对路径';
ALTER TABLE `task` MODIFY COLUMN `error_log` TEXT           DEFAULT NULL COMMENT '渲染失败时的详细错误日志';
ALTER TABLE `task` MODIFY COLUMN `create_time` DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '任务创建时间';
ALTER TABLE `task` MODIFY COLUMN `update_time` DATETIME       NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '任务更新时间';

ALTER TABLE `knowledge_category` MODIFY COLUMN `name` VARCHAR(50)  NOT NULL COMMENT '分类名称（如：算法、数据结构、高等数学）';
ALTER TABLE `knowledge_category` MODIFY COLUMN `icon` VARCHAR(500) DEFAULT NULL COMMENT '分类图标 URL';
ALTER TABLE `knowledge_category` MODIFY COLUMN `description` VARCHAR(200) DEFAULT NULL COMMENT '分类描述';
ALTER TABLE `knowledge_category` MODIFY COLUMN `sort_order` INT          NOT NULL DEFAULT 0 COMMENT '排序权重（数值越小越靠前）';
ALTER TABLE `knowledge_category` MODIFY COLUMN `create_time` DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';

ALTER TABLE `knowledge_entry` MODIFY COLUMN `category_id` INT           NOT NULL COMMENT '所属分类 ID，关联 knowledge_category 表';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `title` VARCHAR(100)  NOT NULL COMMENT '词条标题';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `summary` VARCHAR(500)  DEFAULT NULL COMMENT '简短摘要，列表页展示用';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `definition` TEXT          DEFAULT NULL COMMENT '定义——标准五段式内容第一部分';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `principle` TEXT          DEFAULT NULL COMMENT '核心原理——标准五段式内容第二部分';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `example` TEXT          DEFAULT NULL COMMENT '过程示例——标准五段式内容第三部分';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `complexity` VARCHAR(200)  DEFAULT NULL COMMENT '复杂度/性能分析——标准五段式内容第四部分';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `misconception` TEXT          DEFAULT NULL COMMENT '常见误区——标准五段式内容第五部分';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `source` VARCHAR(200)  DEFAULT NULL COMMENT '来源/参考文献标注';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `difficulty` TINYINT       NOT NULL DEFAULT 1 COMMENT '难度分级：1-入门 2-中等 3-困难';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `view_count` INT           NOT NULL DEFAULT 0 COMMENT '浏览次数，用于热门排序';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';
ALTER TABLE `knowledge_entry` MODIFY COLUMN `update_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间';

ALTER TABLE `animation` MODIFY COLUMN `knowledge_id` INT           NOT NULL COMMENT '关联词条 ID，关联 knowledge_entry 表';
ALTER TABLE `animation` MODIFY COLUMN `title` VARCHAR(100)  NOT NULL COMMENT '动画标题';
ALTER TABLE `animation` MODIFY COLUMN `video_path` VARCHAR(1000) DEFAULT NULL COMMENT '视频文件路径';
ALTER TABLE `animation` MODIFY COLUMN `duration` INT           NOT NULL DEFAULT 0 COMMENT '视频时长（单位：秒）';
ALTER TABLE `animation` MODIFY COLUMN `play_count` INT           NOT NULL DEFAULT 0 COMMENT '播放次数统计';
ALTER TABLE `animation` MODIFY COLUMN `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';

ALTER TABLE `template` MODIFY COLUMN `name` VARCHAR(100)  NOT NULL COMMENT '模板名称';
ALTER TABLE `template` MODIFY COLUMN `description` VARCHAR(500)  DEFAULT NULL COMMENT '模板简介说明';
ALTER TABLE `template` MODIFY COLUMN `cover` VARCHAR(500)  DEFAULT NULL COMMENT '封面图片 URL';
ALTER TABLE `template` MODIFY COLUMN `category` VARCHAR(50)   DEFAULT NULL COMMENT '模板分类（排序/树/函数/概率等）';
ALTER TABLE `template` MODIFY COLUMN `config_schema` JSON          DEFAULT NULL COMMENT '参数配置 JSON Schema（字段名、类型、默认值、校验规则）';
ALTER TABLE `template` MODIFY COLUMN `preview_video` VARCHAR(500)  DEFAULT NULL COMMENT '预览视频路径';
ALTER TABLE `template` MODIFY COLUMN `default_code` TEXT          DEFAULT NULL COMMENT '默认 Manim 代码模板';
ALTER TABLE `template` MODIFY COLUMN `use_count` INT           NOT NULL DEFAULT 0 COMMENT '被使用次数';
ALTER TABLE `template` MODIFY COLUMN `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';
ALTER TABLE `template` MODIFY COLUMN `update_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间';

ALTER TABLE `work` MODIFY COLUMN `user_id` INT           NOT NULL COMMENT '作者 ID，关联 user 表';
ALTER TABLE `work` MODIFY COLUMN `title` VARCHAR(100)  NOT NULL COMMENT '作品标题';
ALTER TABLE `work` MODIFY COLUMN `description` VARCHAR(500)  DEFAULT NULL COMMENT '作品描述说明';
ALTER TABLE `work` MODIFY COLUMN `manim_code` TEXT          DEFAULT NULL COMMENT 'Manim 源码';
ALTER TABLE `work` MODIFY COLUMN `video_path` VARCHAR(1000) DEFAULT NULL COMMENT '视频文件路径';
ALTER TABLE `work` MODIFY COLUMN `cover` VARCHAR(500)  DEFAULT NULL COMMENT '封面图 URL';
ALTER TABLE `work` MODIFY COLUMN `tags` VARCHAR(500)  DEFAULT NULL COMMENT '标签列表（逗号分隔，如：算法,排序,可视化）';
ALTER TABLE `work` MODIFY COLUMN `is_public` TINYINT       NOT NULL DEFAULT 0 COMMENT '是否公开：0-私密（仅自己可见）1-公开（所有人可见）';
ALTER TABLE `work` MODIFY COLUMN `source_work_id` INT           DEFAULT NULL COMMENT 'Fork 来源作品 ID，用于溯源链';
ALTER TABLE `work` MODIFY COLUMN `view_count` INT           NOT NULL DEFAULT 0 COMMENT '播放/查看次数';
ALTER TABLE `work` MODIFY COLUMN `like_count` INT           NOT NULL DEFAULT 0 COMMENT '点赞数';
ALTER TABLE `work` MODIFY COLUMN `collect_count` INT           NOT NULL DEFAULT 0 COMMENT '收藏数';
ALTER TABLE `work` MODIFY COLUMN `fork_count` INT           NOT NULL DEFAULT 0 COMMENT '被 Fork 次数';
ALTER TABLE `work` MODIFY COLUMN `status` TINYINT       NOT NULL DEFAULT 1 COMMENT '作品状态：0-草稿 1-已发布';
ALTER TABLE `work` MODIFY COLUMN `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间';
ALTER TABLE `work` MODIFY COLUMN `update_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '最后更新时间';

ALTER TABLE `work_like` MODIFY COLUMN `work_id` INT      NOT NULL COMMENT '被点赞的作品 ID，关联 work 表';
ALTER TABLE `work_like` MODIFY COLUMN `user_id` INT      NOT NULL COMMENT '点赞用户 ID，关联 user 表';
ALTER TABLE `work_like` MODIFY COLUMN `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间';

ALTER TABLE `work_comment` MODIFY COLUMN `work_id` INT           NOT NULL COMMENT '所属作品 ID，关联 work 表';
ALTER TABLE `work_comment` MODIFY COLUMN `user_id` INT           NOT NULL COMMENT '评论用户 ID，关联 user 表';
ALTER TABLE `work_comment` MODIFY COLUMN `content` VARCHAR(2000) NOT NULL COMMENT '评论内容';
ALTER TABLE `work_comment` MODIFY COLUMN `reply_to_id` INT           DEFAULT NULL COMMENT '回复目标评论 ID，NULL 表示顶层评论，非 NULL 表示楼中楼回复';
ALTER TABLE `work_comment` MODIFY COLUMN `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '评论时间';

ALTER TABLE `user_collect` MODIFY COLUMN `user_id` INT      NOT NULL COMMENT '用户 ID，关联 user 表';
ALTER TABLE `user_collect` MODIFY COLUMN `target_type` TINYINT  NOT NULL COMMENT '收藏类型：1-知识词条 2-动画作品 3-创作模板';
ALTER TABLE `user_collect` MODIFY COLUMN `target_id` INT      NOT NULL COMMENT '被收藏的目标资源 ID';
ALTER TABLE `user_collect` MODIFY COLUMN `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '收藏时间';

ALTER TABLE `user_follow` MODIFY COLUMN `follower_id` INT      NOT NULL COMMENT '关注者 ID（主动关注的一方），关联 user 表';
ALTER TABLE `user_follow` MODIFY COLUMN `followee_id` INT      NOT NULL COMMENT '被关注者 ID（被关注的一方），关联 user 表';
ALTER TABLE `user_follow` MODIFY COLUMN `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '关注时间';

ALTER TABLE `study_record` MODIFY COLUMN `user_id` INT      NOT NULL COMMENT '用户 ID，关联 user 表';
ALTER TABLE `study_record` MODIFY COLUMN `knowledge_id` INT      DEFAULT NULL COMMENT '学习的知识点 ID，关联 knowledge_entry 表（可为空）';
ALTER TABLE `study_record` MODIFY COLUMN `study_duration` INT      NOT NULL DEFAULT 0 COMMENT '学习时长（单位：秒）';
ALTER TABLE `study_record` MODIFY COLUMN `checkin_date` DATE     NOT NULL COMMENT '打卡日期，用于按天聚合统计';
ALTER TABLE `study_record` MODIFY COLUMN `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间';

ALTER TABLE `browse_history` MODIFY COLUMN `user_id` INT      NOT NULL COMMENT '用户 ID，关联 user 表';
ALTER TABLE `browse_history` MODIFY COLUMN `target_type` TINYINT  NOT NULL COMMENT '浏览类型：1-知识词条 2-动画作品 3-创作模板';
ALTER TABLE `browse_history` MODIFY COLUMN `target_id` INT      NOT NULL COMMENT '被浏览的目标资源 ID';
ALTER TABLE `browse_history` MODIFY COLUMN `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '浏览时间';

ALTER TABLE `sandbox_draft` MODIFY COLUMN `user_id` INT           NOT NULL COMMENT '用户 ID，关联 user 表';
ALTER TABLE `sandbox_draft` MODIFY COLUMN `work_id` INT           DEFAULT NULL COMMENT '关联作品 ID（从作品 Fork 而来时非空），关联 work 表';
ALTER TABLE `sandbox_draft` MODIFY COLUMN `manim_code` TEXT          DEFAULT NULL COMMENT 'Manim 代码内容';
ALTER TABLE `sandbox_draft` MODIFY COLUMN `preview_url` VARCHAR(1000) DEFAULT NULL COMMENT '预览视频 URL';
ALTER TABLE `sandbox_draft` MODIFY COLUMN `version` INT           NOT NULL DEFAULT 1 COMMENT '版本号，每次保存自增';
ALTER TABLE `sandbox_draft` MODIFY COLUMN `note` VARCHAR(200)  DEFAULT NULL COMMENT '版本备注说明';
ALTER TABLE `sandbox_draft` MODIFY COLUMN `create_time` DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '草稿保存时间';

-- 脚本执行完毕