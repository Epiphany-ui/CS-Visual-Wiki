# Manim AI 系统 — 实体类表文档

> Java 后端实体映射文档  
> 包路径：`com.manim.pojo`（14 个 POJO）· `com.manim.dto`（3 个 DTO）

---

# 第一部分：POJO 实体类

所有实体类均位于 `com.manim.pojo` 包，使用 MyBatis-Plus `@TableName` 注解映射数据库表名，字段通过 `map-underscore-to-camel-case` 自动转换。

---

## 1. `User` → `user` 表

**类说明**：系统登录用户

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| username | String | username | |
| password | String | password | @JsonIgnore（响应中隐藏） |
| nickname | String | nickname | |
| avatar | String | avatar | |
| intro | String | intro | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT)<br>@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss") |

---

## 2. `Task` → `task` 表

**类说明**：动画生成任务

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| userId | Integer | user_id | |
| userInput | String | user_input | |
| status | Integer | status | 0-处理中 1-成功 2-失败 |
| videoPath | String | video_path | |
| errorLog | String | error_log | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT)<br>@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss") |
| updateTime | LocalDateTime | update_time | @TableField(fill = FieldFill.INSERT_UPDATE)<br>@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss") |

---

## 3. `KnowledgeCategory` → `knowledge_category` 表

**类说明**：百科知识分类

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| name | String | name | |
| icon | String | icon | |
| description | String | description | |
| sortOrder | Integer | sort_order | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

## 4. `KnowledgeEntry` → `knowledge_entry` 表

**类说明**：百科知识词条（五段式内容）

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| categoryId | Integer | category_id | |
| title | String | title | |
| summary | String | summary | |
| definition | String | definition | |
| principle | String | principle | |
| example | String | example | |
| complexity | String | complexity | |
| misconception | String | misconception | |
| source | String | source | |
| difficulty | Integer | difficulty | 1-入门 2-中等 3-困难 |
| viewCount | Integer | view_count | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |
| updateTime | LocalDateTime | update_time | @TableField(fill = FieldFill.INSERT_UPDATE) |

---

## 5. `Animation` → `animation` 表

**类说明**：动画资源（词条配套演示动画）

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| knowledgeId | Integer | knowledge_id | |
| title | String | title | |
| videoPath | String | video_path | |
| duration | Integer | duration | 单位：秒 |
| playCount | Integer | play_count | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

## 6. `Template` → `template` 表

**类说明**：创作模板

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| name | String | name | |
| description | String | description | |
| cover | String | cover | |
| category | String | category | 模板分类标识 |
| configSchema | String | config_schema | JSON 字符串 |
| previewVideo | String | preview_video | |
| defaultCode | String | default_code | |
| useCount | Integer | use_count | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |
| updateTime | LocalDateTime | update_time | @TableField(fill = FieldFill.INSERT_UPDATE) |

---

## 7. `Work` → `work` 表

**类说明**：动画作品（成品）

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| userId | Integer | user_id | |
| title | String | title | |
| description | String | description | |
| manimCode | String | manim_code | |
| videoPath | String | video_path | |
| cover | String | cover | |
| tags | String | tags | 逗号分隔 |
| isPublic | Integer | is_public | 0-私密 1-公开 |
| sourceWorkId | Integer | source_work_id | Fork 来源（可为 null） |
| viewCount | Integer | view_count | |
| likeCount | Integer | like_count | |
| collectCount | Integer | collect_count | |
| forkCount | Integer | fork_count | |
| status | Integer | status | 0-草稿 1-已发布 |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT)<br>@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss") |
| updateTime | LocalDateTime | update_time | @TableField(fill = FieldFill.INSERT_UPDATE)<br>@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss") |

---

## 8. `WorkLike` → `work_like` 表

**类说明**：作品点赞

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| workId | Integer | work_id | |
| userId | Integer | user_id | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

## 9. `WorkComment` → `work_comment` 表

**类说明**：作品评论

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| workId | Integer | work_id | |
| userId | Integer | user_id | |
| content | String | content | |
| replyToId | Integer | reply_to_id | 楼中楼回复（可为 null） |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT)<br>@JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss") |

---

## 10. `UserCollect` → `user_collect` 表

**类说明**：用户收藏（多态）

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| userId | Integer | user_id | |
| targetType | Integer | target_type | 1-词条 2-作品 3-模板 |
| targetId | Integer | target_id | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

## 11. `UserFollow` → `user_follow` 表

**类说明**：用户关注关系

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| followerId | Integer | follower_id | 关注者 |
| followeeId | Integer | followee_id | 被关注者 |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

