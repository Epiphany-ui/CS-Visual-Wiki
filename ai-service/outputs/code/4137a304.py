from manim import *
import numpy as np

class RiemannSum(Scene):
    def construct(self):
        # 设置坐标轴
        axes = Axes(
            x_range=[0, PI, PI/4],
            y_range=[0, 1.5, 0.5],
            x_length=8,
            y_length=4,
            axis_config={"include_numbers": True}
        )
        axes_labels = axes.get_axis_labels(x_label="x", y_label="y")

        # 定义曲线函数
        curve = lambda x: np.sin(x)
        graph = axes.plot(curve, color=BLUE)
        graph_label = MathTex("f(x)=\\sin(x)").next_to(graph, UR, buff=0.2)

        # 显示坐标轴和曲线
        self.play(Create(axes), Write(axes_labels))
        self.play(Create(graph), Write(graph_label))
        self.wait(0.5)

        # 设置黎曼积分区间
        x_min = 0
        x_max = PI

        # 矩形数量控制器
        n_tracker = ValueTracker(2)

        # 矩形组
        rectangles = VGroup()
        self.add(rectangles)

        # 更新矩形的函数
        def update_rectangles(mob, dt):
            # 获取当前矩形数量
            n = int(n_tracker.get_value())
            width = (x_max - x_min) / n
            # 清空旧的矩形
            mob.clear_updaters()
            mob.submobjects = []
            # 生成新矩形
            for i in range(n):
                left_x = x_min + i * width
                right_x = left_x + width
                # 左黎曼和：以左端点高度为矩形高度
                height = curve(left_x)
                # 将矩形放置到坐标轴中的位置
                rect = Rectangle(
                    width=axes.x_axis.point_to_number(right_x) - axes.x_axis.point_to_number(left_x),
                    height=axes.y_axis.point_to_number(height),
                    fill_color=YELLOW,
                    fill_opacity=0.5,
                    stroke_color=YELLOW,
                    stroke_width=1
                )
                # 矩形左下角对齐到 (left_x, 0) 在坐标轴中的坐标
                bottom_left = axes.c2p(left_x, 0)
                rect.move_to(bottom_left, aligned_edge=DL, coor_mask=[True, True, False])
                mob.add(rect)
            # 重新添加 updater
            mob.add_updater(update_rectangles)

        # 初始添加 updater
        rectangles.add_updater(update_rectangles)

        # 显示面积近似值文字
        approx_text = DecimalNumber(0, num_decimal_places=4)
        approx_text.add_updater(lambda m, dt: m.set_value(
            sum(curve(x_min + i * (x_max - x_min) / int(n_tracker.get_value())) * (x_max - x_min) / int(n_tracker.get_value())
                for i in range(int(n_tracker.get_value()))
            if int(n_tracker.get_value()) > 0
        ))
        approx_text.next_to(axes, DOWN, buff=0.5)
        approx_label = Text("近似面积 = ").next_to(approx_text, LEFT, buff=0.2)
        self.play(Write(approx_label), Write(approx_text))

        # 动画增加矩形数量
        self.play(n_tracker.animate.set_value(50), run_time=12)
        self.wait(2)

        # 显示精确面积（积分值）
        exact_area = 2  # ∫_0^π sin(x) dx = 2
        exact_text = DecimalNumber(exact_area, num_decimal_places=4)
        exact_text.next_to(approx_text, DOWN, buff=0.3)
        exact_label = Text("精确面积 = ").next_to(exact_text, LEFT, buff=0.2)
        self.play(Write(exact_label), Write(exact_text))
        self.wait(2)