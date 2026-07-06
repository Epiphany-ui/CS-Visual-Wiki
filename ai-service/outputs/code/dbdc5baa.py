from manim import *
import numpy as np
import math

np.random.seed(42)

class CentralLimitTheorem(Scene):
    def construct(self):
        # ========== 预计算直方图数据 ==========
        N_SAMPLES = 8000
        N_BINS = 50
        x_min, x_max = -4.0, 4.0
        bin_edges = np.linspace(x_min, x_max, N_BINS + 1)
        bin_width = bin_edges[1] - bin_edges[0]
        bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2.0

        # 存储每个 n 的直方图高度（密度值）
        hist_data = {}
        for n in range(1, 31):
            samples = []
            for _ in range(N_SAMPLES):
                s = sum(np.random.random() for _ in range(n))
                z = (s - n * 0.5) / math.sqrt(n / 12.0)
                samples.append(z)
            hist, _ = np.histogram(samples, bins=bin_edges, density=True)
            hist_data[n] = hist

        # ========== 布局参数 ==========
        ax_width = 5.2
        ax_height = 3.5
        left_ax_center = np.array([-3.4, 0.0, 0.0])
        right_ax_center = np.array([3.4, 0.0, 0.0])

        # ========== 左侧坐标轴 ==========
        left_axes = Axes(
            x_range=[x_min, x_max, 1.0],
            y_range=[0.0, 0.50, 0.1],
            x_length=ax_width,
            y_length=ax_height,
            axis_config={
                "include_numbers": True,
                "font_size": 22,
                "decimal_number_config": {"num_decimal_places": 1},
            },
            y_axis_config={"label_direction": LEFT},
            tips=False,
        ).move_to(left_ax_center)

        left_x_label = MathTex("x", font_size=24).next_to(left_axes.x_axis.get_end(), DOWN)
        left_y_label = MathTex("f(x)", font_size=24).next_to(left_axes.y_axis.get_top(), LEFT)

        # ========== 右侧坐标轴 ==========
        right_axes = Axes(
            x_range=[x_min, x_max, 1.0],
            y_range=[0.0, 0.50, 0.1],
            x_length=ax_width,
            y_length=ax_height,
            axis_config={
                "include_numbers": True,
                "font_size": 22,
                "decimal_number_config": {"num_decimal_places": 1},
            },
            y_axis_config={"label_direction": LEFT},
            tips=False,
        ).move_to(right_ax_center)

        right_x_label = MathTex("x", font_size=24).next_to(right_axes.x_axis.get_end(), DOWN)
        right_y_label = MathTex("\\phi(x)", font_size=24).next_to(right_axes.y_axis.get_top(), LEFT)

        # ========== 直方图矩形（左侧） ==========
        bars = VGroup()
        bar_center_xs = []
        for i in range(N_BINS):
            xl = bin_edges[i]
            xr = bin_edges[i+1]
            p_left = left_axes.c2p(xl, 0)
            p_right = left_axes.c2p(xr, 0)
            w = p_right[0] - p_left[0]
            cx = (p_left[0] + p_right[0]) / 2.0
            bar_center_xs.append(cx)

            rect = Rectangle(
                width=w,
                height=0.001,
                fill_color=BLUE,
                fill_opacity=0.55,
                stroke_color=BLUE_D,
                stroke_width=0.5,
            )
            # 底部对齐到坐标轴 x 轴
            rect.move_to([cx, left_axes.c2p(0, 0)[1], 0], aligned_edge=DOWN)
            bars.add(rect)

        # ========== 标准正态曲线 ==========
        normal_pdf = lambda x: math.exp(-x*x/2.0) / math.sqrt(2*math.pi)

        normal_curve = right_axes.plot(
            normal_pdf,
            x_range=[x_min, x_max],
            color=RED,
            stroke_width=3,
        )

        ref_curve = left_axes.plot(
            normal_pdf,
            x_range=[x_min, x_max],
            color=GREY,
            stroke_width=2,
            stroke_opacity=0.5,  # 稍微明显一点
        )

        # ========== 文本元素 ==========
        title = Text(
            "中心极限定理   (Central Limit Theorem)",
            font_size=30,
            color=WHITE,
        ).to_edge(UP, buff=0.35)

        # n 值显示（使用 Text，避免 become 重建）
        n_label = Text("n = 1", font_size=36, color=YELLOW)
        n_label.next_to(title, DOWN, buff=0.25)

        formula = MathTex(
            r"\phi(x) = \frac{1}{\sqrt{2\pi}} e^{-x^2/2}",
            font_size=28,
            color=RED,
        ).to_edge(DOWN, buff=0.35)

        left_label = Text("样本和的分布（标准化）", font_size=20, color=BLUE_D)
        left_label.next_to(left_axes, DOWN, buff=0.15)
        right_label = Text("标准正态分布 N(0,1)", font_size=20, color=RED)
        right_label.next_to(right_axes, DOWN, buff=0.15)

        # ========== 值追踪器 ==========
        n_tracker = ValueTracker(1.0)

        # ========== 更新函数 ==========
        def update_bars(mob, dt):
            n_val = n_tracker.get_value()
            n_clamped = max(1.0, min(30.0, n_val))
            n_floor = int(math.floor(n_clamped))
            n_ceil = min(30, n_floor + 1)
            frac = n_clamped - n_floor

            if n_floor >= 30:
                hist_curr = hist_data[30]
            elif n_floor < 1:
                hist_curr = hist_data[1]
            else:
                h_floor = hist_data[n_floor]
                h_ceil = hist_data[n_ceil]
                hist_curr = (1 - frac) * h_floor + frac * h_ceil

            for i, rect in enumerate(bars):
                h_val = hist_curr[i]
                if h_val < 1e-6:
                    h_val = 0.0
                # 场景坐标高度
                p_bottom = left_axes.c2p(0, 0)
                p_top = left_axes.c2p(0, h_val)
                scene_height = p_top[1] - p_bottom[1]
                if scene_height < 0.001:
                    scene_height = 0.001
                    rect.set_opacity(0.0)
                else:
                    rect.set_opacity(0.55)
                # 仅调整高度，保持底部不变
                rect.stretch_to_fit_height(scene_height, about_edge=DOWN)

        def update_n_label(mob, dt):
            n_val = n_tracker.get_value()
            n_show = round(n_val)
            mob.text = f"n = {n_show}"
            # 重新对齐，防止文字宽度变化导致偏移
            mob.next_to(title, DOWN, buff=0.25)

        bars.add_updater(update_bars)
        n_label.add_updater(update_n_label)

        # ========== 场景组装 ==========
        self.add(
            left_axes, left_x_label, left_y_label,
            right_axes, right_x_label, right_y_label,
            bars, ref_curve, normal_curve,
            title, n_label, formula,
            left_label, right_label,
        )

        # ========== 动画 ==========
        self.play(
            n_tracker.animate.set_value(30.0),
            run_time=23.0,
            rate_func=linear,
        )
        self.wait(2.0)