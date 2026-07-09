# CS-Visual-learn 前端配套完整接口文档（优化版）

> 基于原版文档优化：统一路径前缀、标注鉴权、补充错误码规范、优化接口粒度  
> **所有接口响应统一格式**：`{ "code": 200, "msg": "操作成功", "data": {...} }`，业务数据放在 data 内

---

## 📋 通用规范

### 1. 基础路径

所有接口统一前缀：`/api/v1`

完整请求示例：`POST /api/v1/user/login`

### 2. 公共响应结构

```json
{
  "code": 200,       // 状态码
  "msg": "操作成功", // 提示信息
  "data": {}         // 业务数据（泛型），以下文档只描述 data 内的字段
}
```

### 3. 错误码定义

| code | 含义      | 说明             |
|:----:|:------- |:-------------- |
| 200  | 成功      | 请求正常处理         |
| 400  | 请求参数错误  | 缺少必填参数或参数格式不正确 |
| 401  | 未授权     | JWT 令牌缺失/过期/无效 |
| 403  | 无权限     | 已登录但无权访问该资源    |
| 404  | 资源不存在   | 请求的资源未找到       |
| 405  | 请求方法不支持 | 使用了错误的 HTTP 方法 |
| 500  | 服务器内部错误 | 业务异常或未捕获异常     |

### 4. 分页参数规范

| 参数   | 类型  | 默认值 | 说明          |
|:---- |:---:|:---:|:----------- |
| page | int | 1   | 页码，从 1 开始   |
| size | int | 10  | 每页条数，最大 100 |

分页响应 data 结构：

```json
{
  "list": [],   // 数据列表
  "total": 0    // 总条数
}
```

### 5. 鉴权说明

- `🔒 需登录`：请求头需携带 `Authorization: Bearer <token>`
- `🔓 免登录`：白名单接口，无需 token
- JWT token 通过登录/注册接口获取，有效期 24 小时

### 6. 草稿 vs 发布的生命周期

```
沙箱编辑 → [保存草稿] → sandbox_draft 表（可多次保存，产生版本历史）
         → [发布作品] → work 表（is_public=0 私密 / is_public=1 公开）
         → [公开至画廊] → 前端展示

模板创作 → [生成渲染] → task 表（异步渲染任务）
         → [保存作品] → work 表（可直接保存为私密或公开）
```

---

## 一、登录注册模块

| 接口     | 方法   | 路径                    | 鉴权     |
|:------ |:----:|:--------------------- |:------:|
| 用户登录   | POST | /api/v1/user/login    | 🔓 免登录 |
| 用户注册   | POST | /api/v1/user/register | 🔓 免登录 |
| 获取用户信息 | GET  | /api/v1/user/info     | 🔒 需登录 |
| 退出登录   | POST | /api/v1/user/logout   | 🔒 需登录 |

### 1.1 用户登录

- **路径**：`POST /api/v1/user/login`
- **场景**：登录页账号密码登录，获取 JWT 令牌与用户信息

请求参数：

| 参数       | 类型     | 必填  | 说明     |
|:-------- |:------:|:---:|:------ |
| username | string | 是   | 用户名/账号 |
| password | string | 是   | 登录密码   |

响应：

```json
{
  "code": 200,
  "msg": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "userId": 1,
    "username": "zhangsan",
    "nickname": "张三",
    "avatar": "https://example.com/avatar.png"
  }
}
```

### 1.2 用户注册

- **路径**：`POST /api/v1/user/register`
- **场景**：新用户注册，注册后自动登录返回 token

请求参数：

| 参数       | 类型     | 必填  | 说明               |
|:-------- |:------:|:---:|:---------------- |
| username | string | 是   | 用户名（唯一，不可重复）     |
| password | string | 是   | 密码（不少于 6 位）      |
| nickname | string | 否   | 昵称（默认取 username） |

响应：与 1.1 登录接口相同

