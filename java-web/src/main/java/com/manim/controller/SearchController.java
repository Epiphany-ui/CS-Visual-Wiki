package com.manim.controller;

import com.manim.pojo.Result;
import com.manim.service.SearchService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * 全局搜索模块接口
 * <p>对应接口文档：三、搜索模块</p>
 */
@Tag(name = "全局搜索接口")
@RestController
@RequestMapping("/api/v1/search")
public class SearchController {

    @Autowired
    private SearchService searchService;

    @Operation(summary = "全局统一搜索（知识点/作品/模板/用户）")
    @GetMapping("/all")
    public Result<Map<String, Object>> searchAll(
            @RequestParam("keyword") String keyword,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {
        Map<String, Object> data = searchService.searchAll(keyword, page, size);
        return Result.success(data);
    }
}
