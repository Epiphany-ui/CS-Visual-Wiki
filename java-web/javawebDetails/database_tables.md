# Manim AI 系统 — 数据库表文档

> 数据库：`manim_ai` · 字符集：`utf8mb4` · 排序规则：`utf8mb4_unicode_ci`  
> 共 14 张表，覆盖 8 大业务模块

---

## 1. `user` — 系统登录用户表

**设计原因**：用户系统是所有业务的基础。`username` 唯一约束保证账号不重复，密码存 MD5 密文，`nickname` 作为显示昵称。

### 字段清单

| 列名          | 类型           | 约束                                  | 说明                     |
|:----------- |:------------:|:----------------------------------- |:---------------------- |
| id          | INT          | PK, AUTO_INCREMENT                  | 用户 ID                  |
| username    | VARCHAR(50)  | NOT NULL, UNIQUE                    | 登录账号（唯一，不可重复）          |
| password    | VARCHAR(100) | NOT NULL                            | 登录密码（MD5 加密存储）         |
| nickname    | VARCHAR(50)  | DEFAULT NULL                        | 用户昵称（显示用，默认取 username） |
| avatar      | VARCHAR(500) | DEFAULT NULL                        | 头像图片 URL               |
| intro       | VARCHAR(200) | DEFAULT NULL                        | 个人简介                   |
| create_time | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 注册时间                   |

### 索引

| 名称          | 类型         | 字段       |
|:----------- |:----------:|:-------- |
| uk_username | UNIQUE KEY | username |

### 外键关系

本表无外键，但被以下表引用：`task`、`work`、`work_like`、`work_comment`、`user_collect`、`user_follow`、`study_record`、`browse_history`、`sandbox_draft`

### 覆盖接口

用户注册/登录/信息查询/资料编辑

---

## 2. `task` — 动画生成任务表

**设计原因**：追踪每次 AI 渲染请求，支撑异步任务状态轮询。`user_id` 外键关联用户，`status` 用 TINYINT 表示处理中/成功/失败。

### 字段清单

| 列名          | 类型            | 约束                                            | 说明                   |
|:----------- |:-------------:|:--------------------------------------------- |:-------------------- |
| id          | INT           | PK, AUTO_INCREMENT                            | 任务主键 ID              |
| user_id     | INT           | NOT NULL, FK → user(id)                       | 所属用户 ID              |
| user_input  | VARCHAR(2000) | NOT NULL                                      | 用户输入的动画需求文本          |
| status      | TINYINT       | NOT NULL, DEFAULT 0                           | 任务状态：0-处理中 1-成功 2-失败 |
| video_path  | VARCHAR(1000) | DEFAULT NULL                                  | 渲染成功的视频文件绝对路径        |
| error_log   | TEXT          | DEFAULT NULL                                  | 渲染失败时的详细错误日志         |
| create_time | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | 任务创建时间               |
| update_time | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE | 任务更新时间               |

### 索引

| 名称              | 类型  | 字段          |
|:--------------- |:---:|:----------- |
| idx_user_id     | KEY | user_id     |
| idx_status      | KEY | status      |
| idx_create_time | KEY | create_time |

### 外键关系

| 约束名          | 字段      | 引用表                        |
|:------------ |:------- |:-------------------------- |
| fk_task_user | user_id | user(id) ON DELETE CASCADE |

### 覆盖接口

`POST /template/generate` · `GET /render/status`

---

## 3. `knowledge_category` — 百科知识分类表

**设计原因**：首页分类导航 + 百科分类列表页的数据基础。`sort_order` 控制显示顺序，`icon` 存分类图标。

### 字段清单

| 列名          | 类型           | 约束                                  | 说明                   |
|:----------- |:------------:|:----------------------------------- |:-------------------- |
| id          | INT          | PK, AUTO_INCREMENT                  | 分类 ID                |
| name        | VARCHAR(50)  | NOT NULL                            | 分类名称（如：算法、数据结构、高等数学） |
| icon        | VARCHAR(500) | DEFAULT NULL                        | 分类图标 URL             |
| description | VARCHAR(200) | DEFAULT NULL                        | 分类描述                 |
| sort_order  | INT          | NOT NULL, DEFAULT 0                 | 排序权重（数值越小越靠前）        |
| create_time | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间                 |

