import pyray as rl
import raylib as rlc
import math
import random
from enum import Enum


class Vec2:
    def __init__(self, x, y=None):
        (self.x, self.y) = (
            (float(x.x), float(x.y)) if y is None else (float(x), float(y))
        )

    def __call__(self):
        return rl.Vector2(self.x, self.y)

    def __repr__(self):
        return f"Vec2({self.x}, {self.y})"

    def len(self):
        return math.sqrt(self.x**2 + self.y**2)

    def __add__(self, rhs):
        if isinstance(rhs, Vec2):
            return Vec2(self.x + rhs.x, self.y + rhs.y)
        return Vec2(self.x + rhs, self.y + rhs)

    def __sub__(self, rhs):
        if isinstance(rhs, Vec2):
            return Vec2(self.x - rhs.x, self.y - rhs.y)
        return Vec2(self.x - rhs, self.y - rhs)

    def __mul__(self, rhs):
        if isinstance(rhs, Vec2):
            return Vec2(self.x * rhs.x, self.y * rhs.y)
        return Vec2(self.x * rhs, self.y * rhs)

    def __truediv__(self, rhs):
        if isinstance(rhs, Vec2):
            return Vec2(self.x / rhs.x, self.y / rhs.y)
        return Vec2(self.x / rhs, self.y / rhs)

    def __bool__(self):
        return bool(self.x or self.y)


WINDOW_WIDTH = WINDOW_HEIGHT = 1000
BSIZE = 10


class Block(Enum):
    SAND = 1
    WATER = 2
    TREE = 3
    FIRE = 4
    FISH_LURE = 5


class Tool(Enum):
    AXE = 1
    FISHING_ROD = 2


class State(Enum):
    MOVING = 1
    FISHING = 2


class World:
    def __init__(self):
        self.size = Vec2(100, 100)
        self.blocks = [
            [Block.WATER for _ in range(int(self.size.x))]
            for _ in range(int(self.size.y))
        ]
        self.island_size = self.size.x * 0.8

    def generate_island(self):
        start_pos = int((self.size.x - self.island_size) / 2)
        end_pos = int(start_pos + self.island_size)

        for y in range(start_pos, end_pos):
            for x in range(start_pos, end_pos):
                self.blocks[y][x] = Block.SAND

    def spawn_trees(self):
        for y in range(int(self.size.y)):
            for x in range(int(self.size.x)):
                if self.blocks[y][x] != Block.SAND:
                    continue
                self.blocks[y][x] = (
                    Block.TREE if random.uniform(0, 1) < 0.03 else Block.SAND
                )

    def draw(self):
        for y in range(int(self.size.y)):
            for x in range(int(self.size.x)):
                if self.blocks[y][x] == Block.SAND:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.YELLOW)

                elif self.blocks[y][x] == Block.WATER:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.BLUE)

                elif self.blocks[y][x] == Block.TREE:
                    # sand
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.YELLOW)
                    # trunk
                    rlc.DrawRectangleV(
                        Vec2((x * BSIZE + BSIZE / 2 - BSIZE / 16), y * BSIZE + 1)(),
                        Vec2(int(BSIZE / 8), BSIZE - 1)(),
                        rlc.BROWN,
                    )
                    # leaves
                    rlc.DrawCircleV(
                        Vec2(x * BSIZE + BSIZE / 2, y * BSIZE + BSIZE * 0.3)(),
                        BSIZE * 0.3,
                        rlc.GREEN,
                    )

                elif self.blocks[y][x] == Block.FIRE:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.ORANGE)

                elif self.blocks[y][x] == Block.FISH_LURE:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.BLUE)
                    rlc.DrawCircleV(
                        Vec2(x * BSIZE + BSIZE / 2, y * BSIZE + BSIZE / 2)(),
                        BSIZE / 2,
                        rlc.WHITE,
                    )


