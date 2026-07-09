# Manim AI 智能动画生成系统 — Java 后端模块

## 一、项目定位

CS-Visual-Learn 是一款面向计算机科学与数学领域的交互式知识可视化学习平台的后端服务。  
基于 **Spring Boot 2.7 + MyBatis-Plus**，负责用户认证、百科知识管理、动画任务调度、模板创作、AI 沙箱、社区画廊、个人中心等全部业务逻辑，通过 HTTP 异步调用 Python AI 服务完成 Manim 动画的代码生成与视频渲染。

| 层级 | 模块 | 端口 | 技术 |
|:---|:---|:---:|:---|
| 前端展示 | Vue 前端 | 8081 | Vue 3 + Axios |
| **业务服务** | **Java 后端（本模块）** | **8080** | **Spring Boot + MyBatis-Plus** |
| AI 能力 | Python AI 引擎 | 8000 | FastAPI + Manim + Ollama |

---

## 二、技术栈

| 技术 | 版本 | 用途 |
|:---|:---:|:---|
| Spring Boot | 2.7.18 | 基础框架 |
| MyBatis-Plus | 3.5.7 | ORM（全注解，零 XML） |
| MySQL | 8.0 | 关系数据库 |
| SpringDoc OpenAPI | 1.8.0 | Swagger 接口文档 |
| Hutool | 5.8.34 | HTTP 客户端、JSON 工具 |
| jjwt | 0.12.6 | JWT 令牌生成与解析 |
| Lombok | 可选 | 简化代码（当前使用手写 getter/setter） |
| JDK | 1.8+ | 编译运行 |

---

## 三、项目结构

```
java-web/
├── pom.xml                                    # Maven 依赖
│
├── javawebDetails/                            # 接口 & 数据库文档
│   ├── database.sql                           # 14 张表的建库建表脚本
│   ├── add_column_comments.sql                # 字段中文注释补充脚本
│   ├── CS-Visual-learn 完整接口文档（优化版）.md  # 41 个接口的完整文档
│   ├── database_tables.md                     # 数据库表结构文档
│   └── entity_classes.md                      # 实体类映射文档
│
└── src/main/java/com/manim/
    ├── ManimApplication.java                  # 启动类 @SpringBootApplication + @EnableAsync
    │
    ├── config/
    │   ├── AsyncConfig.java                   # 异步线程池（core=2, max=5, queue=20）
    │   ├── FilterConfig.java                  # 注册 AuthFilter 到 /api/v1/*
    │   ├── JwtConfig.java                     # 启动时读取 yml 注入 JwtUtil
    │   ├── MyMetaObjectHandler.java           # 自动填充 createTime/updateTime
    │   ├── SwaggerConfig.java                 # Swagger 文档信息
    │   └── WebConfig.java                     # CORS 跨域配置
    │
    ├── filter/
    │   └── AuthFilter.java                    # JWT 认证过滤器（白名单放行）
    │
    ├── controller/                            # 9 个 Controller，覆盖 8 大业务模块
    │   ├── AuthController.java                # 用户注册/登录/信息/退出
    │   ├── HomeController.java                # 首页轮播/分类导航/作品列表
    │   ├── SearchController.java              # 全局搜索
    │   ├── KnowledgeController.java           # 百科词条/详情/动画/推荐/收藏/打卡
    │   ├── TemplateController.java            # 模板列表/详情/生成/渲染/保存/导出
    │   ├── AiSandboxController.java           # AI 生成/修复/沙箱渲染/草稿/发布
    │   ├── GalleryController.java             # 画廊排行榜
    │   ├── WorkController.java                # 作品详情/点赞/收藏/评论/Fork/关注
    │   └── UserCenterController.java          # 个人中心/作品/收藏/历史/统计
    │
    ├── service/
    │   ├── AiService.java                     # AI 代码生成/修复
    │   ├── AnimationService.java              # 动画资源查询
    │   ├── BrowseHistoryService.java          # 浏览历史
    │   ├── KnowledgeCategoryService.java      # 百科分类
    │   ├── KnowledgeEntryService.java         # 百科词条
    │   ├── SandboxDraftService.java           # 沙箱草稿/版本历史
    │   ├── SearchService.java                 # 全局搜索
    │   ├── StudyRecordService.java            # 学习打卡
    │   ├── TaskService.java                   # 渲染任务
    │   ├── TemplateService.java               # 创作模板
    │   ├── UserCollectService.java            # 用户收藏（多态）
    │   ├── UserFollowService.java             # 用户关注
    │   ├── UserService.java                   # 用户账号
    │   ├── WorkCommentService.java            # 作品评论
    │   ├── WorkService.java                   # 作品
    │   └── impl/                              # 全部实现类
    │
    ├── mapper/                                # 14 个 Mapper（继承 BaseMapper）
    │
    ├── pojo/                                  # 14 个实体类 @TableName
    │   ├── User.java                          # user 表
    │   ├── Task.java                          # task 表
    │   ├── KnowledgeCategory.java             # knowledge_category 表
    │   ├── KnowledgeEntry.java                # knowledge_entry 表
    │   ├── Animation.java                     # animation 表
    │   ├── Template.java                      # template 表
    │   ├── Work.java                          # work 表
    │   ├── WorkLike.java                      # work_like 表
    │   ├── WorkComment.java                   # work_comment 表
    │   ├── UserCollect.java                   # user_collect 表
    │   ├── UserFollow.java                    # user_follow 表
    │   ├── StudyRecord.java                   # study_record 表
    │   ├── BrowseHistory.java                 # browse_history 表
    │   ├── SandboxDraft.java                  # sandbox_draft 表
    │   └── Result.java                        # 统一响应 {code, msg, data}
    │
    ├── dto/                                   # 7 个数据传输对象
    │   ├── CarouselDTO.java                   # 首页轮播
    │   ├── CategoryDTO.java                   # 首页分类
    │   ├── WorkListDTO.java                   # 首页/画廊作品列表
    │   ├── KnowledgeListDTO.java              # 百科列表
    │   ├── KnowledgeSearchDTO.java            # 搜索-词条
    │   ├── WorkSearchDTO.java                 # 搜索-作品
    │   ├── TemplateSearchDTO.java             # 搜索-模板
    │   ├── UserSearchDTO.java                 # 搜索-用户
    │   └── PythonResponse.java                # Python 服务响应
    │
    ├── exception/
    │   ├── BusinessException.java             # 业务异常
    │   ├── UnauthorizedException.java         # 401 未授权
    │   └── GlobalExceptionHandler.java        # 全局异常处理
    │
    └── utils/
        ├── JwtUtil.java                       # JWT 工具类
        ├── Md5Util.java                       # MD5 加密
        └── UserContext.java                   # ThreadLocal 用户上下文
```