### 外键关系

被 `knowledge_entry.category_id` 引用。

### 覆盖接口

`GET /home/category` · `GET /knowledge/category/list`

---

## 4. `knowledge_entry` — 百科知识词条表

**设计原因**：百科详情页的核心数据——标准五段式内容结构（定义→原理→示例→复杂度→误区）。`difficulty` 支持三级难度过滤，`view_count` 用于热门排序。

### 字段清单

| 列名            | 类型           | 约束                                            | 说明                    |
|:------------- |:------------:|:--------------------------------------------- |:--------------------- |
| id            | INT          | PK, AUTO_INCREMENT                            | 词条 ID                 |
| category_id   | INT          | NOT NULL, FK → knowledge_category(id)         | 所属分类 ID               |
| title         | VARCHAR(100) | NOT NULL                                      | 词条标题                  |
| summary       | VARCHAR(500) | DEFAULT NULL                                  | 简短摘要，列表页展示用           |
| definition    | TEXT         | DEFAULT NULL                                  | 定义——标准五段式内容第一部分       |
| principle     | TEXT         | DEFAULT NULL                                  | 核心原理——标准五段式内容第二部分     |
| example       | TEXT         | DEFAULT NULL                                  | 过程示例——标准五段式内容第三部分     |
| complexity    | VARCHAR(200) | DEFAULT NULL                                  | 复杂度/性能分析——标准五段式内容第四部分 |
| misconception | TEXT         | DEFAULT NULL                                  | 常见误区——标准五段式内容第五部分     |
| source        | VARCHAR(200) | DEFAULT NULL                                  | 来源/参考文献标注             |
| difficulty    | TINYINT      | NOT NULL, DEFAULT 1                           | 难度分级：1-入门 2-中等 3-困难   |
| view_count    | INT          | NOT NULL, DEFAULT 0                           | 浏览次数，用于热门排序           |
| create_time   | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | 创建时间                  |
| update_time   | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE | 最后更新时间                |

### 索引

| 名称             | 类型  | 字段          |
|:-------------- |:---:|:----------- |
| idx_category   | KEY | category_id |
| idx_difficulty | KEY | difficulty  |
| idx_view_count | KEY | view_count  |

### 外键关系

| 约束名               | 字段          | 引用表                                      |
|:----------------- |:----------- |:---------------------------------------- |
| fk_entry_category | category_id | knowledge_category(id) ON DELETE CASCADE |

同时被 `animation.knowledge_id` 和 `study_record.knowledge_id` 引用。

### 覆盖接口

`GET /knowledge/detail` · `GET /knowledge/recommend` · `GET /knowledge/category/list`

---

## 5. `animation` — 动画资源表

**设计原因**：每个知识词条可绑定 N 个演示动画，独立存储便于播放统计和后续扩展。

### 字段清单

| 列名           | 类型            | 约束                                  | 说明         |
|:------------ |:-------------:|:----------------------------------- |:---------- |
| id           | INT           | PK, AUTO_INCREMENT                  | 动画 ID      |
| knowledge_id | INT           | NOT NULL, FK → knowledge_entry(id)  | 关联词条 ID    |
| title        | VARCHAR(100)  | NOT NULL                            | 动画标题       |
| video_path   | VARCHAR(1000) | DEFAULT NULL                        | 视频文件路径     |
| duration     | INT           | NOT NULL, DEFAULT 0                 | 视频时长（单位：秒） |
| play_count   | INT           | NOT NULL, DEFAULT 0                 | 播放次数统计     |
| create_time  | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 创建时间       |

### 索引

| 名称            | 类型  | 字段           |
|:------------- |:---:|:------------ |
| idx_knowledge | KEY | knowledge_id |

