import pyray as rl
import raylib as rlc
import math
import random
from enum import Enum, auto


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


class Tool(Enum):
    AXE = 1
    FISHING_ROD = 2


class State(Enum):
    MOVING = 1
    FISHING = 2


class Block:
    class Type(Enum):
        SAND = 1
        WATER = 2
        TREE = 3
        FIRE = 4
        BOBBER = 5

    def __init__(self, block_type, height):
        self.type = block_type
        self.height = height


class World:
    def __init__(self):
        self.size = Vec2(100, 100)
        self.blocks = [
            [Block(Block.Type.WATER, 0) for _ in range(int(self.size.x))]
            for _ in range(int(self.size.y))
        ]
        self.island_size = self.size * 0.8
        self.generate_island()
        self.spawn_trees()

    def generate_island(self):
        start_pos = int((self.size.x - self.island_size.x) / 2)
        end_pos = int(start_pos + self.island_size.x)

        for y in range(start_pos, end_pos):
            for x in range(start_pos, end_pos):
                self.blocks[y][x] = Block(Block.Type.SAND, 0)

    def spawn_trees(self):
        for y in range(int(self.size.y)):
            for x in range(int(self.size.x)):
                if self.blocks[y][x].type != Block.Type.SAND:
                    continue
                self.blocks[y][x].type = (
                    Block.Type.TREE if random.uniform(0, 1) < 0.03 else Block.Type.SAND
                )

    def draw(self):
        for y in range(int(self.size.y)):
            for x in range(int(self.size.x)):
                if self.blocks[y][x].type == Block.Type.SAND:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.YELLOW)

                elif self.blocks[y][x].type == Block.Type.WATER:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.BLUE)

                elif self.blocks[y][x].type == Block.Type.TREE:
                    self._draw_tree(x, y)

                elif self.blocks[y][x].type == Block.Type.FIRE:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.ORANGE)

                elif self.blocks[y][x].type == Block.Type.BOBBER:
                    rlc.DrawRectangle(x * BSIZE, y * BSIZE, BSIZE, BSIZE, rlc.BLUE)

    def _draw_tree(self, x, y):
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


