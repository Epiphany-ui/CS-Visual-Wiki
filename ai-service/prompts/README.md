# Prompt 模板目录

存放 AI 生成 / 修复相关的 System Prompt 模板文件，使用 Jinja2 模板语法，支持变量插值和热重载。

## 模板文件

| 文件 | 用途 | 变量 |
|------|------|------|
| `code_generation.j2` | Manim 代码生成 System Prompt | `max_animation_duration`, `references` |
| `code_fix.j2` | Manim 代码修复 System Prompt | `error_message` |

## 设计原则

- **核心引擎零修改**：`ai_engine.py` 通过 `prompt_service` 加载 Prompt，不直接硬编码
- **热重载**：修改 Prompt 文件后，调用 `POST /api/prompts/reload` 或在下次渲染时自动检测更新，无需重启服务
- **回退机制**：Prompt 文件缺失时，`prompt_service` 自动使用内置默认 Prompt，保证向后兼容

## 如何迭代 Prompt

1. 直接编辑 `.j2` 模板文件，使用 `{{ variable_name }}` 语法引用变量
2. 热重载使修改生效：
   ```bash
   curl -X POST http://localhost:8000/api/prompts/reload
   ```
3. 预览渲染结果（用于调试）：
   ```bash
   curl http://localhost:8000/api/prompts/code_generation
   ```

## API 接口

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/prompts/list` | 列出所有 Prompt 模板 |
| GET | `/api/prompts/{name}` | 预览指定 Prompt 模板内容 |
| POST | `/api/prompts/reload` | 热重载所有 Prompt 模板 |

## 添加新 Prompt

1. 在此目录新建 `.j2` 模板文件
2. 在 `services/prompt_service.py` 的 `_get_default()` 方法中添加对应的回退 Prompt（可选）
3. 在代码中调用 `prompt_service.render("模板名", **变量)` 获取 Prompt 文本
4. 调用 `POST /api/prompts/reload` 使新模板生效
