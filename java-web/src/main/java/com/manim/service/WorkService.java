package com.manim.service;

import com.manim.dto.CarouselDTO;
import com.manim.dto.WorkListDTO;
import com.manim.pojo.Work;

import java.util.List;

/**
 * 作品业务接口
 */
public interface WorkService {

    Work getById(Integer id);

    Work getPublicDetail(Integer workId);

    List<Work> listByUser(Integer userId, Integer status, Integer page, Integer size);

    List<Work> listGallery(String rankType, String sort, String category, Integer page, Integer size);

    List<Work> listHomeWorks(String type, Integer page, Integer size);

    /** 获取首页轮播作品（取播放量前 6 的公开作品） */
    List<CarouselDTO> listCarousel();

    /** 获取首页精选/最新作品列表 DTO（含作者名） */
    List<WorkListDTO> listHomeWorksDTO(String type, Integer page, Integer size);

    /** 统计首页作品总数 */
    int countHomeWorks(String type);

    Integer saveWork(Work work);

    void updateWork(Work work);

    void incrementViewCount(Integer workId);

    // 点赞
    boolean toggleLike(Integer workId, Integer userId, boolean isLike);

    // 收藏
    boolean toggleCollect(Integer workId, Integer userId, boolean isCollect);

    // Fork
    Integer forkWork(Integer workId, Integer userId);

    // 删除作品（所有者校验）
    void deleteWork(Integer workId, Integer userId);

    // 切换公开/私有
    void toggleVisibility(Integer workId, Integer userId);

    // 更新标题和描述（所有者校验）
    void updateWorkFields(Integer workId, Integer userId, String title, String description);
}