### 外键关系

| 约束名                    | 字段           | 引用表                                   |
|:---------------------- |:------------ |:------------------------------------- |
| fk_animation_knowledge | knowledge_id | knowledge_entry(id) ON DELETE CASCADE |

### 覆盖接口

`GET /knowledge/animation/list`

---

## 6. `template` — 创作模板表

**设计原因**：零代码创作的核心。`config_schema` 存 JSON 描述参数表单结构（字段名、类型、默认值、校验规则）。首批官方模板包含排序算法可视化、函数图像绘制、二叉树遍历、正态分布、傅里叶级数。

### 字段清单

| 列名            | 类型           | 约束                                            | 说明                |
|:------------- |:------------:|:--------------------------------------------- |:----------------- |
| id            | INT          | PK, AUTO_INCREMENT                            | 模板 ID             |
| name          | VARCHAR(100) | NOT NULL                                      | 模板名称              |
| description   | VARCHAR(500) | DEFAULT NULL                                  | 模板简介说明            |
| cover         | VARCHAR(500) | DEFAULT NULL                                  | 封面图片 URL          |
| category      | VARCHAR(50)  | DEFAULT NULL                                  | 模板分类（排序/树/函数/概率等） |
| config_schema | JSON         | DEFAULT NULL                                  | 参数配置 JSON Schema  |
| preview_video | VARCHAR(500) | DEFAULT NULL                                  | 预览视频路径            |
| default_code  | TEXT         | DEFAULT NULL                                  | 默认 Manim 代码模板     |
| use_count     | INT          | NOT NULL, DEFAULT 0                           | 被使用次数             |
| create_time   | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | 创建时间              |
| update_time   | DATETIME     | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE | 最后更新时间            |

### 索引

| 名称            | 类型  | 字段        |
|:------------- |:---:|:--------- |
| idx_category  | KEY | category  |
| idx_use_count | KEY | use_count |

### 覆盖接口

`GET /template/list` · `GET /template/detail`

---

## 7. `work` — 动画作品表（成品）

**设计原因**：社区画廊的核心实体。`source_work_id` 实现 Fork 溯源链（类似 GitHub）；`like/collect/fork/view_count` 做排行榜和热度排序；`is_public` 控制私密/公开。

### 字段清单

| 列名             | 类型            | 约束                                            | 说明               |
|:-------------- |:-------------:|:--------------------------------------------- |:---------------- |
| id             | INT           | PK, AUTO_INCREMENT                            | 作品 ID            |
| user_id        | INT           | NOT NULL, FK → user(id)                       | 作者 ID            |
| title          | VARCHAR(100)  | NOT NULL                                      | 作品标题             |
| description    | VARCHAR(500)  | DEFAULT NULL                                  | 作品描述说明           |
| manim_code     | TEXT          | DEFAULT NULL                                  | Manim 源码         |
| video_path     | VARCHAR(1000) | DEFAULT NULL                                  | 视频文件路径           |
| cover          | VARCHAR(500)  | DEFAULT NULL                                  | 封面图 URL          |
| tags           | VARCHAR(500)  | DEFAULT NULL                                  | 标签列表（逗号分隔）       |
| is_public      | TINYINT       | NOT NULL, DEFAULT 0                           | 是否公开：0-私密 1-公开   |
| source_work_id | INT           | DEFAULT NULL, FK → work(id)                   | Fork 来源作品 ID（溯源） |
| view_count     | INT           | NOT NULL, DEFAULT 0                           | 播放/查看次数          |
| like_count     | INT           | NOT NULL, DEFAULT 0                           | 点赞数              |
| collect_count  | INT           | NOT NULL, DEFAULT 0                           | 收藏数              |
| fork_count     | INT           | NOT NULL, DEFAULT 0                           | 被 Fork 次数        |
| status         | TINYINT       | NOT NULL, DEFAULT 1                           | 作品状态：0-草稿 1-已发布  |
| create_time    | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP           | 创建时间             |
| update_time    | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP ON UPDATE | 最后更新时间           |

