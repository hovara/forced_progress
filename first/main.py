import pyray as rl
import raylib as rlc
import math
import random


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

SAND = 1
WATER = 2
TREE = 3
FIRE = 4
FISH_LURE = 5
BSIZE = 10

AXE = 1
FISHING_ROD = 2

MOVING = 1
FISHING = 2


class World:
    def __init__(self):
        self.size = Vec2(100, 100)
        self.blocks = [
            [WATER for _ in range(int(self.size.x))] for _ in range(int(self.size.y))
        ]
        self.island_size = self.size.x * 0.8

    def generate_island(self):
        start_pos = int((self.size.x - self.island_size) / 2)
        end_pos = int(start_pos + self.island_size)

        for y in range(start_pos, end_pos):
            for x in range(start_pos, end_pos):
                self.blocks[y][x] = SAND

    def spawn_trees(self):
        for y in range(int(self.size.y)):
            for x in range(int(self.size.x)):
                if self.blocks[y][x] != SAND:
                    continue
                self.blocks[y][x] = TREE if random.uniform(0, 1) < 0.03 else SAND

    def draw(self):
        for y in range(int(self.size.y)):
            for x in range(int(self.size.x)):
                if self.blocks[y][x] == SAND:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.YELLOW)
                elif self.blocks[y][x] == WATER:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.BLUE)
                elif self.blocks[y][x] == TREE:
                    # sand
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.YELLOW)
                    # trunk
                    rlc.DrawRectangleV(
                        Vec2((x * BSIZE + BSIZE / 2 - BSIZE / 16), y * BSIZE)(),
                        Vec2(int(BSIZE / 8), BSIZE)(),
                        rlc.BROWN,
                    )
                    # leaves
                    rlc.DrawCircleV(
                        Vec2(x * BSIZE + BSIZE / 2, y * BSIZE + BSIZE * 0.3)(),
                        BSIZE * 0.3,
                        rlc.GREEN,
                    )
                elif self.blocks[y][x] == FIRE:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.ORANGE)
                elif self.blocks[y][x] == FISH_LURE:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.BLUE)
                    rlc.DrawCircleV(
                        Vec2(x * BSIZE + BSIZE / 2, y * BSIZE + BSIZE / 2)(),
                        BSIZE / 2,
                        rlc.WHITE,
                    )


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.camera = rl.Camera2D()
        self.camera.offset = (Vec2(WINDOW_WIDTH, WINDOW_HEIGHT) / 2)()
        self.camera.zoom = 10
        self.state = MOVING
        self.fishing_timer = 0
        self.fish_lure_pos = Vec2(0, 0)

        # inventory
        self.tool = AXE

        self.wood = 0
        self.sappling = 0
        self.fish = 0

        self.MAX_FOOD = 10
        self.food_timer = 0
        self.food = 10

        self.wetness_timer = 0
        self.wetness = 0

    def move(self):
        dx = rlc.IsKeyDown(rlc.KEY_D) - rlc.IsKeyDown(rlc.KEY_A)
        dy = rlc.IsKeyDown(rlc.KEY_S) - rlc.IsKeyDown(rlc.KEY_W)
        if dir := Vec2(dx, dy):
            self.pos += dir / dir.len() * rlc.GetFrameTime() * 100

    def _fish(self, world):
        self.fishing_timer += rlc.GetFrameTime()
        if self.fishing_timer >= 3:
            self.fishing_timer = 0
            self.state = MOVING
            print("from _fish", self.fish_lure_pos)
            print(world.blocks[int(self.fish_lure_pos.y)][int(self.fish_lure_pos.x)])
            world.blocks[int(self.fish_lure_pos.y)][int(self.fish_lure_pos.x)] = WATER
            print(world.blocks[int(self.fish_lure_pos.y)][int(self.fish_lure_pos.x)])
            self.fish_lure_pos = Vec2(0, 0)

    def update(self, world):
        # update food
        if rlc.IsKeyPressed(rlc.KEY_U):
            self.food -= 1
            self.food = min(10, max(0, self.food))

        self.food_timer += rlc.GetFrameTime()
        while self.food_timer >= 10:
            self.food_timer -= 10
            self.food -= 1
            self.food = min(10, max(0, self.food))

        # update wetness
        if rlc.IsKeyPressed(rlc.KEY_U):
            self.wetness += 1
            self.wetness = min(10, max(0, self.wetness))

        self.wetness_timer += rlc.GetFrameTime()
        while self.wetness_timer >= 10:
            self.wetness_timer -= 10
            self.wetness += 1
            self.wetness = min(10, max(0, self.wetness))

        if self.state == MOVING:
            self.move()

        if self.state == FISHING:
            self._fish(world)

        self.camera.target = self.pos()
        self.camera.zoom = math.exp(
            math.log(self.camera.zoom) + rlc.GetMouseWheelMove() * 0.1
        )

        # mouse block coordinates
        mpos = rlc.GetScreenToWorld2D(rlc.GetMousePosition(), self.camera)
        W_x = int(max(0, min(world.size.x - 1, mpos.x / BSIZE)))
        W_y = int(max(0, min(world.size.y - 1, mpos.y / BSIZE)))

        if rlc.IsKeyPressed(rlc.KEY_TWO):
            self.tool = FISHING_ROD
        elif rlc.IsKeyPressed(rlc.KEY_ONE):
            self.tool = AXE

        if rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_LEFT) and self.state == MOVING:
            # break tree
            if world.blocks[W_y][W_x] == TREE and self.tool == AXE:
                dx = (mpos.x - self.pos.x) ** 2
                dy = (mpos.y - self.pos.y) ** 2
                if math.sqrt(dx + dy) < 15:
                    world.blocks[W_y][W_x] = SAND
                    self.wood += 1
                    self.sappling += 1 if random.uniform(0, 1) <= 0.33 else 0
                # else:
                #     return "You are too far from the tree!"
            # fishing
            elif world.blocks[W_y][W_x] == WATER and self.tool == FISHING_ROD:
                self.state = FISHING
                world.blocks[W_y][W_x] = FISH_LURE
                self.fish_lure_pos = Vec2(W_x, W_y)
                print("set fish lure at", self.fish_lure_pos, "or", Vec2(W_y, W_x))
                print(world.blocks[W_y][W_x])
        elif rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_LEFT) and self.state == FISHING:
            # fish behaviour
            pass

        if rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_RIGHT):
            if world.blocks[W_y][W_x] == SAND and self.wood >= 50:
                self.wood -= 50
                world.blocks[W_y][W_x] = FIRE
            # else:
            #     return "You need more wood to build FIRE!"

    def draw(self):
        # body
        rlc.DrawCircleV(self.pos(), 2, rlc.RED)
        # head
        rlc.DrawCircleV((self.pos - Vec2(0, 2))(), 1, rl.Color(224, 183, 94, 255))

        # equipped tool
        if self.tool == AXE:
            rlc.DrawRectangleV(
                Vec2(self.pos.x + 3, self.pos.y - 2)(), Vec2(0.5, 4)(), rlc.DARKBROWN
            )
            rlc.DrawTriangle(
                Vec2(self.pos.x + 5, self.pos.y - 2)(),
                Vec2(self.pos.x + 3, self.pos.y - 1)(),
                Vec2(self.pos.x + 5, self.pos.y)(),
                rlc.GRAY,
            )
        elif self.tool == FISHING_ROD:
            rlc.DrawRectangleV(
                Vec2(self.pos.x + 3, self.pos.y - 8)(), Vec2(0.5, 10)(), rlc.DARKBROWN
            )
            fish_tip = Vec2(self.pos.x + 3.25, self.pos.y - 8)

            # fishing line
            rlc.DrawCircleV(fish_tip(), 0.5, rlc.BROWN)
            if self.state == FISHING:
                line_points = 20
                line_coords = []
                for i in range(line_points):
                    T = 1 / (line_points - 1) * i
                    line_coords.append(
                        rlc.GetSplinePointLinear(
                            fish_tip(),
                            (self.fish_lure_pos * BSIZE + Vec2(BSIZE / 2, BSIZE / 2))(),
                            T,
                        )
                    )
                    # if i not in (0, line_points - 1):
                    #     line_coords[-1].y -= 30 * ((T - 0.5) ** 2)
                    line_coords[-1].y -= 60 * ((T - 0.5) ** 2) - 15
                rlc.DrawSplineLinear(line_coords, line_points, 0.5, rlc.BLACK)

    def draw_stats(self):
        # items quantity
        text = (
            f"Wood: {self.wood} | Sappling: {self.sappling} | Fish: {self.fish}"
        ).encode()
        rlc.DrawRectangleV(
            Vec2(0, 0)(), Vec2(30 * len(text), 70)(), rl.Color(0, 0, 0, 100)
        )
        rlc.DrawText(text, 10, 10, 50, rlc.WHITE)

        # equiped tool tooltip
        text = (
            "Equiped Tool: " + ("AXE" if self.tool == AXE else "FISHING_ROD")
        ).encode()
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
    player = Player(Vec2(10, 10))
    world = World()
    world.generate_island()
    world.spawn_trees()
    while not rlc.WindowShouldClose():
        player.update(world)
        rlc.BeginDrawing()
        rlc.BeginMode2D(player.camera)
        rlc.ClearBackground(rlc.BLACK)
        world.draw()
        player.draw()
        rlc.EndMode2D()
        player.draw_stats()
        rlc.EndDrawing()
    rlc.CloseWindow()


if __name__ == "__main__":
    main()