```json
{
  "code": 200,
  "msg": "注册成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiJ9...",
    "userId": 1,
    "username": "zhangsan",
    "nickname": "张三"
  }
}
```

### 1.3 获取当前登录用户信息

- **路径**：`GET /api/v1/user/info`
- **场景**：全局页面校验登录状态、展示用户信息

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "userId": 1,
    "username": "zhangsan",
    "nickname": "张三",
    "avatar": "https://example.com/avatar.png",
    "intro": "热爱数学和编程",
    "createTime": "2025-01-01 12:00:00"
  }
}
```

### 1.4 用户退出登录

- **路径**：`POST /api/v1/user/logout`
- **场景**：退出登录，前端清除 token

响应：

```json
{
  "code": 200,
  "msg": "已退出登录",
  "data": null
}
```

> JWT 为无状态令牌，后端清除 ThreadLocal 上下文，前端删除本地 token 即可。

---

## 二、首页模块

| 接口        | 方法  | 路径                     | 鉴权     |
|:--------- |:---:|:---------------------- |:------:|
| 获取轮播动画    | GET | /api/v1/home/carousel  | 🔓 免登录 |
| 获取分类导航    | GET | /api/v1/home/category  | 🔓 免登录 |
| 获取精选/最新作品 | GET | /api/v1/home/work/list | 🔓 免登录 |

### 2.1 获取首页热门轮播动画

- **路径**：`GET /api/v1/home/carousel`
- **场景**：首页渲染热门动画轮播

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "workId": 1,
      "cover": "https://example.com/cover1.png",
      "title": "冒泡排序可视化",
      "viewCount": 15230,
      "authorName": "张三"
    },
    {
      "workId": 2,
      "cover": "https://example.com/cover2.png",
      "title": "傅里叶级数方波分解",
      "viewCount": 8920,
      "authorName": "李四"
    }
  ]
}
```

### 2.2 获取首页知识点分类列表

- **路径**：`GET /api/v1/home/category`
- **场景**：首页展示学科分类导航

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "id": 1,
      "name": "算法",
      "icon": "https://example.com/icon-algo.png",
      "entryCount": 42
    },
    {
      "id": 2,
      "name": "数据结构",
      "icon": "https://example.com/icon-ds.png",
      "entryCount": 28
    },
    {
      "id": 3,
      "name": "高等数学",
      "icon": "https://example.com/icon-math.png",
      "entryCount": 35
    }
  ]
}
```

### 2.3 获取首页精选/最新作品列表

- **路径**：`GET /api/v1/home/work/list`
- **场景**：首页渲染精选或最新公开作品

请求参数：

| 参数   | 类型     | 必填  | 默认     | 说明                      |
|:---- |:------:|:---:|:------:|:----------------------- |
| type | string | 否   | latest | featured-精选 / latest-最新 |
| page | int    | 否   | 1      | 页码                      |
| size | int    | 否   | 10     | 每页条数                    |

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "workId": 1,
        "cover": "https://example.com/cover1.png",
        "title": "冒泡排序可视化",
        "authorName": "张三",
        "likeCount": 256,
        "viewCount": 15230
      }
    ],
    "total": 1
  }
}
```

---

## 三、搜索模块

| 接口   | 方法  | 路径                 | 鉴权     |
|:---- |:---:|:------------------ |:------:|
| 全局搜索 | GET | /api/v1/search/all | 🔓 免登录 |

### 3.1 全局统一搜索

- **路径**：`GET /api/v1/search/all`
- **场景**：首页搜索框全局搜索（知识点/作品/模板/用户）

请求参数：