---

## 四、数据库设计

共 **14 张表**，覆盖 8 大业务模块。详细结构见 `javawebDetails/database_tables.md`。

| 表名 | 说明 | 关键字段 |
|:---|:---|:---|
| user | 系统用户 | username, password, nickname, avatar, intro |
| task | 渲染任务 | user_id(FK), user_input, status, video_path, error_log |
| knowledge_category | 百科分类 | name, icon, sort_order |
| knowledge_entry | 百科词条 | category_id(FK), title, definition~misconception, difficulty |
| animation | 动画资源 | knowledge_id(FK), title, video_path, duration |
| template | 创作模板 | name, config_schema(JSON), default_code, use_count |
| work | 动画作品 | user_id(FK), title, manim_code, source_work_id, like/view/collect/fork_count |
| work_like | 作品点赞 | work_id(FK), user_id(FK), UNIQUE(work_id, user_id) |
| work_comment | 作品评论 | work_id(FK), user_id(FK), content, reply_to_id |
| user_collect | 用户收藏（多态） | user_id(FK), target_type, target_id, UNIQUE 三字段 |
| user_follow | 用户关注 | follower_id(FK), followee_id(FK), UNIQUE 两字段 |
| study_record | 学习打卡 | user_id(FK), knowledge_id(FK), study_duration, checkin_date |
| browse_history | 浏览历史 | user_id(FK), target_type, target_id |
| sandbox_draft | 沙箱草稿 | user_id(FK), work_id(FK), manim_code, version |

**17 个外键约束、4 个唯一键、19 个索引**。建表执行 `javawebDetails/database.sql`。

---

## 五、API 接口总表

所有接口统一前缀 `/api/v1`，返回 `Result<T>` 格式：

```json
{ "code": 200, "msg": "操作成功", "data": {} }
```