## 12. `StudyRecord` → `study_record` 表

**类说明**：学习打卡记录

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| userId | Integer | user_id | |
| knowledgeId | Integer | knowledge_id | 可为 null |
| studyDuration | Integer | study_duration | 单位：秒 |
| checkinDate | LocalDate | checkin_date | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

## 13. `BrowseHistory` → `browse_history` 表

**类说明**：浏览历史

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| userId | Integer | user_id | |
| targetType | Integer | target_type | 1-词条 2-作品 3-模板 |
| targetId | Integer | target_id | |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

## 14. `SandboxDraft` → `sandbox_draft` 表

**类说明**：沙箱创作草稿（含版本历史）

| 字段 | 类型 | 映射列 | 注解 |
|:---|:---:|:---|:---|
| id | Integer | id | @TableId(type = IdType.AUTO) |
| userId | Integer | user_id | |
| workId | Integer | work_id | Fork 来源（可为 null） |
| manimCode | String | manim_code | |
| previewUrl | String | preview_url | |
| version | Integer | version | 每次保存自增 |
| note | String | note | 版本备注 |
| createTime | LocalDateTime | create_time | @TableField(fill = FieldFill.INSERT) |

---

# 第二部分：DTO 类

DTO 类位于 `com.manim.dto` 包，用于接口返回时裁剪字段，不直接映射数据库表。

---

## 1. `CarouselDTO` — 首页轮播作品

**用途**：`GET /home/carousel` 返回首页轮播数据

| 字段 | 类型 | 数据来源 |
|:---|:---:|:---|
| workId | Integer | Work.id |
| cover | String | Work.cover |
| title | String | Work.title |
| viewCount | Integer | Work.view_count |
| authorName | String | User.nickname（跨表关联查询） |

**说明**：不直接返回 Work 实体的全部 17 个字段，只暴露前端轮播展示需要的 5 个字段。作者名通过 `userMapper.selectById(work.getUserId())` 获取。

---

## 2. `CategoryDTO` — 首页分类导航

**用途**：`GET /home/category` 返回首页分类导航

| 字段 | 类型 | 数据来源 |
|:---|:---:|:---|
| id | Integer | KnowledgeCategory.id |
| name | String | KnowledgeCategory.name |
| icon | String | KnowledgeCategory.icon |
| entryCount | Integer | `COUNT(knowledge_entry WHERE category_id = ?)` |

**说明**：`entryCount` 不是直接存的字段，而是通过 `knowledgeEntryMapper.selectCount()` 实时统计该分类下的词条数量。

---

## 3. `PythonResponse` — Python AI 服务响应

**用途**：接收 Python AI 服务 `/generate` 接口的 JSON 响应

| 字段 | 类型 | JSON 字段 | 说明 |
|:---|:---:|:---|:---|
| success | boolean | success | 是否生成成功 |
| code | String | code | 生成的 Manim 代码 |
| videoPath | String | video_path | @JsonProperty("video_path") |
| tryCount | int | try_count | @JsonProperty("try_count")，实际重试次数 |
| log | String | log | 执行日志 / 错误信息 |

**说明**：仅用于 Java 后端反序列化 Python 服务的 HTTP 响应，不返回给前端。

---

# 附录：全局公共类

## `Result<T>` — 统一响应封装

**包路径**：`com.manim.pojo.Result`

| 字段 | 类型 | 说明 |
|:---|:---:|:---|
| code | int | 响应码：200-成功 500-业务失败 401-未授权 |
| msg | String | 提示信息 |
| data | T | 业务数据（泛型） |

**静态工厂方法**：

| 方法 | 用途 |
|:---|:---|
| `Result.success()` | 成功，无 data |
| `Result.success(data)` | 成功，带 data |
| `Result.success(msg, data)` | 成功，自定义 msg + data |
| `Result.fail(msg)` | 失败，code=500 |
| `Result.fail(code, msg)` | 失败，自定义 code |

---

## 映射规则说明

MyBatis-Plus 下划线转驼峰自动映射（`map-underscore-to-camel-case: true`）：

```
数据库列名           Java 字段名
─────────────       ─────────────
user_id      →      userId
create_time  →      createTime
video_path   →      videoPath
source_work_id →    sourceWorkId
```

时间字段通过 `@TableField(fill = ...)` 自动填充：
- `FieldFill.INSERT` → 插入时自动写入当前时间
- `FieldFill.INSERT_UPDATE` → 插入和更新时自动写入当前时间
