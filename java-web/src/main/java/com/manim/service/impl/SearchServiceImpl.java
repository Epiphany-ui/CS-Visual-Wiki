package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.dto.KnowledgeSearchDTO;
import com.manim.dto.TemplateSearchDTO;
import com.manim.dto.UserSearchDTO;
import com.manim.dto.WorkSearchDTO;
import com.manim.mapper.KnowledgeEntryMapper;
import com.manim.mapper.TemplateMapper;
import com.manim.mapper.UserMapper;
import com.manim.mapper.WorkMapper;
import com.manim.pojo.KnowledgeEntry;
import com.manim.pojo.Template;
import com.manim.pojo.User;
import com.manim.pojo.Work;
import com.manim.service.SearchService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
public class SearchServiceImpl implements SearchService {

    @Autowired
    private KnowledgeEntryMapper knowledgeEntryMapper;

    @Autowired
    private WorkMapper workMapper;

    @Autowired
    private TemplateMapper templateMapper;

    @Autowired
    private UserMapper userMapper;

    @Override
    public Map<String, Object> searchAll(String keyword, Integer page, Integer size) {
        if (keyword == null || keyword.trim().isEmpty()) {
            Map<String, Object> empty = new HashMap<>();
            empty.put("knowledgeList", Collections.emptyList());
            empty.put("workList", Collections.emptyList());
            empty.put("templateList", Collections.emptyList());
            empty.put("userList", Collections.emptyList());
            return empty;
        }

        String kw = "%" + keyword.trim() + "%";
        int limit = 5; // 搜索框快捷展示，每类固定 5 条

        // 1. 搜索知识词条
        List<KnowledgeSearchDTO> knowledgeList = knowledgeEntryMapper.selectList(
                new QueryWrapper<KnowledgeEntry>()
                        .like("title", kw)
                        .or().like("summary", kw)
                        .orderByDesc("view_count")
                        .last("LIMIT " + limit)
        ).stream().map(e -> new KnowledgeSearchDTO(
                e.getId(), e.getTitle(), e.getSummary(), e.getDifficulty()
        )).collect(Collectors.toList());

        // 2. 搜索公开作品
        List<WorkSearchDTO> workList = workMapper.selectList(
                new QueryWrapper<Work>()
                        .eq("is_public", 1).eq("status", 1)
                        .and(w -> w.like("title", kw).or().like("description", kw))
                        .orderByDesc("like_count")
                        .last("LIMIT " + limit)
        ).stream().map(w -> {
            User author = userMapper.selectById(w.getUserId());
            return new WorkSearchDTO(
                    w.getId(), w.getTitle(), w.getCover(),
                    author != null ? author.getNickname() : "未知用户",
                    w.getLikeCount()
            );
        }).collect(Collectors.toList());

        // 3. 搜索模板
        List<TemplateSearchDTO> templateList = templateMapper.selectList(
                new QueryWrapper<Template>()
                        .like("name", kw)
                        .or().like("description", kw)
                        .orderByDesc("use_count")
                        .last("LIMIT " + limit)
        ).stream().map(t -> new TemplateSearchDTO(
                t.getId(), t.getName(), t.getDescription(), t.getUseCount()
        )).collect(Collectors.toList());

        // 4. 搜索用户
        List<UserSearchDTO> userList = userMapper.selectList(
                new QueryWrapper<User>()
                        .like("username", kw)
                        .or().like("nickname", kw)
                        .last("LIMIT " + limit)
        ).stream().map(u -> new UserSearchDTO(
                u.getId(), u.getUsername(), u.getNickname(), u.getAvatar()
        )).collect(Collectors.toList());

        Map<String, Object> result = new LinkedHashMap<>();
        result.put("knowledgeList", knowledgeList);
        result.put("workList", workList);
        result.put("templateList", templateList);
        result.put("userList", userList);
        return result;
    }
}