### 5.1 登录注册模块（AuthController）

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| POST | /api/v1/user/register | 🔓 | 注册，返回 token |
| POST | /api/v1/user/login | 🔓 | 登录，返回 token |
| GET | /api/v1/user/info | 🔒 | 获取当前用户信息 |
| POST | /api/v1/user/logout | 🔒 | 退出登录 |

### 5.2 首页模块（HomeController）

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| GET | /api/v1/home/carousel | 🔓 | 热门轮播（按播放量取前 6） |
| GET | /api/v1/home/category | 🔓 | 分类导航（含词条数量） |
| GET | /api/v1/home/work/list | 🔓 | 精选/最新作品列表（分页） |

### 5.3 搜索模块（SearchController）

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| GET | /api/v1/search/all | 🔓 | 全局搜索（词条/作品/模板/用户，各 5 条） |

### 5.4 百科知识模块（KnowledgeController）

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| GET | /api/v1/knowledge/category/list | 🔓 | 分类知识点列表（含动画数量） |
| GET | /api/v1/knowledge/detail | 🔓 | 词条详情（自动递增 view_count） |
| GET | /api/v1/knowledge/animation/list | 🔓 | 配套动画列表 |
| GET | /api/v1/knowledge/recommend | 🔓 | 相关推荐（同分类按热度） |
| POST | /api/v1/knowledge/collect | 🔒 | 收藏/取消收藏词条 |
| POST | /api/v1/study/checkin | 🔒 | 学习打卡 |

### 5.5 模板创作模块（TemplateController）

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| GET | /api/v1/template/list | 🔓 | 模板列表（按使用量排序） |
| GET | /api/v1/template/detail | 🔓 | 模板详情 + config_schema |
| POST | /api/v1/template/generate | 🔒 | 提交渲染任务 |
| GET | /api/v1/render/status | 🔒 | 查询渲染状态 |
| POST | /api/v1/template/work/save | 🔒 | 保存渲染结果为作品 |
| GET | /api/v1/work/export | 🔒 | 导出 mp4/gif/code |
| GET | /api/v1/task/list | 🔒 | 历史任务列表 |

### 5.6 AI 沙箱模块（AiSandboxController）

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| POST | /api/v1/ai/generate/code | 🔓 | AI 生成 Manim 代码 |
| POST | /api/v1/ai/fix/code | 🔓 | AI 修复代码错误 |
| POST | /api/v1/sandbox/render | 🔒 | 沙箱手动渲染 |
| GET | /api/v1/sandbox/version/list | 🔒 | 版本历史查询 |
| POST | /api/v1/sandbox/draft/save | 🔒 | 保存草稿（版本自增） |
| POST | /api/v1/work/publish | 🔒 | 发布作品至画廊 |

### 5.7 社区画廊模块

**GalleryController**：

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| GET | /api/v1/gallery/list | 🔓 | 画廊排行榜（日/周/月） |

**WorkController**：

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| GET | /api/v1/work/public/detail | 🔓 | 公开作品详情 |
| POST | /api/v1/work/like | 🔒 | 点赞/取消 |
| POST | /api/v1/work/collect | 🔒 | 收藏/取消 |
| GET | /api/v1/work/comment/list | 🔓 | 评论列表 |
| POST | /api/v1/work/comment/add | 🔒 | 发布评论（楼中楼） |
| POST | /api/v1/work/fork | 🔒 | Fork 二次创作 |
| GET | /api/v1/user/author/home | 🔓 | 创作者主页 |
| POST | /api/v1/user/follow | 🔒 | 关注/取消关注 |

### 5.8 个人中心模块（UserCenterController）

| 方法 | 路径 | 鉴权 | 说明 |
|:---:|:---|:---:|:---|
| GET | /api/v1/user/home/data | 🔒 | 个人中心首页数据 |
| GET | /api/v1/user/work/list | 🔒 | 我的作品列表 |
| GET | /api/v1/user/collect/list | 🔒 | 我的收藏列表 |
| GET | /api/v1/user/history/list | 🔒 | 浏览历史 |
| GET | /api/v1/user/study/stat | 🔒 | 学习统计 |
| GET | /api/v1/user/author/stat | 🔒 | 创作者数据统计 |
| PUT | /api/v1/user/profile/update | 🔒 | 更新个人资料 |

---

## 六、认证与数据流

