package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.WorkCommentMapper;
import com.manim.pojo.WorkComment;
import com.manim.service.WorkCommentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class WorkCommentServiceImpl implements WorkCommentService {

    @Autowired
    private WorkCommentMapper workCommentMapper;

    @Override
    public List<WorkComment> listByWorkId(Integer workId) {
        return workCommentMapper.selectList(
                new QueryWrapper<WorkComment>()
                        .eq("work_id", workId)
                        .orderByAsc("create_time"));
    }

    @Override
    public Integer addComment(Integer workId, Integer userId, String content, Integer replyToId) {
        WorkComment comment = new WorkComment();
        comment.setWorkId(workId);
        comment.setUserId(userId);
        comment.setContent(content);
        comment.setReplyToId(replyToId);
        workCommentMapper.insert(comment);
        return comment.getId();
    }
}
