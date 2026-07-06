from manim import *
import numpy as np

class GradientDescentVisualization(Scene):
    def construct(self):
        # ---------- 函数与梯度定义 ----------
        def f(x, y):
            return x**2 + 2 * y**2

        def grad_f(x, y):
            # 梯度向量
            return np.array([2 * x, 4 * y])

        # ---------- 参数设置 ----------
        init_point = np.array([2.5, 2.0])              # 起始点 (x, y)
        alpha = 0.1                                    # 步长
        num_steps = 120                                 # 离散步数
        trajectory_points = [init_point]
        current = init_point.copy()
        for _ in range(num_steps):
            g = grad_f(current[0], current[1])
            current = current - alpha * g
            trajectory_points.append(current)

        # 插值函数：根据 t (0 ~ num_steps) 返回路径上的点
        def interpolate(t):
            t_clamped = np.clip(t, 0, num_steps)
            idx = int(t_clamped)
            frac = t_clamped - idx
            if idx >= num_steps:
                return np.array([*trajectory_points[-1], 0])
            else:
                p0 = np.array([*trajectory_points[idx], 0])
                p1 = np.array([*trajectory_points[idx+1], 0])
                return (1 - frac) * p0 + frac * p1

        # ---------- 坐标轴 ----------
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2.5, 2.5, 1],
            x_length=10,
            y_length=7,
            axis_config={"color": BLUE},
            tips=False,
        )
        labels = axes.get_axis_labels(x_label="x", y_label="y")
        self.add(axes, labels)

        # ---------- 等高线（椭圆） ----------
        contours = VGroup()
        for c in [0.5, 1.0, 2.0, 3.0, 4.0, 6.0]:
            # 椭圆: x^2 + 2y^2 = c  => a = sqrt(c), b = sqrt(c/2)
            a = np.sqrt(c)
            b = np.sqrt(c / 2)
            contour = ParametricFunction(
                lambda t, a=a, b=b: axes.coords_to_point(a * np.cos(t), b * np.sin(t)),
                t_range=[0, 2 * PI],
                color=GRAY,
                stroke_width=1,
            )
            # 额外添加一个水平翻转的对称部分？不需要，ParametricFunction画满2pi即完整椭圆
            contours.add(contour)

        self.add(contours)

        # ---------- 初始点与轨迹 ----------
        dot = Dot(color=YELLOW, radius=0.1)
        # 随时间更新位置
        t_tracker = ValueTracker(0.0)
        dot.add_updater(lambda d: d.move_to(interpolate(t_tracker.get_value())))
        self.add(dot)

        # 轨迹线
        trace = TracedPath(dot.get_center, stroke_color=YELLOW, stroke_width=3)
        self.add(trace)

        # 添加起始点标记
        start_label = MathTex(r"\mathbf{x}_0", color=YELLOW, font_size=30)
        start_label.next_to(axes.coords_to_point(*init_point), UR, buff=0.1)
        self.add(start_label)

        # 添加描述文字
        title = Text("Gradient Descent", font_size=36, color=WHITE)
        title.to_corner(UL)
        self.add(title)

        formula = MathTex(r"f(x,y)=x^2+2y^2", font_size=28, color=WHITE)
        formula.next_to(title, DOWN, aligned_edge=LEFT, buff=0.3)
        self.add(formula)

        # ---------- 动画：沿着梯度下降路径移动 ----------
        self.play(
            t_tracker.animate.set_value(num_steps),
            run_time=12,
            rate_func=linear,
        )
        self.wait(1)