package com.manim.utils;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.MalformedJwtException;
import io.jsonwebtoken.UnsupportedJwtException;
import io.jsonwebtoken.security.Keys;
import io.jsonwebtoken.security.SecurityException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Component;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.util.Date;

/**
 * JWT 令牌工具类
 * <p>
 * 提供令牌的生成、解析与校验功能。
 * 密钥和过期时间从 application.yml 中读取。
 * </p>
 */
@Component
public class JwtUtil {

    private static final Logger log = LoggerFactory.getLogger(JwtUtil.class);

    private final SecretKey secretKey;
    private final long expiration;

    /**
     * 构造器注入配置值
     *
     * @param secret     JWT 签名密钥字符串
     * @param expiration 令牌过期时间（毫秒）
     */
    public JwtUtil(@Value("${jwt.secret}") String secret,
                   @Value("${jwt.expiration}") long expiration) {
        // 将密钥字符串转为 HMAC-SHA 算法的 SecretKey
        this.secretKey = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.expiration = expiration;
    }

    /**
     * 生成 JWT 令牌
     *
     * @param userId 用户标识（用户名或ID）
     * @return JWT 字符串
     */
    public String generateToken(String userId) {
        Date now = new Date();
        Date expiryDate = new Date(now.getTime() + expiration);

        return Jwts.builder()
                .subject(userId)
                .issuedAt(now)
                .expiration(expiryDate)
                .signWith(secretKey)
                .compact();
    }

    /**
     * 从令牌中解析 Claims（包含校验签名和有效期）
     *
     * @param token JWT 字符串
     * @return 解析成功的 Claims；失败返回 null
     */
    public Claims parseToken(String token) {
        try {
            return Jwts.parser()
                    .verifyWith(secretKey)
                    .build()
                    .parseSignedClaims(token)
                    .getPayload();
        } catch (ExpiredJwtException e) {
            log.warn("JWT 已过期: {}", e.getMessage());
        } catch (SecurityException | MalformedJwtException e) {
            log.warn("JWT 签名校验失败: {}", e.getMessage());
        } catch (UnsupportedJwtException e) {
            log.warn("不支持的 JWT 格式: {}", e.getMessage());
        } catch (IllegalArgumentException e) {
            log.warn("JWT 参数异常: {}", e.getMessage());
        }
        return null;
    }

    /**
     * 校验令牌是否有效
     *
     * @param token JWT 字符串
     * @return true 有效，false 无效/过期
     */
    public boolean validateToken(String token) {
        return parseToken(token) != null;
    }

    /**
     * 从令牌中获取用户标识
     *
     * @param token JWT 字符串
     * @return 用户 ID；解析失败返回 null
     */
    public String getUserIdFromToken(String token) {
        Claims claims = parseToken(token);
        return claims != null ? claims.getSubject() : null;
    }
}