| 参数      | 类型     | 必填  | 默认  | 说明    |
|:------- |:------:|:---:|:---:|:----- |
| keyword | string | 是   | -   | 搜索关键词 |
| page    | int    | 否   | 1   | 页码    |
| size    | int    | 否   | 10  | 每页条数  |

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "knowledgeList": [
      {
        "id": 1,
        "title": "冒泡排序",
        "summary": "通过重复遍历比较相邻元素..."
      }
    ],
    "workList": [
      {
        "workId": 1,
        "title": "冒泡排序可视化",
        "authorName": "张三"
      }
    ],
    "templateList": [
      {
        "id": 1,
        "name": "排序算法可视化",
        "useCount": 128
      }
    ],
    "userList": [
      {
        "userId": 1,
        "nickname": "张三",
        "avatar": "https://example.com/avatar.png"
      }
    ]
  }
}
```

---

## 四、百科知识模块 + 学习打卡

| 接口         | 方法   | 路径                               | 鉴权     |
|:---------- |:----:|:-------------------------------- |:------:|
| 获取分类知识点列表  | GET  | /api/v1/knowledge/category/list  | 🔓 免登录 |
| 获取词条详情     | GET  | /api/v1/knowledge/detail         | 🔓 免登录 |
| 获取配套动画     | GET  | /api/v1/knowledge/animation/list | 🔓 免登录 |
| 获取相关推荐     | GET  | /api/v1/knowledge/recommend      | 🔓 免登录 |
| 收藏/取消收藏知识点 | POST | /api/v1/knowledge/collect        | 🔒 需登录 |
| 学习打卡       | POST | /api/v1/study/checkin            | 🔒 需登录 |

### 4.1 获取百科分类知识点列表

- **路径**：`GET /api/v1/knowledge/category/list`
- **场景**：百科分类列表页渲染

请求参数：

| 参数         | 类型  | 必填  | 说明                  |
|:---------- |:---:|:---:|:------------------- |
| categoryId | int | 否   | 分类 ID（不传返回全部分类）     |
| difficulty | int | 否   | 难度筛选：1-入门 2-中等 3-困难 |
| page       | int | 否   | 页码                  |
| size       | int | 否   | 每页条数                |

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "title": "冒泡排序",
        "summary": "通过重复遍历数组比较相邻元素...",
        "difficulty": 1,
        "animationCount": 3
      }
    ],
    "total": 1
  }
}
```

### 4.2 获取知识点百科详情

- **路径**：`GET /api/v1/knowledge/detail`
- **场景**：百科详情页渲染完整词条内容

请求参数：`knowledgeId`（词条 ID）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "id": 1,
    "title": "冒泡排序",
    "summary": "通过重复遍历数组，依次比较相邻元素...",
    "definition": "冒泡排序是一种简单的排序算法...",
    "principle": "每一轮遍历将最大（或最小）的元素"冒泡"到数组末端...",
    "example": "输入数组 [5, 3, 8, 4, 2]：\n第一轮：3, 5, 4, 2, [8]\n第二轮：3, 4, 2, [5, 8]\n...",
    "complexity": "最好 O(n)，最坏 O(n²)，平均 O(n²)",
    "misconception": "1. 冒泡排序和选择排序容易混淆...",
    "source": "维基百科",
    "difficulty": 1,
    "categoryId": 1,
    "viewCount": 15230
  }
}
```

### 4.3 获取知识点配套动画列表

- **路径**：`GET /api/v1/knowledge/animation/list`
- **场景**：百科详情页加载内嵌动画

请求参数：`knowledgeId`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "id": 1,
      "title": "冒泡排序全过程演示",
      "videoPath": "/videos/bubble-sort-full.mp4",
      "duration": 120,
      "playCount": 8920
    },
    {
      "id": 2,
      "title": "冒泡排序优化版对比",
      "videoPath": "/videos/bubble-sort-opt.mp4",
      "duration": 85,
      "playCount": 4520
    }
  ]
}
```

### 4.4 获取相关推荐知识点

- **路径**：`GET /api/v1/knowledge/recommend`
- **场景**：百科详情页推荐前置/关联/拓展知识