```
请求 → AuthFilter (Filter, 拦截 /api/v1/*)
  │
  ├─ 白名单 (/api/v1/user/register, /api/v1/user/login) → 直接放行
  │
  └─ 其他请求 → 校验 Authorization: Bearer <token>
       ├─ 无/无效 → 返回 401 JSON
       └─ 有效 → JwtUtil 解析 username
                 → UserContext.setUsername(username)
                 → 放行 → Controller 从 UserContext 取用户
                 → finally → UserContext.remove()
```

### 异步调用 Python AI 服务

```
POST /api/v1/template/generate  或  POST /api/v1/sandbox/render
  │
  ├─ 入库 task (status=0)
  │
  └─ @Async（独立线程池 manim-async-*）
       │
       ├─ POST http://localhost:8000/generate
       │   body: { user_input, max_retry }
       │
       └─ response: { success, video_path, log }
            ├─ success=true  → status=1, 写入 video_path
            └─ success=false → status=2, 写入 error_log
```

---

## 七、异常处理体系

```
Filter 层（AuthFilter）
  └─ 手动 write JSON（Filter 在 DispatcherServlet 之前执行）

Controller 层
  └─ throw BusinessException / UnauthorizedException
       └─ @RestControllerAdvice（GlobalExceptionHandler）捕获
            └─ 封装为 Result{code, msg} 返回前端

GlobalExceptionHandler 处理范围：
  ├─ UnauthorizedException              → 401
  ├─ BusinessException                  → 自定义 code（默认 500）
  ├─ MissingServletRequestParameterException → 400
  ├─ HttpRequestMethodNotSupportedException  → 405
  └─ Exception（兜底）                  → 500
```

---

## 八、配置说明

### application.yml 要点

```yaml
server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/manim_ai
    username: root
    password: 123456       # ← 修改为本地数据库密码

mybatis-plus:
  type-aliases-package: com.manim.pojo
  configuration:
    map-underscore-to-camel-case: true
    log-impl: org.apache.ibatis.logging.stdout.StdOutImpl

jwt:
  secret: ManimAI2024SecretKeyForJWTTokenGenerationMustBe256BitsLong!!
  expiration: 86400000     # 24 小时

manim:
  ai:
    base-url: http://localhost:8000
    generate-endpoint: /generate
    read-timeout: 180000   # 3 分钟
```

---

## 九、启动步骤

### 1. 建库建表

在 DataGrip 中依次运行：
1. `javawebDetails/database.sql` — 创建 14 张表
2. `javawebDetails/add_column_comments.sql` — 补充字段中文注释

### 2. 修改数据库密码

编辑 `src/main/resources/application.yml`，将 `spring.datasource.password` 改为本地密码。

### 3. 启动 Python AI 服务（可选）

AI 沙箱和模板渲染功能依赖 Python 服务，确保 `http://localhost:8000` 可访问。  
如果仅测试用户/百科/社区等模块，Python 服务不可用时 AI 相关接口会返回降级提示文案。

### 4. 启动 Java 服务

```bash
cd java-web
mvn spring-boot:run
```

或直接在 IDEA 中运行 `ManimApplication.main()`。

### 5. 访问

| 地址 | 说明 |
|:---|:---|
| `http://localhost:8080/swagger-ui.html` | Swagger 接口文档 |
| `http://localhost:8000/docs` | Python AI 服务文档 |

---

## 十、Swagger 测试说明

1. 打开 `http://localhost:8080/swagger-ui.html`
2. 先调用 **用户账号接口** 的 `POST /api/v1/user/login` 或 `POST /api/v1/user/register`
3. 从返回 `data` 中复制 `token` 值
4. 点击 Swagger 右上角 **Authorize**，输入 `Bearer <token>`（注意 Bearer 后有空格）
5. 现在可测试所有 🔒 需登录的接口

---

## 十一、项目文档索引

| 文档 | 位置 | 说明 |
|:---|:---|:---|
| 接口文档（优化版） | `javawebDetails/CS-Visual-learn 完整接口文档（优化版）.md` | 41 个接口的完整定义 |
| 数据库表文档 | `javawebDetails/database_tables.md` | 14 张表的字段/索引/外键 |
| 实体类映射文档 | `javawebDetails/entity_classes.md` | POJO ↔ 表映射关系 |
| 数据库脚本 | `javawebDetails/database.sql` | 建库建表（14 张表） |
| 注释补充脚本 | `javawebDetails/add_column_comments.sql` | 字段中文注释 |
