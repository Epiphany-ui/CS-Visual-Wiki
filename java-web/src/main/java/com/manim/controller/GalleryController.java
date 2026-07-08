package com.manim.controller;

import com.manim.pojo.Result;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.web.bind.annotation.*;

/**
 * 社区画廊模块接口
 * <p>对应接口文档：7.1 画廊作品列表/排行榜</p>
 */
@Tag(name = "社区画廊接口")
@RestController
@RequestMapping("/api/v1/gallery")
public class GalleryController {

    @Operation(summary = "获取画廊作品列表/排行榜")
    @GetMapping("/list")
    public Result<?> getGalleryList(@RequestParam(value = "rankType", defaultValue = "weekly") String rankType,
                                     @RequestParam(value = "category", required = false) String category,
                                     @RequestParam(value = "page", defaultValue = "1") Integer page,
                                     @RequestParam(value = "size", defaultValue = "10") Integer size) {
        // TODO: 实现画廊列表查询
        return Result.success("操作成功");
    }
}
