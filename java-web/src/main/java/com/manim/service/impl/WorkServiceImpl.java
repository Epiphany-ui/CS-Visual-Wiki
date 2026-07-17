package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.dto.CarouselDTO;
import com.manim.dto.WorkListDTO;
import com.manim.mapper.*;
import com.manim.pojo.*;
import com.manim.exception.BusinessException;
import com.manim.service.WorkService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class WorkServiceImpl implements WorkService {

    @Autowired
    private WorkMapper workMapper;

    @Autowired
    private WorkLikeMapper workLikeMapper;

    @Autowired
    private UserCollectMapper userCollectMapper;

    @Autowired
    private SandboxDraftMapper sandboxDraftMapper;

    @Autowired
    private UserMapper userMapper;

    @Override
    public Work getById(Integer id) {
        return workMapper.selectById(id);
    }

    @Override
    public Work getPublicDetail(Integer workId) {
        Work work = workMapper.selectById(workId);
        if (work != null && work.getIsPublic() == 1) {
            work.setViewCount(work.getViewCount() == null ? 1 : work.getViewCount() + 1);
            workMapper.updateById(work);
        }
        return work;
    }

    @Override
    public List<Work> listByUser(Integer userId, Integer status, Integer page, Integer size) {
        QueryWrapper<Work> qw = new QueryWrapper<>();
        qw.eq("user_id", userId);
        if (status != null) qw.eq("status", status);
        qw.orderByDesc("create_time");
        qw.last("LIMIT " + ((page - 1) * size) + "," + size);
        return workMapper.selectList(qw);
    }

    @Override
    public List<Work> listGallery(String rankType, String sort, String category, Integer page, Integer size) {
        QueryWrapper<Work> qw = new QueryWrapper<>();
        qw.eq("is_public", 1).eq("status", 1);
        if (category != null && !category.isEmpty()) qw.like("tags", category);
        // 优先用 sort 参数（前端直接传），fallback 到 rankType
        if (sort != null && !sort.isEmpty()) {
            switch (sort) {
                case "time":  qw.orderByDesc("create_time"); break;
                case "likes": qw.orderByDesc("like_count"); break;
                case "views": qw.orderByDesc("view_count"); break;
                default:      qw.orderByDesc("create_time"); break;
            }
        } else if ("daily".equals(rankType) || "weekly".equals(rankType) || "monthly".equals(rankType)) {
            qw.orderByDesc("view_count");
        } else {
            qw.orderByDesc("like_count");
        }
        qw.last("LIMIT " + ((page - 1) * size) + "," + size);
        return workMapper.selectList(qw);
    }

    @Override
    public List<CarouselDTO> listCarousel() {
        QueryWrapper<Work> qw = new QueryWrapper<>();
        qw.eq("is_public", 1)
           .eq("status", 1)
           .orderByDesc("view_count")
           .last("LIMIT 6");
        List<Work> works = workMapper.selectList(qw);

        return works.stream().map(w -> {
            User author = userMapper.selectById(w.getUserId());
            return new CarouselDTO(
                    w.getId(),
                    w.getCover(),
                    w.getTitle(),
                    w.getViewCount(),
                    author != null ? author.getNickname() : "未知用户"
            );
        }).collect(java.util.stream.Collectors.toList());
    }

    @Override
    public List<Work> listHomeWorks(String type, Integer page, Integer size) {
        QueryWrapper<Work> qw = new QueryWrapper<>();
        qw.eq("is_public", 1).eq("status", 1);
        if ("featured".equals(type)) {
            qw.orderByDesc("like_count");
        } else {
            qw.orderByDesc("create_time");
        }
        qw.last("LIMIT " + ((page - 1) * size) + "," + size);
        return workMapper.selectList(qw);
    }

    @Override
    public List<WorkListDTO> listHomeWorksDTO(String type, Integer page, Integer size) {
        List<Work> works = listHomeWorks(type, page, size);
        java.time.format.DateTimeFormatter fmt = java.time.format.DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        return works.stream().map(w -> {
            User author = userMapper.selectById(w.getUserId());
            return new WorkListDTO(
                    w.getId(),
                    w.getUserId(),
                    w.getCover(),
                    w.getTitle(),
                    w.getDescription(),
                    author != null ? author.getNickname() : "未知用户",
                    author != null ? author.getAvatar() : null,
                    w.getLikeCount(),
                    w.getViewCount(),
                    w.getSourceWorkId(),
                    null, // sourceAuthorName
                    null, // sourceAuthorId
                    w.getForkCount(),
                    w.getVideoPath(),
                    w.getCreateTime() != null ? w.getCreateTime().format(fmt) : null
            );
        }).collect(java.util.stream.Collectors.toList());
    }

    @Override
    public int countHomeWorks(String type) {
        QueryWrapper<Work> qw = new QueryWrapper<>();
        qw.eq("is_public", 1).eq("status", 1);
        return workMapper.selectCount(qw).intValue();
    }

    @Override
    public Integer saveWork(Work work) {
        workMapper.insert(work);
        return work.getId();
    }

    @Override
    public void updateWork(Work work) {
        workMapper.updateById(work);
    }

    @Override
    public void incrementViewCount(Integer workId) {
        Work work = workMapper.selectById(workId);
        if (work != null) {
            work.setViewCount(work.getViewCount() == null ? 1 : work.getViewCount() + 1);
            workMapper.updateById(work);
        }
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean toggleLike(Integer workId, Integer userId, boolean isLike) {
        Work work = workMapper.selectById(workId);
        if (work == null) return false;

        QueryWrapper<WorkLike> qw = new QueryWrapper<>();
        qw.eq("work_id", workId).eq("user_id", userId);
        WorkLike existing = workLikeMapper.selectOne(qw);

        if (isLike && existing == null) {
            WorkLike like = new WorkLike();
            like.setWorkId(workId);
            like.setUserId(userId);
            workLikeMapper.insert(like);
            work.setLikeCount(work.getLikeCount() == null ? 1 : work.getLikeCount() + 1);
        } else if (!isLike && existing != null) {
            workLikeMapper.deleteById(existing.getId());
            work.setLikeCount(Math.max(0, (work.getLikeCount() == null ? 0 : work.getLikeCount()) - 1));
        }
        workMapper.updateById(work);
        return true;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public boolean toggleCollect(Integer workId, Integer userId, boolean isCollect) {
        Work work = workMapper.selectById(workId);
        if (work == null) return false;

        com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<com.manim.pojo.UserCollect> qw =
                new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<>();
        qw.eq("user_id", userId).eq("target_type", 2).eq("target_id", workId);
        com.manim.pojo.UserCollect existing = userCollectMapper.selectOne(qw);

        if (isCollect && existing == null) {
            com.manim.pojo.UserCollect collect = new com.manim.pojo.UserCollect();
            collect.setUserId(userId);
            collect.setTargetType(2);
            collect.setTargetId(workId);
            userCollectMapper.insert(collect);
            work.setCollectCount(work.getCollectCount() == null ? 1 : work.getCollectCount() + 1);
        } else if (!isCollect && existing != null) {
            userCollectMapper.deleteById(existing.getId());
            work.setCollectCount(Math.max(0, (work.getCollectCount() == null ? 0 : work.getCollectCount()) - 1));
        }
        workMapper.updateById(work);
        return true;
    }

    @Override
    @Transactional(rollbackFor = Exception.class)
    public Integer forkWork(Integer workId, Integer userId) {
        Work source = workMapper.selectById(workId);
        if (source == null) return null;

        // 创建新作品副本
        Work fork = new Work();
        fork.setUserId(userId);
        fork.setTitle(source.getTitle() + " (Fork)");
        fork.setManimCode(source.getManimCode());
        fork.setSourceWorkId(workId);
        fork.setStatus(0); // 草稿
        fork.setIsPublic(0);
        workMapper.insert(fork);

        // 原作品 fork 计数+1
        source.setForkCount(source.getForkCount() == null ? 1 : source.getForkCount() + 1);
        workMapper.updateById(source);

        // 创建沙箱草稿
        SandboxDraft draft = new SandboxDraft();
        draft.setUserId(userId);
        draft.setWorkId(fork.getId());
        draft.setManimCode(source.getManimCode());
        draft.setVersion(1);
        sandboxDraftMapper.insert(draft);

        return fork.getId();
    }

    @Override
    public void deleteWork(Integer workId, Integer userId) {
        Work work = workMapper.selectById(workId);
        if (work == null) throw new BusinessException("作品不存在");
        if (!work.getUserId().equals(userId)) throw new BusinessException("无权删除他人作品");
        workMapper.deleteById(workId);
    }

    @Override
    public void toggleVisibility(Integer workId, Integer userId) {
        Work work = workMapper.selectById(workId);
        if (work == null) throw new BusinessException("作品不存在");
        if (!work.getUserId().equals(userId)) throw new BusinessException("无权操作他人作品");
        work.setIsPublic(work.getIsPublic() == 1 ? 0 : 1);
        workMapper.updateById(work);
    }

    @Override
    public void updateWorkFields(Integer workId, Integer userId, String title, String description) {
        Work work = workMapper.selectById(workId);
        if (work == null) throw new BusinessException("作品不存在");
        if (!work.getUserId().equals(userId)) throw new BusinessException("无权修改他人作品");
        if (title != null && !title.trim().isEmpty()) work.setTitle(title.trim());
        if (description != null) work.setDescription(description.trim());
        workMapper.updateById(work);
    }
}