请求参数：`knowledgeId`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "id": 2,
      "title": "选择排序",
      "summary": "每次从未排序部分选出最小元素...",
      "difficulty": 1
    },
    {
      "id": 3,
      "title": "插入排序",
      "summary": "将未排序元素插入已排序序列的合适位置...",
      "difficulty": 1
    }
  ]
}
```

### 4.5 知识点收藏/取消收藏

- **路径**：`POST /api/v1/knowledge/collect`

请求参数：

| 参数          | 类型   | 必填  | 说明                   |
|:----------- |:----:|:---:|:-------------------- |
| knowledgeId | int  | 是   | 词条 ID                |
| isCollect   | bool | 是   | true-收藏 / false-取消收藏 |

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": null
}
```

### 4.6 学习打卡 & 进度记录

- **路径**：`POST /api/v1/study/checkin`

请求参数：

| 参数            | 类型  | 必填  | 说明            |
|:------------- |:---:|:---:|:------------- |
| knowledgeId   | int | 否   | 关联知识点 ID（可为空） |
| studyDuration | int | 是   | 学习时长（秒）       |

响应：

```json
{
  "code": 200,
  "msg": "打卡成功",
  "data": null
}
```

---

## 五、模板创作模块

| 接口      | 方法   | 路径                         | 鉴权     |
|:------- |:----:|:-------------------------- |:------:|
| 获取模板列表  | GET  | /api/v1/template/list      | 🔓 免登录 |
| 获取模板详情  | GET  | /api/v1/template/detail    | 🔓 免登录 |
| 模板生成动画  | POST | /api/v1/template/generate  | 🔒 需登录 |
| 查询渲染状态  | GET  | /api/v1/render/status      | 🔒 需登录 |
| 保存/发布作品 | POST | /api/v1/template/work/save | 🔒 需登录 |
| 导出作品资源  | GET  | /api/v1/work/export        | 🔒 需登录 |

### 5.1 获取模板分类列表

- **路径**：`GET /api/v1/template/list`
- **场景**：模板库列表页

请求参数：`category`（分类筛选）、`page`、`size`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "name": "排序算法可视化",
        "cover": "https://example.com/template-sort.png",
        "description": "支持冒泡/选择/插入/快排/归并切换",
        "category": "排序",
        "useCount": 256,
        "configFields": ["arraySize", "speed", "algorithmType"]
      }
    ],
    "total": 1
  }
}
```

### 5.2 获取模板详情及参数配置

- **路径**：`GET /api/v1/template/detail`
- **场景**：模板参数配置页加载

请求参数：`templateId`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "id": 1,
    "name": "排序算法可视化",
    "description": "支持冒泡/选择/插入/快排/归并切换，可调数组大小、速度",
    "cover": "https://example.com/template-sort.png",
    "category": "排序",
    "configSchema": {
      "type": "object",
      "properties": {
        "arraySize": { "type": "integer", "default": 10, "min": 3, "max": 50 },
        "speed": { "type": "string", "default": "normal", "enum": ["slow", "normal", "fast"] },
        "algorithmType": { "type": "string", "default": "bubble", "enum": ["bubble", "selection", "insertion", "quick", "merge"] }
      }
    },
    "previewVideo": "/videos/template-sort-preview.mp4",
    "useCount": 256
  }
}
```

### 5.3 模板参数生成动画（核心渲染接口）

- **路径**：`POST /api/v1/template/generate`
- **场景**：用户修改参数后一键生成动画，返回 taskId 供轮询

请求参数：

| 参数        | 类型     | 必填  | 默认  | 说明                 |
|:--------- |:------:|:---:|:---:|:------------------ |
| userInput | string | 是   | -   | 用户需求文本 / 模板参数 JSON |
| maxRetry  | int    | 否   | 3   | AI 调试最大重试次数        |

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "taskId": 42
  }
}
```

### 5.4 查询渲染任务状态

- **路径**：`GET /api/v1/render/status`
- **场景**：前端轮询渲染进度

请求参数：`taskId`

响应（处理中）：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "taskId": 42,
    "status": 0,
    "videoPath": null,
    "errorLog": null,
    "createTime": "2025-01-01 12:00:00"
  }
}
```

