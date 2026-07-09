package com.manim.controller;

import com.manim.dto.CarouselDTO;
import com.manim.dto.CategoryDTO;
import com.manim.dto.WorkListDTO;
import com.manim.pojo.Result;
import com.manim.service.KnowledgeCategoryService;
import com.manim.service.WorkService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 首页模块接口
 * <p>对应接口文档：二、首页模块</p>
 */
@Tag(name = "首页模块接口")
@RestController
@RequestMapping("/api/v1/home")
public class HomeController {

    @Autowired
    private WorkService workService;

    @Autowired
    private KnowledgeCategoryService knowledgeCategoryService;

    @Operation(summary = "获取首页热门轮播动画")
    @GetMapping("/carousel")
    public Result<List<CarouselDTO>> getCarousel() {
        List<CarouselDTO> list = workService.listCarousel();
        return Result.success(list);
    }

    @Operation(summary = "获取首页知识点分类列表")
    @GetMapping("/category")
    public Result<List<CategoryDTO>> getCategory() {
        List<CategoryDTO> list = knowledgeCategoryService.listWithEntryCount();
        return Result.success(list);
    }

    @Operation(summary = "获取首页精选/最新作品列表")
    @GetMapping("/work/list")
    public Result<Map<String, Object>> getWorkList(
            @RequestParam(value = "type", defaultValue = "latest") String type,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {
        List<WorkListDTO> list = workService.listHomeWorksDTO(type, page, size);
        int total = workService.countHomeWorks(type);
        Map<String, Object> data = new HashMap<>();
        data.put("list", list);
        data.put("total", total);
        return Result.success(data);
    }
}