class FishingManager:
    TIME_LIMIT = 3
    BASE_ANGULAR_SPEED = 300

    def __init__(self):
        self.timer = 0.0
        self.lure_pos = Vec2(0, 0)
        self.fish = 0

        # do i need to put these here???
        self.target_segment = 1
        self.start_target = 20
        self.end_target = 40

        self.curr_speed = self.BASE_ANGULAR_SPEED
        self.curr_angle = 0
        self.dir = 1

    def set_target(self):
        self.target_segment = int(max(0, round(random.uniform(0, 1) * 10) - 2))
        self.start_target = self.target_segment * 20
        self.end_target = self.start_target + 20

    def pull_fish(self):
        if self.curr_angle >= self.start_target and self.curr_angle <= self.end_target:
            self.fish += 1
        self.timer = self.TIME_LIMIT

    def update(self, player, world):
        self.timer += rlc.GetFrameTime()

        self.curr_angle += self.dir * self.curr_speed * rlc.GetFrameTime()
        if self.curr_angle <= 0 or self.curr_angle >= 180:
            self.dir *= -1
            self.curr_speed += self.curr_speed * 0.2

        if self.timer >= self.TIME_LIMIT:
            self.timer = 0
            player.state = State.MOVING
            world.blocks[int(self.lure_pos.y)][int(self.lure_pos.x)] = Block.WATER
            self.lure_pos = Vec2(0, 0)
            self.curr_speed = self.BASE_ANGULAR_SPEED

    def draw(self):
        # indicator bg
        outer_radius = WINDOW_WIDTH / 2 - 100
        center = Vec2(WINDOW_WIDTH // 2, WINDOW_HEIGHT - outer_radius)
        seg_angle = 20
        segments = 9

        rlc.DrawRectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, rlc.Fade(rlc.BLACK, 0.5))

        for s in range(segments):
            color = rlc.Fade(rlc.WHITE, 0.6) if s % 2 else rlc.Fade(rlc.GREEN, 0.3)
            rlc.DrawCircleSector(
                center(),
                outer_radius,
                180 + seg_angle * s,
                180 + seg_angle * s + seg_angle,
                segments,
                color,
            )
            rlc.DrawCircleSectorLines(
                center(),
                outer_radius,
                180 + seg_angle * s,
                180 + seg_angle * s + seg_angle,
                segments,
                color,
            )

        rlc.DrawCircleSector(
            center(),
            outer_radius,
            180 + self.start_target,
            180 + self.end_target,
            segments,
            rlc.Fade(rlc.YELLOW, 0.9),
        )

        rlc.DrawCircleSector(
            center(),
            outer_radius,
            180 + self.curr_angle,
            180 + self.curr_angle + 1,
            segments,
            rlc.Fade(rlc.MAROON, 0.5),
        )


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.camera = rl.Camera2D()
        self.camera.offset = (Vec2(WINDOW_WIDTH, WINDOW_HEIGHT) / 2)()
        self.camera.zoom = 10
        self.state = State.MOVING

        # inventory
        self.tool = Tool.AXE

        self.wood = 0
        self.sappling = 0

        self.fishing = FishingManager()

        # stats
        self.MAX_FOOD = 10
        self.food_timer = 0
        self.food = 10

        self.wetness_timer = 0
        self.wetness = 0

    def move(self, world):
        dx = rlc.IsKeyDown(rlc.KEY_D) - rlc.IsKeyDown(rlc.KEY_A)
        dy = rlc.IsKeyDown(rlc.KEY_S) - rlc.IsKeyDown(rlc.KEY_W)
        self.dir = Vec2(dx, dy)
        if self.dir:
            self.pos += self.dir / self.dir.len() * rlc.GetFrameTime() * 100
            start_pos = int((world.size.x - world.island_size) / 2) * BSIZE
            end_pos = int(start_pos + world.island_size * BSIZE)
            self.pos.x = max(start_pos, min(self.pos.x, end_pos))
            self.pos.y = max(start_pos, min(self.pos.y, end_pos))

    def update(self, world):
        # debugg update food
        self.food_timer += rlc.GetFrameTime()
        while self.food_timer >= 10:
            self.food_timer -= 10
            self.food -= 1
            self.food = min(10, max(0, self.food))

        # update wetness
        self.wetness_timer += rlc.GetFrameTime()
        while self.wetness_timer >= 10:
            self.wetness_timer -= 10
            self.wetness += 1
            self.wetness = min(10, max(0, self.wetness))

        match self.state:
            case State.MOVING:
                self.move(world)
            case State.FISHING:
                self.fishing.update(self, world)

        self.camera.target = self.pos()
        self.camera.zoom = math.exp(
            math.log(self.camera.zoom) + rlc.GetMouseWheelMove() * 0.1
        )

        # interract
        # mouse block coordinates
        mpos = rlc.GetScreenToWorld2D(rlc.GetMousePosition(), self.camera)
        W_x = int(max(0, min(world.size.x - 1, mpos.x / BSIZE)))
        W_y = int(max(0, min(world.size.y - 1, mpos.y / BSIZE)))

        if rlc.IsKeyPressed(rlc.KEY_TWO):
            self.tool = Tool.FISHING_ROD
        elif rlc.IsKeyPressed(rlc.KEY_ONE):
            self.tool = Tool.AXE

        if (
            rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_LEFT)
            and self.state == State.MOVING
        ):
            # break tree
            if world.blocks[W_y][W_x] == Block.TREE and self.tool == Tool.AXE:
                dx = (mpos.x - self.pos.x) ** 2
                dy = (mpos.y - self.pos.y) ** 2
                if math.sqrt(dx + dy) < 15:
                    world.blocks[W_y][W_x] = Block.SAND
                    self.wood += 1
                    self.sappling += 1 if random.uniform(0, 1) <= 0.33 else 0
                # else:
                #     return "You are too far from the tree!"
            # fishing
            elif (
                world.blocks[W_y][W_x] == Block.WATER and self.tool == Tool.FISHING_ROD
            ):
                self.state = State.FISHING
                world.blocks[W_y][W_x] = Block.FISH_LURE
                self.fishing.lure_pos = Vec2(W_x, W_y)
                self.fishing.set_target()
        elif (
            rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_LEFT)
            and self.state == State.FISHING
        ):
            self.fishing.pull_fish()

        if rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_RIGHT):
            if world.blocks[W_y][W_x] == Block.SAND and self.wood >= 50:
                self.wood -= 50
                world.blocks[W_y][W_x] = Block.FIRE
            # else:
            #     return "You need more wood to build FIRE!"

    def draw(self):
        # body
        rlc.DrawCircleV(self.pos(), 2, rlc.RED)
        # head
        rlc.DrawCircleV(
            (self.pos - Vec2(0, 2) + self.dir * 0.4)(), 1, rl.Color(224, 183, 94, 255)
        )

        # equipped tool
        if self.tool == Tool.AXE:
            rlc.DrawRectangleV(
                Vec2(self.pos.x + 3, self.pos.y - 2)(), Vec2(0.5, 4)(), rlc.DARKBROWN
            )
            rlc.DrawTriangle(
                Vec2(self.pos.x + 5, self.pos.y - 2)(),
                Vec2(self.pos.x + 3, self.pos.y - 1)(),
                Vec2(self.pos.x + 5, self.pos.y)(),
                rlc.GRAY,
            )
        elif self.tool == Tool.FISHING_ROD:
            rlc.DrawRectangleV(
                Vec2(self.pos.x + 3, self.pos.y - 8)(), Vec2(0.5, 10)(), rlc.DARKBROWN
            )
            fish_tip = Vec2(self.pos.x + 3.25, self.pos.y - 8)

            # fishing line
            rlc.DrawCircleV(fish_tip(), 0.5, rlc.BROWN)
            if self.state == State.FISHING:
                line_points = 20
                line_coords = []
                for i in range(line_points):
                    T = 1 / (line_points - 1) * i
                    line_coords.append(
                        rlc.GetSplinePointLinear(
                            fish_tip(),
                            (
                                self.fishing.lure_pos * BSIZE
                                + Vec2(BSIZE / 2, BSIZE / 2)
                            )(),
                            T,
                        )
                    )
                    line_coords[-1].y -= 60 * ((T - 0.5) ** 2) - 15
                rlc.DrawSplineLinear(line_coords, line_points, 0.5, rlc.BLACK)

    def draw_stats(self):
        # items quantity
        text = (
            f"Wood: {self.wood} | Sappling: {self.sappling} | Fish: {self.fishing.fish}"
        ).encode()
        rlc.DrawRectangleV(
            Vec2(0, 0)(), Vec2(30 * len(text), 70)(), rl.Color(0, 0, 0, 100)
        )
        rlc.DrawText(text, 10, 10, 50, rlc.WHITE)

        # equiped tool tooltip
        text = ("Equiped Tool: " + self.tool.name).encode()
        rlc.DrawRectangleV(
            Vec2(0, 70)(), Vec2(30 * len(text), 70)(), rl.Color(0, 0, 0, 100)
        )
        rlc.DrawText(text, 10, 10 + 70, 50, rlc.WHITE)

        # stats
        text = ("Food: " + "".join(["*" for _ in range(self.food)])).encode()
        rlc.DrawRectangleV(
            Vec2(0, 140)(), Vec2(30 * len(text), 70)(), rl.Color(0, 0, 0, 100)
        )
        rlc.DrawText(
            text,
            10,
            10 + 140,
            50,
            rl.Color(255, int(25.5 * self.food), int(25.5 * self.food), 255),
        )

        text = ("Wetness: " + "".join(["*" for _ in range(self.wetness)])).encode()
        rlc.DrawRectangleV(
            Vec2(0, 210)(), Vec2(30 * len(text), 70)(), rl.Color(0, 0, 0, 100)
        )
        rlc.DrawText(
            text,
            10,
            10 + 210,
            50,
            rl.Color(255 - int(25.5 * (min(10, self.wetness))), 255, 255, 255),
        )


def main():
    rlc.InitWindow(WINDOW_WIDTH, WINDOW_HEIGHT, b"First")
    world = World()
    world.generate_island()
    world.spawn_trees()
    # player = Player(Vec2(world.size.x // 2 * BSIZE, world.size.y // 2 * BSIZE))
    player = Player(Vec2(130, 130))
    while not rlc.WindowShouldClose():
        player.update(world)
        rlc.BeginDrawing()

        rlc.BeginMode2D(player.camera)
        rlc.ClearBackground(rlc.BLACK)
        world.draw()
        player.draw()
        rlc.EndMode2D()

        player.draw_stats()
        if player.state == State.FISHING:
            player.fishing.draw()

        rlc.EndDrawing()
    rlc.CloseWindow()


if __name__ == "__main__":
    main()