### 索引

| 名称             | 类型  | 字段                |
|:-------------- |:---:|:----------------- |
| idx_user       | KEY | user_id           |
| idx_public     | KEY | is_public, status |
| idx_view_count | KEY | view_count        |
| idx_like_count | KEY | like_count        |
| idx_source     | KEY | source_work_id    |

### 外键关系

| 约束名            | 字段             | 引用表                         |
|:-------------- |:-------------- |:--------------------------- |
| fk_work_user   | user_id        | user(id) ON DELETE CASCADE  |
| fk_work_source | source_work_id | work(id) ON DELETE SET NULL |

同时被 `work_like`、`work_comment`、`sandbox_draft` 引用。

### 覆盖接口

`GET /gallery/list` · `GET /work/public/detail` · `POST /work/fork` · `GET /home/work/list` · `GET /home/carousel`

---

## 8. `work_like` — 作品点赞表

**设计原因**：独立表存储点赞避免 work 表行锁竞争，`(work_id, user_id)` 联合唯一约束防止重复点赞。

### 字段清单

| 列名          | 类型       | 约束                                  | 说明        |
|:----------- |:--------:|:----------------------------------- |:--------- |
| id          | INT      | PK, AUTO_INCREMENT                  | 主键        |
| work_id     | INT      | NOT NULL, FK → work(id)             | 被点赞的作品 ID |
| user_id     | INT      | NOT NULL, FK → user(id)             | 点赞用户 ID   |
| create_time | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 点赞时间      |

### 索引

| 名称           | 类型         | 字段               |
|:------------ |:----------:|:---------------- |
| uk_work_user | UNIQUE KEY | work_id, user_id |
| idx_user     | KEY        | user_id          |

### 外键关系

| 约束名          | 字段      | 引用表                        |
|:------------ |:------- |:-------------------------- |
| fk_like_work | work_id | work(id) ON DELETE CASCADE |
| fk_like_user | user_id | user(id) ON DELETE CASCADE |

### 覆盖接口

`POST /work/like`

---

## 9. `work_comment` — 作品评论表

**设计原因**：`reply_to_id` 指向父评论 ID 实现楼中楼回复结构，NULL 表示顶层评论，非 NULL 表示回复某条评论。

### 字段清单

| 列名          | 类型            | 约束                                  | 说明             |
|:----------- |:-------------:|:----------------------------------- |:-------------- |
| id          | INT           | PK, AUTO_INCREMENT                  | 评论 ID          |
| work_id     | INT           | NOT NULL, FK → work(id)             | 所属作品 ID        |
| user_id     | INT           | NOT NULL, FK → user(id)             | 评论用户 ID        |
| content     | VARCHAR(2000) | NOT NULL                            | 评论内容           |
| reply_to_id | INT           | DEFAULT NULL                        | 回复目标评论 ID（楼中楼） |
| create_time | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 评论时间           |

### 索引

| 名称       | 类型  | 字段      |
|:-------- |:---:|:------- |
| idx_work | KEY | work_id |
| idx_user | KEY | user_id |

### 外键关系

| 约束名             | 字段      | 引用表                        |
|:--------------- |:------- |:-------------------------- |
| fk_comment_work | work_id | work(id) ON DELETE CASCADE |
| fk_comment_user | user_id | user(id) ON DELETE CASCADE |

### 覆盖接口

`GET /work/comment/list` · `POST /work/comment/add`

---

## 10. `user_collect` — 用户收藏表（多态）

**设计原因**：`target_type` + `target_id` 多态设计，一张表统一管理对"知识词条/动画作品/创作模板"三类资源的收藏，`(user_id, target_type, target_id)` 联合唯一防止重复收藏。

### 字段清单