class FanMenu:
    BASE_ANGULAR_SPEED = 300
    PICK_TIME = 5

    def __init__(self):
        self.options = 3
        self.option_arc = 180 / self.options
        self.curr_angle = 0
        self.dir = 1

        self.ON = False

    def select(self):
        print(self.curr_angle // self.option_arc)
        return int(self.curr_angle // self.option_arc)

    def __call__(self):
        self.ON = True
        self.options = random.choice((3, 5, 7, 9))
        self.option_arc = 180 / self.options

    def __bool__(self):
        return bool(self.ON)

    def update(self):
        self.curr_angle += self.dir * self.BASE_ANGULAR_SPEED * rlc.GetFrameTime()
        if self.curr_angle <= 0 or self.curr_angle >= 180:
            self.curr_angle = min(180, max(0, self.curr_angle))
            self.dir *= -1

    def draw(self):
        # indicator bg
        outer_radius = WINDOW_WIDTH / 2 - 100
        center = Vec2(WINDOW_WIDTH // 2, WINDOW_HEIGHT - outer_radius)
        arc = self.option_arc
        # segments should depend on ocean depth (farther == more fish / different fish)
        options = self.options

        # out of focus "black layer"
        rlc.DrawRectangle(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, rlc.Fade(rlc.BLACK, 0.5))

        for o in range(options):
            color = rlc.Fade(rlc.WHITE, 0.6) if o % 2 else rlc.Fade(rlc.GREEN, 0.3)
            rlc.DrawCircleSector(
                center(), outer_radius, 180 + arc * o, 180 + arc * o + arc, 10, color
            )
            rlc.DrawCircleSectorLines(
                center(), outer_radius, 180 + arc * o, 180 + arc * o + arc, 10, color
            )

        # target indicator

        rlc.DrawCircleSector(
            center(),
            outer_radius,
            180 + self.curr_angle,
            180 + self.curr_angle + 1,
            10,
            rlc.Fade(rlc.MAROON, 0.5),
        )


class FishingManager:
    PULL_TIME = 0.66
    FISHING_WINDOW_START = 7 - PULL_TIME
    FISHING_MENU_TIME = 5

    def __init__(self):
        self.fish = 0
        self.fish_menu = FanMenu()

        self.fish_hooked = False

        self.time_limit = random.randint(4, 7)
        self.timer = 0.0

        self.bobber_pos = Vec2(0, 0)
        self.bobber_sink = 0.0
        self.sink_dir = 1
        self.wave_size = BSIZE / 8

    def _set_time_window(self):
        self.time_limit = random.randint(3, 6)
        self.FISHING_WINDOW_START = self.time_limit - self.PULL_TIME

    def pull_fish(self):
        if self.fish_hooked:
            self.fish_menu()
            self.timer = 0
            self.time_limit = self.fish_menu.PICK_TIME
        else:
            self.timer = self.time_limit

    def _reset_bobber(self, world):
        world.blocks[int(self.bobber_pos.y)][
            int(self.bobber_pos.x)
        ].type = Block.Type.WATER
        self.bobber_pos = Vec2(0, 0)
        self.wave_size = BSIZE / 8
        self.fish_hooked = False
        self.bobber_sink = 0

    def update(self, player, world):
        self.timer += rlc.GetFrameTime()
        if self.timer >= self.time_limit:
            self.timer = 0
            self._reset_bobber(world)
            player.state = State.MOVING
            self.fish_menu.ON = False
            return

        elif not self.fish_hooked and self.timer >= self.FISHING_WINDOW_START:
            self.fish_hooked = True
            self.wave_size = BSIZE / 8

        # update wave size
        self.wave_size = min(BSIZE, self.wave_size + rlc.GetFrameTime())

        # update bobber
        sink_speed = 0.25
        if not self.fish_hooked:
            self.bobber_sink += rlc.GetFrameTime() * self.sink_dir * sink_speed

            max_sink = 0.25
            if self.bobber_sink >= max_sink or self.bobber_sink <= 0:
                self.sink_dir *= -1
        elif self.bobber_sink != 1:
            self.bobber_sink = 1

    def _draw_waves(self, center, state):
        if state == State.FISHING:
            fade = 1 - self.wave_size / (BSIZE / 2) + 0.15
            # draw splash
            if self.wave_size <= 1.6:
                rlc.DrawCircleV(center(), 1.6, rlc.Fade(rlc.WHITE, 0.8))
            # draw waves
            rlc.DrawCircleV(center(), self.wave_size, rlc.Fade(rlc.BLUE, fade))
            rlc.DrawCircleV(center(), self.wave_size * 0.8, rlc.Fade(rlc.SKYBLUE, fade))
            rlc.DrawCircleV(center(), self.wave_size * 0.6, rlc.Fade(rlc.BLUE, fade))
            rlc.DrawCircleV(center(), self.wave_size * 0.4, rlc.Fade(rlc.SKYBLUE, fade))
            rlc.DrawCircleV(center(), self.wave_size * 0.2, rlc.Fade(rlc.BLUE, fade))
            rlc.DrawCircleV(center(), self.wave_size * 0.1, rlc.Fade(rlc.SKYBLUE, fade))

    def draw_bobber(self, center, state):
        self._draw_waves(center, state)
        rlc.DrawCircleV(center(), 1 - self.bobber_sink, rlc.RED)
        offset = Vec2(0, 0) if state == State.FISHING else Vec2(0, -1)
        rlc.DrawCircleV((center + offset)(), 0.4, rlc.WHITE)

    def draw(self, pos, state):
        fishing_rod_body = Vec2(pos.x + 3, pos.y - 8)
        fishing_rod_tip = Vec2(pos.x + 3.25, pos.y - 8)
        bobber_pos = (
            fishing_rod_tip + Vec2(0.5, 2)
            if state == State.MOVING
            else self.bobber_pos * BSIZE + BSIZE / 2
        )

        # draw fishing bobber
        self.draw_bobber(bobber_pos, state)

        # draw fishing rod
        rlc.DrawRectangleV(fishing_rod_body(), Vec2(0.5, 10)(), rlc.DARKBROWN)
        rlc.DrawCircleV(fishing_rod_tip(), 0.5, rlc.BROWN)

        # draw fishing line
        if state == State.FISHING:
            line_points = 20
            line_coords = []
            for i in range(line_points):
                T = 1 / (line_points - 1) * i
                line_coords.append(
                    rlc.GetSplinePointLinear(
                        fishing_rod_tip(),
                        (self.bobber_pos * BSIZE + Vec2(BSIZE / 2, BSIZE / 2))(),
                        T,
                    )
                )
                line_coords[-1].y -= 60 * ((T - 0.5) ** 2) - 15
            rlc.DrawSplineLinear(line_coords, line_points, 0.2, rlc.BLACK)
        elif state == State.MOVING:
            rlc.DrawLineEx(
                fishing_rod_tip(), (bobber_pos - Vec2(0, 1))(), 0.2, rlc.BLACK
            )


class Item:
    class ID(Enum):
        # fish
        SURGEONFISH = 1
        CLOWNFISH = 2
        CRAB = 3
        PUFFERFISH = 4
        ANCHOVY = 5
        ANGELFISH = 6
        BASS = 7
        GOLDFISH = 8
        TROUT = 9
        CATFISH = 10
        # tools
        AXE = 11
        FISHING_ROD = 12
        # food
        APPLE = 13
        COOKED_FISH = 14
        # materials
        WOOD = 15
        STICK = 16
        SAPPLING = 17
        STONE = 18
        # furniuture
        FIRE = 19

    atlas = None

    @classmethod
    def load_atlas(cls):
        if cls.atlas is None:
            cls.atlas = rlc.LoadTexture(b"./assets/items.png")

    @classmethod
    def unload_atlas(cls):
        if cls.atlas is not None:
            rlc.UnloadTexture(cls.atlas)
            cls.atlas = None

    def __init__(self, item_id):
        self.id = ITEM_DATA[item_id]["id"]
        self.stack_size = ITEM_DATA[item_id]["stack_size"]

    def draw(self, pos):
        # rlc.DrawTextureRec(
        #     self.atlas,
        #     rl.Rectangle(int(self.id.value - 1) * 16, 0, 16, 16),
        #     pos(),
        #     rlc.WHITE,
        # )
        rlc.DrawTexturePro(
            self.atlas,
            rl.Rectangle(int(self.id.value - 1) * 16, 0, 16, 16),
            rl.Rectangle(pos.x, pos.y, 96, 96),
            Vec2(0, 0)(),
            0,
            rlc.WHITE,
        )


ITEM_DATA = {
    Item.ID.AXE: {"id": Item.ID.AXE, "stack_size": 1},
    Item.ID.FISHING_ROD: {"id": Item.ID.FISHING_ROD, "stack_size": 1},
    Item.ID.WOOD: {"id": Item.ID.WOOD, "stack_size": 64},
    Item.ID.SAPPLING: {"id": Item.ID.SAPPLING, "stack_size": 64},
}


class Inventory:
    class Slot:
        def __init__(self, item=None, quantity=0):
            self.item = item
            self.quantity = quantity

        def copy(self):
            return Inventory.Slot(Item(self.item.id), self.quantity)

    SLOT_SIZE = Vec2(100, 100)

    def __init__(self):
        self.slots = [[self.Slot() for _ in range(5)] for _ in range(3)]
        self.selection = 0

        self.ON = False

    def pickup(self, item, q):
        for y in range(3):
            for x in range(5):
                if q:
                    s = self.slots[y][x]

                    if s.item is None:
                        s.item = item

                    if s.item.id == item.id:
                        if s.quantity + q > s.item.stack_size:
                            dq = s.item.stack_size - s.quantity
                            q -= dq
                            s.quantity += dq
                        else:
                            s.quantity += q
                            q = 0
                else:
                    break
        if q:
            print("Inventory is full, dropped " + str(q) + " items.")
            # drop items, requires world to store item list on each block

    def remove(self, slot_pos, q):
        x, y = int(slot_pos.x), int(slot_pos.y)
        if self.slots[y][x].item is not None:
            if q >= self.slots[y][x].quantity:
                old_slot = self.slots[y][x].copy()
                self.slots[y][x] = Inventory.Slot()
                # put item in cursor
                return old_slot
            else:
                self.slots[y][x].quantity -= q
                # put item in cursor
                return Inventory.Slot(Item(self.slots[y][x].item.id), q)

    def add(self, slot_pos, item, q):
        x, y = int(slot_pos.x), int(slot_pos.y)
        s = self.slots[y][x]
        if s.item is None:
            s.item = item
            s.quantity = q
        elif s.item.id == item.id:
            if s.quantity + q >= s.item.stack_size:
                dq = s.item.stack_size - s.quantity
                q -= dq
                s.quantity += dq
                # put item excess back in cursor
                return Inventory.Slot(Item(s.item.id), q)

    def update(self, player):
        if rlc.IsKeyPressed(rlc.KEY_I):
            self.ON = not self.ON

        hotbar_selection = {
            rlc.KEY_ONE: 0,
            rlc.KEY_TWO: 1,
            rlc.KEY_THREE: 2,
            rlc.KEY_FOUR: 3,
            rlc.KEY_FIVE: 4,
        }
        key = rlc.GetKeyPressed()
        self.selection = (
            hotbar_selection[key] if key in hotbar_selection.keys() else self.selection
        )

        player.item_in_hand = self.slots[0][self.selection].item

    def draw(self):
        # 5 -> MAX_SLOTS_PER_ROW
        # 100 -> SLOT_SIZE
        for x in range(5):
            for y in range(3):
                if y >= 1 and not self.ON:
                    break
                offset = Vec2(1 + x, 1 + y) * 10
                pos = Vec2(x, y) * 100 + offset
                rlc.DrawRectangleV(pos(), self.SLOT_SIZE(), rlc.Fade(rlc.BLACK, 0.5))
                if self.slots[y][x].item is None:
                    continue
                else:
                    self.slots[y][x].item.draw(pos + Vec2(2, 2))
                    if self.slots[y][x].item.stack_size > 1:
                        rlc.DrawText(
                            str(self.slots[y][x].quantity).encode("utf-8"),
                            int(pos.x + 60),
                            int(pos.y + 70),
                            32,
                            rlc.WHITE,
                        )

                # elif self.slots[y][x].item.id is Item.ID.AXE:
                #     item_pos = pos + Vec2(50 - 6.25, 5)
                #     item_size = self.SLOT_SIZE * Vec2(0.125, 0.9)
                #     rlc.DrawRectangleV(
                #         item_pos(),
                #         item_size(),
                #         rlc.DARKBROWN,
                #     )
                #     rlc.DrawTriangle(
                #         (item_pos + Vec2(50, 0))(),
                #         (item_pos + Vec2(0, 25 * 0.9))(),
                #         (item_pos + Vec2(50, 50 * 0.9))(),
                #         rlc.GRAY,
                #     )
                # elif self.slots[y][x].item.id is Item.ID.FISHING_ROD:
                #     item_pos = pos + Vec2(50 - 2.5, 5)
                #     item_size = self.SLOT_SIZE * Vec2(0.05, 0.9)
                #
                #     fishing_rod_body = item_pos
                #     fishing_rod_tip = item_pos + Vec2(2.5, 0)
                #
                #     bobber_pos = fishing_rod_tip + Vec2(5, 20)
                #     # draw bobber
                #     rlc.DrawCircleV(bobber_pos(), 10, rlc.RED)
                #     offset = Vec2(0, -10)
                #     rlc.DrawCircleV((bobber_pos + offset)(), 4, rlc.WHITE)
                #
                #     # draw body
                #     rlc.DrawRectangleV(fishing_rod_body(), item_size(), rlc.DARKBROWN)
                #     rlc.DrawCircleV(fishing_rod_tip(), 5, rlc.BROWN)
                #
                #     # draw line
                #     rlc.DrawLineEx(
                #         fishing_rod_tip(), (bobber_pos - Vec2(0, 10))(), 2, rlc.BLACK
                #     )

        offset = Vec2(1 + self.selection % 5, 1 + self.selection // 5) * 10
        pos = Vec2(self.selection % 5, self.selection // 5) * 100 + offset
        rec = rl.Rectangle(int(pos.x), int(pos.y), 100, 100)
        rlc.DrawRectangleLinesEx(rec, 3, rlc.LIGHTGRAY)


class Player:
    def __init__(self, pos):
        self.pos = pos
        self.camera = rl.Camera2D()
        self.camera.offset = (Vec2(WINDOW_WIDTH, WINDOW_HEIGHT) / 2)()
        self.camera.zoom = 10
        self.state = State.MOVING

        # inventory
        self.inventory = Inventory()
        self.item_in_hand = None

        self.wood = 0
        self.sappling = 0

        self.fishing = FishingManager()

        # stats
        self.MAX_FOOD = 10
        self.food_timer = 0
        self.food = 10

        self.wetness_timer = 0
        self.wetness = 10

    def move(self, world):
        dx = rlc.IsKeyDown(rlc.KEY_D) - rlc.IsKeyDown(rlc.KEY_A)
        dy = rlc.IsKeyDown(rlc.KEY_S) - rlc.IsKeyDown(rlc.KEY_W)
        self.dir = Vec2(dx, dy)
        if self.dir:
            self.pos += self.dir / self.dir.len() * rlc.GetFrameTime() * 100
            start_pos = int((world.size.x - world.island_size.x) / 2) * BSIZE
            end_pos = int(start_pos + world.island_size.x * BSIZE)
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

        # fish menu update
        if self.fishing.fish_menu:
            self.fishing.fish_menu.update()

        self.inventory.update(self)

        # interract
        # mouse block coordinates
        mpos = rlc.GetScreenToWorld2D(rlc.GetMousePosition(), self.camera)
        W_x = int(max(0, min(world.size.x - 1, mpos.x / BSIZE)))
        W_y = int(max(0, min(world.size.y - 1, mpos.y / BSIZE)))

        # if rlc.IsKeyPressed(rlc.KEY_TWO):
        #     self.tool = Tool.FISHING_ROD
        # elif rlc.IsKeyPressed(rlc.KEY_ONE):
        #     self.tool = Tool.AXE

        if (
            rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_LEFT)
            and self.state == State.MOVING
        ):
            # break tree
            if (
                world.blocks[W_y][W_x].type == Block.Type.TREE
                and self.item_in_hand.id == Item.ID.AXE
            ):
                dx = (mpos.x - self.pos.x) ** 2
                dy = (mpos.y - self.pos.y) ** 2
                if math.sqrt(dx + dy) < 15:
                    world.blocks[W_y][W_x].type = Block.Type.SAND
                    self.inventory.pickup(Item(Item.ID.WOOD), random.randint(1, 5))
                    if random.uniform(0, 1) <= 0.33:
                        self.inventory.pickup(Item(Item.ID.SAPPLING), 1)
                # else:
                #     return "You are too far from the tree!"
            # fishing
            elif (
                world.blocks[W_y][W_x].type == Block.Type.WATER
                and self.item_in_hand.id == Item.ID.FISHING_ROD
            ):
                self.state = State.FISHING
                world.blocks[W_y][W_x].type = Block.Type.BOBBER
                self.fishing.bobber_pos = Vec2(W_x, W_y)
                self.fishing._set_time_window()
        elif (
            rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_LEFT)
            and self.state == State.FISHING
        ):
            if self.fishing.fish_menu:
                self.fishing.fish_menu.select()
                self.fishing.timer = self.fishing.time_limit
            else:
                self.fishing.pull_fish()

        if rlc.IsMouseButtonPressed(rlc.MOUSE_BUTTON_RIGHT):
            if world.blocks[W_y][W_x].type == Block.Type.SAND and self.wood >= 50:
                self.wood -= 50
                world.blocks[W_y][W_x].type = Block.Type.FIRE
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
        if self.item_in_hand is not None:
            if self.item_in_hand.id == Item.ID.AXE:
                rlc.DrawRectangleV(
                    Vec2(self.pos.x + 3, self.pos.y - 2)(),
                    Vec2(0.5, 4)(),
                    rlc.DARKBROWN,
                )
                rlc.DrawTriangle(
                    Vec2(self.pos.x + 5, self.pos.y - 2)(),
                    Vec2(self.pos.x + 3, self.pos.y - 1)(),
                    Vec2(self.pos.x + 5, self.pos.y)(),
                    rlc.GRAY,
                )
            elif self.item_in_hand.id == Item.ID.FISHING_ROD:
                self.fishing.draw(self.pos, self.state)

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
        text = (
            "Equiped Tool: "
            + (
                self.item_in_hand.id.name
                if self.item_in_hand.id in Item.ID
                else "PLACEHOLDER"
            )
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
    Item.load_atlas()
    world = World()
    # player = Player(Vec2(world.size.x // 2 * BSIZE, world.size.y // 2 * BSIZE))
    player = Player(Vec2(130, 130))
    player.inventory.pickup(Item(Item.ID.FISHING_ROD), 1)
    player.inventory.pickup(Item(Item.ID.AXE), 1)
    while not rlc.WindowShouldClose():
        player.update(world)
        rlc.BeginDrawing()

        rlc.BeginMode2D(player.camera)
        rlc.ClearBackground(rlc.BLACK)
        world.draw()
        player.draw()
        rlc.EndMode2D()

        # player.draw_stats()
        if player.fishing.fish_menu:
            player.fishing.fish_menu.draw()

        player.inventory.draw()

        rlc.EndDrawing()
    Item.unload_atlas()
    rlc.CloseWindow()


if __name__ == "__main__":
    main()