响应（成功）：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "taskId": 42,
    "status": 1,
    "videoPath": "/videos/output_42.mp4",
    "errorLog": null,
    "createTime": "2025-01-01 12:00:00",
    "updateTime": "2025-01-01 12:05:30"
  }
}
```

响应（失败）：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "taskId": 42,
    "status": 2,
    "videoPath": null,
    "errorLog": "第3次重试后仍失败：ManimError: ...",
    "createTime": "2025-01-01 12:00:00",
    "updateTime": "2025-01-01 12:10:00"
  }
}
```

> status 取值：0-处理中 / 1-成功 / 2-失败

### 5.5 模板作品保存/发布

- **路径**：`POST /api/v1/template/work/save`
- **场景**：成品预览页保存私密作品或发布公开作品

请求参数：

| 参数        | 类型     | 必填  | 说明             |
|:--------- |:------:|:---:|:-------------- |
| taskId    | int    | 是   | 渲染任务 ID        |
| workTitle | string | 否   | 作品标题           |
| workDesc  | string | 否   | 作品描述           |
| isPublic  | bool   | 否   | 是否公开（默认 false） |

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "workId": 10
  }
}
```

### 5.6 作品资源导出

- **路径**：`GET /api/v1/work/export`
- **场景**：导出 MP4/GIF/源码

请求参数：`workId`、`exportType`（mp4/gif/code）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "downloadUrl": "/download/work_10.mp4"
  }
}
```

---

## 六、AI 沙箱创作模块

| 接口      | 方法   | 路径                           | 鉴权     |
|:------- |:----:|:---------------------------- |:------:|
| AI 生成代码 | POST | /api/v1/ai/generate/code     | 🔒 需登录 |
| AI 修复代码 | POST | /api/v1/ai/fix/code          | 🔒 需登录 |
| 沙箱手动渲染  | POST | /api/v1/sandbox/render       | 🔒 需登录 |
| 版本历史查询  | GET  | /api/v1/sandbox/version/list | 🔒 需登录 |
| 沙箱草稿保存  | POST | /api/v1/sandbox/draft/save   | 🔒 需登录 |
| 作品发布提交  | POST | /api/v1/work/publish         | 🔒 需登录 |

### 6.1 AI 自然语言生成 Manim 代码

- **路径**：`POST /api/v1/ai/generate/code`

请求参数：`userPrompt`（自然语言需求）、`knowledgeId`（可选，关联知识点）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "manimCode": "from manim import *\nclass MyScene(Scene):\n    def construct(self):\n        ...",
    "description": "生成了一个冒泡排序的动画",
    "suggestedParams": { "speed": "normal", "arraySize": 10 }
  }
}
```

### 6.2 AI 代码智能修复

- **路径**：`POST /api/v1/ai/fix/code`

请求参数：`errorLog`（错误日志）、`oldCode`（当前代码）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "fixedCode": "from manim import *\nclass MyScene(Scene):\n    def construct(self):\n        ...",
    "fixNote": "修复了 Square 对象未定义的问题，将 Square() 替换为 Rectangle()"
  }
}
```

### 6.3 沙箱代码手动渲染

- **路径**：`POST /api/v1/sandbox/render`

请求参数：`manimCode`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "taskId": 43,
    "previewUrl": "/videos/preview_43.mp4",
    "errorLog": null
  }
}
```

### 6.4 沙箱版本历史记录查询

- **路径**：`GET /api/v1/sandbox/version/list`

请求参数：`workId`（草稿/作品 ID）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "id": 101,
      "version": 1,
      "manimCode": "from manim import *...",
      "note": "初始生成",
      "createTime": "2025-01-01 12:00:00"
    },
    {
      "id": 102,
      "version": 2,
      "manimCode": "from manim import *...",
      "note": "调整颜色参数",
      "createTime": "2025-01-01 12:30:00"
    }
  ]
}
```