| 列名          | 类型       | 约束                                  | 说明                        |
|:----------- |:--------:|:----------------------------------- |:------------------------- |
| id          | INT      | PK, AUTO_INCREMENT                  | 主键                        |
| user_id     | INT      | NOT NULL, FK → user(id)             | 用户 ID                     |
| target_type | TINYINT  | NOT NULL                            | 收藏类型：1-知识词条 2-动画作品 3-创作模板 |
| target_id   | INT      | NOT NULL                            | 被收藏的目标资源 ID               |
| create_time | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 收藏时间                      |

### 索引

| 名称             | 类型         | 字段                              |
|:-------------- |:----------:|:------------------------------- |
| uk_user_target | UNIQUE KEY | user_id, target_type, target_id |
| idx_target     | KEY        | target_type, target_id          |

### 外键关系

| 约束名             | 字段      | 引用表                        |
|:--------------- |:------- |:-------------------------- |
| fk_collect_user | user_id | user(id) ON DELETE CASCADE |

### 覆盖接口

`POST /knowledge/collect` · `POST /work/collect` · `GET /user/collect/list`

---

## 11. `user_follow` — 用户关注关系表

**设计原因**：关注/粉丝是完全对称的关联关系，`follower_id`→`followee_id` 单向，查询粉丝时反向联表。联合唯一约束防止重复关注。

### 字段清单

| 列名          | 类型       | 约束                                  | 说明              |
|:----------- |:--------:|:----------------------------------- |:--------------- |
| id          | INT      | PK, AUTO_INCREMENT                  | 主键              |
| follower_id | INT      | NOT NULL, FK → user(id)             | 关注者 ID（主动关注的一方） |
| followee_id | INT      | NOT NULL, FK → user(id)             | 被关注者 ID（被关注的一方） |
| create_time | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 关注时间            |

### 索引

| 名称           | 类型         | 字段                       |
|:------------ |:----------:|:------------------------ |
| uk_follow    | UNIQUE KEY | follower_id, followee_id |
| idx_follower | KEY        | follower_id              |
| idx_followee | KEY        | followee_id              |

### 外键关系

| 约束名                | 字段          | 引用表                        |
|:------------------ |:----------- |:-------------------------- |
| fk_follow_follower | follower_id | user(id) ON DELETE CASCADE |
| fk_follow_followee | followee_id | user(id) ON DELETE CASCADE |

### 覆盖接口

`POST /user/follow`

---

## 12. `study_record` — 学习打卡记录表

**设计原因**：记录用户每次学习知识点后的打卡行为，`study_duration` 存学习时长（秒），`checkin_date` 存打卡日期用于按天聚合统计。

### 字段清单

| 列名             | 类型       | 约束                                     | 说明             |
|:-------------- |:--------:|:-------------------------------------- |:-------------- |
| id             | INT      | PK, AUTO_INCREMENT                     | 主键             |
| user_id        | INT      | NOT NULL, FK → user(id)                | 用户 ID          |
| knowledge_id   | INT      | DEFAULT NULL, FK → knowledge_entry(id) | 学习的知识点 ID（可为空） |
| study_duration | INT      | NOT NULL, DEFAULT 0                    | 学习时长（单位：秒）     |
| checkin_date   | DATE     | NOT NULL                               | 打卡日期，用于按天聚合统计  |
| create_time    | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP    | 记录创建时间         |

### 索引

| 名称            | 类型  | 字段                    |
|:------------- |:---:|:--------------------- |
| idx_user_date | KEY | user_id, checkin_date |
| idx_knowledge | KEY | knowledge_id          |

### 外键关系

| 约束名                | 字段           | 引用表                                    |
|:------------------ |:------------ |:-------------------------------------- |
| fk_study_user      | user_id      | user(id) ON DELETE CASCADE             |
| fk_study_knowledge | knowledge_id | knowledge_entry(id) ON DELETE SET NULL |

### 覆盖接口

`POST /study/checkin` · `GET /user/study/stat`

---

## 13. `browse_history` — 浏览历史表

**设计原因**：记录用户浏览过的词条/作品/模板，按 `create_time` 倒序返回最近浏览，查询时 GROUP BY target 做去重。

