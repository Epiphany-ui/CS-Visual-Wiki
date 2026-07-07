package com.manim.pojo;

/**
 * 全局接口统一返回封装
 *
 * @param <T> 业务数据类型
 */
public class Result<T> {

    /** 响应码：200-成功，500-业务失败 */
    private int code;

    /** 提示信息 */
    private String msg;

    /** 业务数据 */
    private T data;

    public Result() {
    }

    public Result(int code, String msg, T data) {
        this.code = code;
        this.msg = msg;
        this.data = data;
    }

    // ==================== 静态工厂方法 ====================

    /** 成功（无数据返回） */
    public static <T> Result<T> success() {
        return new Result<>(200, "操作成功", null);
    }

    /** 成功（带业务数据） */
    public static <T> Result<T> success(T data) {
        return new Result<>(200, "操作成功", data);
    }

    /** 成功（自定义 msg + data） */
    public static <T> Result<T> success(String msg, T data) {
        return new Result<>(200, msg, data);
    }

    /** 业务失败（默认 code=500） */
    public static <T> Result<T> fail(String msg) {
        return new Result<>(500, msg, null);
    }

    /** 业务失败（自定义 code + msg） */
    public static <T> Result<T> fail(int code, String msg) {
        return new Result<>(code, msg, null);
    }

    // ===== getters & setters =====

    public int getCode() {
        return code;
    }

    public void setCode(int code) {
        this.code = code;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public T getData() {
        return data;
    }

    public void setData(T data) {
        this.data = data;
    }
}