### 6.5 沙箱草稿保存

- **路径**：`POST /api/v1/sandbox/draft/save`

请求参数：

| 参数         | 类型     | 必填  | 说明            |
|:---------- |:------:|:---:|:------------- |
| draftId    | int    | 否   | 已有草稿 ID（更新时传） |
| manimCode  | string | 是   | 当前 Manim 代码   |
| previewUrl | string | 否   | 预览视频 URL      |

> 每次保存会产生一个新版本（version 自增），支持版本回退。

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "draftId": 101,
    "version": 3
  }
}
```

### 6.6 作品发布配置提交

- **路径**：`POST /api/v1/work/publish`
- **场景**：从沙箱公开作品到画廊

请求参数：

| 参数         | 类型     | 必填  | 说明       |
|:---------- |:------:|:---:|:-------- |
| workTitle  | string | 是   | 作品标题     |
| workDesc   | string | 否   | 作品描述     |
| tagList    | string | 否   | 标签（逗号分隔） |
| isPublic   | bool   | 是   | 是否公开     |
| code       | string | 是   | Manim 源码 |
| previewUrl | string | 否   | 预览视频地址   |

响应：

```json
{
  "code": 200,
  "msg": "发布成功",
  "data": {
    "publishedWorkId": 10
  }
}
```

---

## 七、社区画廊模块

| 接口        | 方法   | 路径                         | 鉴权     |
|:--------- |:----:|:-------------------------- |:------:|
| 画廊列表/排行榜  | GET  | /api/v1/gallery/list       | 🔓 免登录 |
| 公开作品详情    | GET  | /api/v1/work/public/detail | 🔓 免登录 |
| 点赞/取消点赞   | POST | /api/v1/work/like          | 🔒 需登录 |
| 收藏/取消收藏   | POST | /api/v1/work/collect       | 🔒 需登录 |
| 评论列表      | GET  | /api/v1/work/comment/list  | 🔓 免登录 |
| 发布评论      | POST | /api/v1/work/comment/add   | 🔒 需登录 |
| Fork 二次创作 | POST | /api/v1/work/fork          | 🔒 需登录 |
| 创作者主页     | GET  | /api/v1/user/author/home   | 🔓 免登录 |
| 关注/取消关注   | POST | /api/v1/user/follow        | 🔒 需登录 |

### 7.1 获取画廊作品列表/排行榜

- **路径**：`GET /api/v1/gallery/list`

请求参数：

| 参数       | 类型     | 必填  | 默认     | 说明                                           |
|:-------- |:------:|:---:|:------:|:-------------------------------------------- |
| rankType | string | 否   | weekly | daily-日榜 / weekly-周榜 / monthly-月榜 / total-总榜 |
| category | string | 否   | -      | 分类筛选（按 tags 模糊匹配）                            |
| page     | int    | 否   | 1      | 页码                                           |
| size     | int    | 否   | 10     | 每页条数                                         |

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "workId": 1,
        "cover": "https://example.com/cover1.png",
        "title": "冒泡排序可视化",
        "authorName": "张三",
        "authorAvatar": "https://example.com/avatar.png",
        "likeCount": 256,
        "viewCount": 15230,
        "tags": "算法,排序"
      }
    ],
    "total": 1
  }
}
```

### 7.2 获取公开作品详情

- **路径**：`GET /api/v1/work/public/detail`
- **场景**：作品详情页渲染

