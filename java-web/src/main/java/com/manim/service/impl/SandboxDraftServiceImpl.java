package com.manim.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import com.manim.mapper.SandboxDraftMapper;
import com.manim.pojo.SandboxDraft;
import com.manim.service.SandboxDraftService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class SandboxDraftServiceImpl implements SandboxDraftService {

    @Autowired
    private SandboxDraftMapper sandboxDraftMapper;

    @Override
    public Integer saveDraft(Integer userId, Integer workId, String manimCode, String previewUrl) {
        // 获取当前最大版本号
        QueryWrapper<SandboxDraft> qw = new QueryWrapper<>();
        qw.eq("user_id", userId);
        if (workId != null) qw.eq("work_id", workId);
        qw.orderByDesc("version").last("LIMIT 1");
        SandboxDraft latest = sandboxDraftMapper.selectOne(qw);
        int newVersion = (latest == null) ? 1 : latest.getVersion() + 1;

        SandboxDraft draft = new SandboxDraft();
        draft.setUserId(userId);
        draft.setWorkId(workId);
        draft.setManimCode(manimCode);
        draft.setPreviewUrl(previewUrl);
        draft.setVersion(newVersion);
        sandboxDraftMapper.insert(draft);
        return draft.getId();
    }

    @Override
    public List<SandboxDraft> getVersionList(Integer workId, Integer userId) {
        QueryWrapper<SandboxDraft> qw = new QueryWrapper<>();
        qw.eq("user_id", userId);
        if (workId != null) qw.eq("work_id", workId);
        qw.orderByDesc("version");
        return sandboxDraftMapper.selectList(qw);
    }

    @Override
    public SandboxDraft getById(Integer id) {
        return sandboxDraftMapper.selectById(id);
    }
}
