# CS-Visual-Learn Java Spring Boot Dockerfile
# 多阶段构建：Maven 编译 → JRE 运行

# ==== 构建阶段 ====
FROM maven:3.9-eclipse-temurin-8 AS build
WORKDIR /app

# 先复制 pom.xml 单独下载依赖（利用缓存）
COPY java-web/pom.xml .
RUN mvn dependency:go-offline -B || true

# 复制源码并编译
COPY java-web/src ./src
RUN mvn package -DskipTests -B

# ==== 运行阶段 ====
FROM eclipse-temurin:8-jre
WORKDIR /app

# 从构建阶段复制 JAR
COPY --from=build /app/target/*.jar app.jar

# 暴露端口
EXPOSE 8080

# 启动（支持外部参数覆盖）
ENTRYPOINT ["java", "-jar", "app.jar"]