请求参数：`workId`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "workId": 1,
    "title": "冒泡排序可视化",
    "description": "通过动画直观展示冒泡排序的完整过程",
    "videoPath": "/videos/work_1.mp4",
    "manimCode": "from manim import *...",
    "tags": "算法,排序",
    "authorInfo": {
      "userId": 1,
      "nickname": "张三",
      "avatar": "https://example.com/avatar.png"
    },
    "sourceWorkId": null,
    "viewCount": 15230,
    "likeCount": 256,
    "collectCount": 88,
    "forkCount": 15,
    "createTime": "2025-01-01 12:00:00"
  }
}
```

### 7.3 作品点赞/取消点赞

- **路径**：`POST /api/v1/work/like`

请求参数：`workId`、`isLike`（true-点赞 / false-取消点赞）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": null
}
```

### 7.4 作品收藏/取消收藏

- **路径**：`POST /api/v1/work/collect`

请求参数：`workId`、`isCollect`（true-收藏 / false-取消收藏）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": null
}
```

### 7.5 作品评论列表 & 发布评论

**获取评论列表**：`GET /api/v1/work/comment/list?workId=1`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": [
    {
      "id": 1,
      "workId": 1,
      "userId": 2,
      "nickname": "李四",
      "avatar": "https://example.com/avatar2.png",
      "content": "这个动画太直观了！",
      "replyToId": null,
      "createTime": "2025-01-02 14:00:00"
    },
    {
      "id": 2,
      "workId": 1,
      "userId": 1,
      "nickname": "张三",
      "avatar": "https://example.com/avatar.png",
      "content": "谢谢支持！",
      "replyToId": 1,
      "createTime": "2025-01-02 15:00:00"
    }
  ]
}
```

**发布评论**：`POST /api/v1/work/comment/add`

请求参数：

| 参数      | 类型     | 必填  | 说明             |
|:------- |:------:|:---:|:-------------- |
| workId  | int    | 是   | 作品 ID          |
| content | string | 是   | 评论内容           |
| replyId | int    | 否   | 回复目标评论 ID（楼中楼） |

响应：

```json
{
  "code": 200,
  "msg": "评论成功",
  "data": {
    "commentId": 3
  }
}
```

### 7.6 作品 Fork 二次创作

- **路径**：`POST /api/v1/work/fork`
- **场景**：复刻他人作品至个人沙箱

请求参数：`workId`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "workId": 11,
    "sourceCode": "from manim import *...",
    "sourceAuthor": "张三"
  }
}
```

### 7.7 获取创作者主页数据

- **路径**：`GET /api/v1/user/author/home`

请求参数：`authorId`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "authorInfo": {
      "userId": 1,
      "nickname": "张三",
      "avatar": "https://example.com/avatar.png",
      "intro": "热爱数学和编程"
    },
    "workCount": 15,
    "totalLikes": 892,
    "followerCount": 128,
    "workList": [
      {
        "workId": 1,
        "title": "冒泡排序可视化",
        "cover": "https://example.com/cover1.png",
        "viewCount": 15230,
        "likeCount": 256
      }
    ]
  }
}
```

### 7.8 关注/取消关注创作者

- **路径**：`POST /api/v1/user/follow`

请求参数：`authorId`、`isFollow`（true-关注 / false-取消关注）

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": null
}
```

---

## 八、个人中心模块

| 接口      | 方法  | 路径                          | 鉴权     |
|:------- |:---:|:--------------------------- |:------:|
| 个人中心首页  | GET | /api/v1/user/home/data      | 🔒 需登录 |
| 我的作品列表  | GET | /api/v1/user/work/list      | 🔒 需登录 |
| 我的收藏列表  | GET | /api/v1/user/collect/list   | 🔒 需登录 |
| 浏览历史记录  | GET | /api/v1/user/history/list   | 🔒 需登录 |
| 学习统计数据  | GET | /api/v1/user/study/stat     | 🔒 需登录 |
| 创作者数据统计 | GET | /api/v1/user/author/stat    | 🔒 需登录 |
| 更新个人资料  | PUT | /api/v1/user/profile/update | 🔒 需登录 |

### 8.1 获取个人中心首页数据

- **路径**：`GET /api/v1/user/home/data`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "userInfo": {
      "userId": 1,
      "nickname": "张三",
      "avatar": "https://example.com/avatar.png"
    },
    "workCount": 15,
    "collectCount": 28,
    "totalStudyMinutes": 360,
    "checkinDays": 12,
    "followerCount": 128,
    "followeeCount": 32
  }
}
```

