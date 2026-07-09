package com.manim.service;

import com.manim.pojo.WorkComment;

import java.util.List;

/**
 * 作品评论业务接口
 */
public interface WorkCommentService {

    List<WorkComment> listByWorkId(Integer workId);

    Integer addComment(Integer workId, Integer userId, String content, Integer replyToId);
}
