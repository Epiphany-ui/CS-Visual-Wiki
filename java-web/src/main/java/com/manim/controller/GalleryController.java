package com.manim.controller;

import com.manim.dto.WorkListDTO;
import com.manim.pojo.Result;
import com.manim.pojo.User;
import com.manim.pojo.Work;
import com.manim.service.UserService;
import com.manim.service.WorkService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Tag(name = "社区画廊接口")
@RestController
@RequestMapping("/api/v1/gallery")
public class GalleryController {

    @Autowired
    private WorkService workService;

    @Autowired
    private UserService userService;

    @Operation(summary = "获取画廊作品列表/排行榜")
    @GetMapping("/list")
    public Result<Map<String, Object>> getGalleryList(
            @RequestParam(value = "rankType", defaultValue = "weekly") String rankType,
            @RequestParam(value = "sort", required = false) String sort,
            @RequestParam(value = "category", required = false) String category,
            @RequestParam(value = "page", defaultValue = "1") Integer page,
            @RequestParam(value = "size", defaultValue = "10") Integer size) {

        List<Work> works = workService.listGallery(rankType, sort, category, page, size);
        List<WorkListDTO> list = works.stream().map(w -> {
            User author = userService.getById(w.getUserId());
            String authorName = author != null ?
                (author.getNickname() != null ? author.getNickname() : author.getUsername()) :
                "匿名用户";
            String authorAvatar = author != null ? author.getAvatar() : null;
            String createTime = w.getCreateTime() != null ? w.getCreateTime().toString() : null;
            // Fork 来源信息
            String sourceAuthorName = null;
            Integer sourceAuthorId = null;
            if (w.getSourceWorkId() != null) {
                Work sourceWork = workService.getById(w.getSourceWorkId());
                if (sourceWork != null) {
                    User sourceAuthor = userService.getById(sourceWork.getUserId());
                    if (sourceAuthor != null) {
                        sourceAuthorName = sourceAuthor.getNickname() != null ? sourceAuthor.getNickname() : sourceAuthor.getUsername();
                        sourceAuthorId = sourceAuthor.getId();
                    }
                }
            }
            return new WorkListDTO(w.getId(), w.getUserId(), w.getCover(), w.getTitle(),
                    w.getDescription(), authorName, authorAvatar,
                    w.getLikeCount(), w.getViewCount(),
                    w.getSourceWorkId(), sourceAuthorName, sourceAuthorId,
                    w.getForkCount(), w.getVideoPath(), createTime);
        }).collect(Collectors.toList());

        Map<String, Object> data = new HashMap<>();
        data.put("list", list);
        data.put("total", list.size());
        return Result.success(data);
    }
}
