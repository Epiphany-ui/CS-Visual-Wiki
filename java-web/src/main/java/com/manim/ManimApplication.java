package com.manim;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

@SpringBootApplication
@EnableAsync
public class ManimApplication {

    public static void main(String[] args) {
        SpringApplication.run(ManimApplication.class, args);
    }
}
