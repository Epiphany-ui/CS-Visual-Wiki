package com.manim.service;

import com.manim.pojo.SandboxDraft;

import java.util.List;

/**
 * 沙箱草稿（版本历史）业务接口
 */
public interface SandboxDraftService {

    Integer saveDraft(Integer userId, Integer workId, String manimCode, String previewUrl);

    List<SandboxDraft> getVersionList(Integer workId, Integer userId);

    SandboxDraft getById(Integer id);
}
