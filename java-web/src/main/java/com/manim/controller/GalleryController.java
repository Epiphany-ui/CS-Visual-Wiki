package com.manim.controller;

import com.manim.dto.WorkListDTO;
import com.manim.pojo.Result;
import com.manim.pojo.Work;
import com.manim.service.WorkService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 社区画廊模块接口
 * <p>对应接口文档：7.1 画廊作品列表/排行榜</p>
 */
@Tag(name = "社区画廊接口")
@RestController
@RequestMapping("/api/v1/gallery")
public class GalleryController {

    @Autowired
    private WorkService workService;

    @Operation(summary = "获取画廊作品列表/排行榜")
    @GetMapping("/list")
    public Result<Map<String, Object>> getGalleryList(
            @RequestParam(value = "rankType", defaultValue = "weekly") String rankType,
            @RequestParam(value = "category", required = false) String category,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {

        List<Work> works = workService.listGallery(rankType, category, page, size);
        List<WorkListDTO> list = works.stream().map(w ->
                new WorkListDTO(w.getId(), w.getCover(), w.getTitle(), null,
                        w.getLikeCount(), w.getViewCount(), null)
        ).collect(Collectors.toList());

        Map<String, Object> data = new HashMap<>();
        data.put("list", list);
        data.put("total", list.size());
        return Result.success(data);
    }
}
