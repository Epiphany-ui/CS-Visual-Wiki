package com.manim.controller;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;

/**
 * 页面跳转控制器（返回 Thymeleaf 页面名称）
 */
@Tag(name = "页面跳转接口")
@Controller
public class PageController {

    @Operation(summary = "首页（需求输入页面）")
    @GetMapping("/")
    public String index() {
        return "index";
    }

    @Operation(summary = "任务列表页")
    @GetMapping("/tasks")
    public String taskList() {
        return "task-list";
    }

    @Operation(summary = "任务详情页")
    @GetMapping("/task/{id}")
    public String taskDetail(@PathVariable Long id) {
        return "task-detail";
    }
}