### 8.2 获取我的作品列表

- **路径**：`GET /api/v1/user/work/list`

请求参数：`status`（0-草稿 / 1-已发布）、`page`、`size`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "workId": 1,
        "title": "冒泡排序可视化",
        "status": 1,
        "isPublic": 1,
        "viewCount": 15230,
        "likeCount": 256,
        "createTime": "2025-01-01 12:00:00"
      }
    ],
    "total": 15
  }
}
```

### 8.3 获取我的收藏列表

- **路径**：`GET /api/v1/user/collect/list`

请求参数：`type`（1-词条 / 2-作品 / 3-模板）、`page`、`size`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "targetType": 2,
        "targetId": 5,
        "title": "快速排序可视化",
        "authorName": "李四",
        "createTime": "2025-01-03 10:00:00"
      }
    ],
    "total": 28
  }
}
```

### 8.4 获取浏览历史记录

- **路径**：`GET /api/v1/user/history/list`

请求参数：`page`、`size`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "list": [
      {
        "id": 1,
        "targetType": 2,
        "targetId": 1,
        "title": "冒泡排序可视化",
        "createTime": "2025-01-05 18:30:00"
      }
    ],
    "total": 56
  }
}
```

### 8.5 获取个人学习统计数据

- **路径**：`GET /api/v1/user/study/stat`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "totalStudyMinutes": 360,
    "checkinDays": 12,
    "masteredEntries": 8,
    "dailyRecords": [
      { "date": "2025-01-05", "minutes": 30 },
      { "date": "2025-01-06", "minutes": 45 }
    ]
  }
}
```

### 8.6 获取创作者作品数据统计

- **路径**：`GET /api/v1/user/author/stat`

响应：

```json
{
  "code": 200,
  "msg": "操作成功",
  "data": {
    "totalViews": 45230,
    "totalLikes": 1892,
    "totalCollects": 568,
    "totalForks": 120,
    "workDetails": [
      {
        "workId": 1,
        "title": "冒泡排序可视化",
        "viewCount": 15230,
        "likeCount": 256,
        "collectCount": 88,
        "forkCount": 15
      }
    ]
  }
}
```

### 8.7 更新个人账号资料

- **路径**：`PUT /api/v1/user/profile/update`

请求参数：

| 参数       | 类型     | 必填  | 说明     |
|:-------- |:------:|:---:|:------ |
| nickname | string | 否   | 昵称     |
| avatar   | string | 否   | 头像 URL |
| intro    | string | 否   | 个人简介   |

> 支持部分更新：只传需要修改的字段即可。

响应：

```json
{
  "code": 200,
  "msg": "更新成功",
  "data": null
}
```

---

## 九、数据库实体关系图（文字版）

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

---

## 📌 优化说明（相对原版）

| 问题    | 原版              | 优化版                                |
|:----- |:--------------- |:---------------------------------- |
| 路径前缀  | 接口路径缺少统一前缀      | 全部补全为 `/api/v1/...`                |
| 鉴权标注  | 未告知哪些接口要登录      | 每张表格标注 🔓/🔒                       |
| 错误码体系 | 仅有 code/msg，无定义 | 新增完整错误码表                           |
| 分页规范  | page/size 散乱定义  | 集中规范默认值和上限，统一 `{list, total}` 结构   |
| 响应格式  | 仅文字描述 data 内字段  | 全部展示完整 `{code, msg, data}` JSON 示例 |
| 接口粒度  | 无明确区分           | 区分草稿保存 vs 作品发布流程                   |
| 实体关系  | 无说明             | 新增数据库关系图                           |