### 字段清单

| 列名          | 类型       | 约束                                  | 说明                        |
|:----------- |:--------:|:----------------------------------- |:------------------------- |
| id          | INT      | PK, AUTO_INCREMENT                  | 主键                        |
| user_id     | INT      | NOT NULL, FK → user(id)             | 用户 ID                     |
| target_type | TINYINT  | NOT NULL                            | 浏览类型：1-知识词条 2-动画作品 3-创作模板 |
| target_id   | INT      | NOT NULL                            | 被浏览的目标资源 ID               |
| create_time | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 浏览时间                      |

### 索引

| 名称            | 类型  | 字段                        |
|:------------- |:---:|:------------------------- |
| idx_user_time | KEY | user_id, create_time DESC |
| idx_target    | KEY | target_type, target_id    |

### 外键关系

| 约束名             | 字段      | 引用表                        |
|:--------------- |:------- |:-------------------------- |
| fk_history_user | user_id | user(id) ON DELETE CASCADE |

### 覆盖接口

`GET /user/history/list`

---

## 14. `sandbox_draft` — 沙箱创作草稿表（含版本历史）

**设计原因**：沙箱创作需要自动保存 + 版本回退，每次保存写入一条记录，`version` 递增标识版本号，`work_id` 非空表示从作品 Fork 而来。

### 字段清单

| 列名          | 类型            | 约束                                  | 说明               |
|:----------- |:-------------:|:----------------------------------- |:---------------- |
| id          | INT           | PK, AUTO_INCREMENT                  | 草稿 ID            |
| user_id     | INT           | NOT NULL, FK → user(id)             | 用户 ID            |
| work_id     | INT           | DEFAULT NULL, FK → work(id)         | 关联作品 ID（Fork 来源） |
| manim_code  | TEXT          | DEFAULT NULL                        | Manim 代码内容       |
| preview_url | VARCHAR(1000) | DEFAULT NULL                        | 预览视频 URL         |
| version     | INT           | NOT NULL, DEFAULT 1                 | 版本号，每次保存自增       |
| note        | VARCHAR(200)  | DEFAULT NULL                        | 版本备注说明           |
| create_time | DATETIME      | NOT NULL, DEFAULT CURRENT_TIMESTAMP | 草稿保存时间           |

### 索引

| 名称            | 类型  | 字段                        |
|:------------- |:---:|:------------------------- |
| idx_user      | KEY | user_id                   |
| idx_work      | KEY | work_id                   |
| idx_user_time | KEY | user_id, create_time DESC |

### 外键关系

| 约束名           | 字段      | 引用表                         |
|:------------- |:------- |:--------------------------- |
| fk_draft_user | user_id | user(id) ON DELETE CASCADE  |
| fk_draft_work | work_id | work(id) ON DELETE SET NULL |

### 覆盖接口

`GET /sandbox/version/list` · `POST /sandbox/draft/save`

---

## ER 关系总图

```
user (1) ──< (N) task
user (1) ──< (N) work
user (1) ──< (N) work_like
user (1) ──< (N) work_comment
user (1) ──< (N) user_collect      (多态：可收藏词条/作品/模板)
user (1) ──< (N) user_follow        (关注者 → 被关注者)
user (1) ──< (N) study_record
user (1) ──< (N) browse_history
user (1) ──< (N) sandbox_draft

knowledge_category (1) ──< (N) knowledge_entry
knowledge_entry (1) ──< (N) animation
knowledge_entry (1) ──< (N) study_record

work (1) ──< (N) work_like
work (1) ──< (N) work_comment
work (1) ──< (N) sandbox_draft
work (1) ──< (1) work               (Fork 自引用：source_work_id)
```

## 统计汇总

| 指标   | 数值    |
|:---- |:-----:|
| 总表数  | 14    |
| 外键约束 | 17    |
| 唯一约束 | 4     |
| 索引   | 19    |
| 覆盖接口 | ~41 个 |
