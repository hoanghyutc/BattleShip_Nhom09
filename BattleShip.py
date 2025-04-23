import pygame
import random
import time
import settings
import Menu

# Biến cài đặt mặc định
GRID_SIZE = 10
SHIP_COUNT = 4

# Biến toàn cục cho chế độ chơi
ai_level = "normal"




def start_game(grid_size=10, ship_count=4, difficulty="normal"):
    global GRID_SIZE, SHIP_COUNT, ai_level
    GRID_SIZE = grid_size
    SHIP_COUNT = ship_count
    ai_level = difficulty

    pygame.init()
    pygame.mixer.init()

    # âm thanh
    gunshot_sound = pygame.mixer.Sound("assets/sounds/gunshot.wav")
    gunshot_sound.set_volume(0.5)
    splash_sound = pygame.mixer.Sound("assets/sounds/splash.wav")
    splash_sound.set_volume(0.4)
    # âm thanh nền
    pygame.mixer.music.load("assets/sounds/battle.wav")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1, 0.0)

    WIDTH, HEIGHT = 900, 600
    CELL_SIZE = 30
    # MARGIN = 50
    # Kích thước bảng pixel
    grid_pixel_width = (GRID_SIZE + 1) * CELL_SIZE
    total_width = 2 * grid_pixel_width + 100  # khoảng cách giữa 2 bảng

    # Vị trí bắt đầu vẽ bảng bên trái (điều chỉnh để căn giữa)
    start_x = (WIDTH - total_width) // 2

    # Tọa độ bảng người chơi và AI (điều chỉnh để đối xứng)
    player_offset_x = start_x
    ai_offset_x = start_x + grid_pixel_width + 100

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Battleship Game")

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    GRAY = (200, 200, 200)
    BLACK = (0, 0, 0)

    def draw_text(text, x, y, color=BLACK):
        font = pygame.font.Font(None, 30)
        render = font.render(text, True, color)
        text_rect = render.get_rect(center=(x, y))  # Sử dụng center thay vì topleft
        screen.blit(render, text_rect)

    # Tạo danh sách tàu dựa trên số lượng tàu được chọn
    # ships_data = []
    # if SHIP_COUNT >= 2:
    #     ships_data.append((5, "Carrier", "assets/images/ships/carrier/carrier1.png", "assets/images/ships/carrier/carrier.png"))
    # if SHIP_COUNT >= 3:
    #     ships_data.append((4, "Battleship", "assets/images/ships/battleship/battleship1.png", "assets/images/ships/battleship/battleship.png"))
    # if SHIP_COUNT >= 4:
    #     ships_data.append((3, "Cruiser", "assets/images/ships/cruiser/cruiser1.png", "assets/images/ships/cruiser/cruiser.png"))
    # if SHIP_COUNT >= 4:
    #     ships_data.append((2, "Destroyer", "assets/images/ships/destroyer/destroyer1.png", "assets/images/ships/destroyer/destroyer.png"))
    # # if SHIP_COUNT >= 3:
    # #     ships_data.append((2, "Submarine", "assets/images/ships/submarine/submarine.png", "assets/images/ships/submarine/submarine.png"))
    ALL_SHIPS = [
        (2, "Destroyer", "assets/images/ships/destroyer/destroyer1.png", "assets/images/ships/destroyer/destroyer.png"),
        (3, "Cruiser", "assets/images/ships/cruiser/cruiser1.png", "assets/images/ships/cruiser/cruiser.png"),
        (4, "Battleship", "assets/images/ships/battleship/battleship1.png",
         "assets/images/ships/battleship/battleship.png"),
        (5, "Carrier", "assets/images/ships/carrier/carrier1.png", "assets/images/ships/carrier/carrier.png"),
    ]
    ships_data = ALL_SHIPS[:SHIP_COUNT]

    ALL_DESTROYED_SHIPS = [
        (2, "Destroyer_Destroyed", "assets/images/ships/destroyer/destroyer_destroyed_horizontal.png",
         "assets/images/ships/destroyer/destroyer_destroyed_vertical.png"),
        (3, "Cruiser_Destroyed", "assets/images/ships/cruiser/cruiser_destroyed_horizontal.png",
         "assets/images/ships/cruiser/cruiser_destroyed_vertical.png"),
        (4, "Battleship_Destroyed", "assets/images/ships/battleship/battleship_destroyed_horizontal.png",
         "assets/images/ships/battleship/battleship_destroyed_vertical.png"),
        (5, "Carrier_Destroyed", "assets/images/ships/carrier/carrier_destroyed_horizontal.png",
         "assets/images/ships/carrier/carrier_destroyed_vertical.png"),
    ]

    ships_destroyed = ALL_DESTROYED_SHIPS[:SHIP_COUNT]

    # Track which ships have been sunk
    player_sunk_ships = [False] * len(ships_data)
    ai_sunk_ships = [False] * len(ships_data)

    # Track the position and orientation of AI ships for display when sunk
    ai_ships_orientation = [None] * len(ships_data)
    ai_ships_start_pos = [None] * len(ships_data)

    # Track the position and orientation of player ships for display when sunk
    player_ships_orientation = [None] * len(ships_data)
    player_ships_start_pos = [None] * len(ships_data)

    def can_place_ship(grid, x, y, size, direction):
        occupied_cells = set()
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if grid[row][col] == 1:
                    occupied_cells.add((col, row))
        if direction == "H":
            if x + size > GRID_SIZE:
                return False
            return not any((x + i, y) in occupied_cells for i in range(size))
        else:
            if y + size > GRID_SIZE:
                return False
            return not any((x, y + i) in occupied_cells for i in range(size))

    def place_ship(grid, x, y, size, direction):
        ship_coords = []
        for i in range(size):
            if direction == "H":
                grid[y][x + i] = 1
                ship_coords.append((x + i, y))
            else:
                grid[y + i][x] = 1
                ship_coords.append((x, y + i))
        return ship_coords

    def handle_shot(grid, shots, ship_locations, x, y):
        if shots[y][x] != 0:
            return False, False, -1  # Already shot here, return invalid ship index

        shots[y][x] = 1 if grid[y][x] == 1 else -1
        hit = False
        sunk = False
        ship_idx = -1  # Track which ship was hit

        # Kiểm tra nếu bắn trúng tàu
        for idx, ship_loc in enumerate(ship_locations):
            if (x, y) in ship_loc:
                hit = True
                ship_idx = idx
                # Kiểm tra xem tất cả các ô của tàu đã bị bắn chưa
                all_hit = all(shots[cy][cx] == 1 for cx, cy in ship_loc)
                if all_hit:
                    sunk = True
                break

        if hit:
            gunshot_sound.play()
        else:
            splash_sound.play()
        return hit, sunk, ship_idx

    def ai_place_ships():
        ai_grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
        ai_ships_locations = [set() for _ in range(len(ships_data))]

        for i, (size, name, path_h, path_v) in enumerate(ships_data):
            placed = False
            while not placed:
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                direction = random.choice(["H", "V"])
                if can_place_ship(ai_grid, x, y, size, direction):
                    ship_coords = place_ship(ai_grid, x, y, size, direction)
                    ai_ships_locations[i] = set(ship_coords)
                    # Store ship orientation and starting position for displaying when sunk
                    ai_ships_orientation[i] = direction
                    ai_ships_start_pos[i] = (x, y)
                    placed = True

        return ai_grid, ai_ships_locations

    def get_ship_probability_map(ai_shots, remaining_ships):
        prob_map = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

        # Tính xác suất cho mỗi ô dựa trên kích thước tàu còn lại
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if ai_shots[y][x] != 0:  # Đã bắn
                    continue

                # Kiểm tra khả năng đặt tàu theo chiều ngang
                for ship_size in remaining_ships:
                    # Kiểm tra hướng ngang
                    if x + ship_size <= GRID_SIZE:
                        valid = True
                        for i in range(ship_size):
                            if x + i >= GRID_SIZE or ai_shots[y][x + i] == -1:  # Nếu gặp ô đã bắn trượt
                                valid = False
                                break
                        if valid:
                            for i in range(ship_size):
                                prob_map[y][x + i] += 1

                    # Kiểm tra hướng dọc
                    if y + ship_size <= GRID_SIZE:
                        valid = True
                        for i in range(ship_size):
                            if y + i >= GRID_SIZE or ai_shots[y + i][x] == -1:
                                valid = False
                                break
                        if valid:
                            for i in range(ship_size):
                                prob_map[y + i][x] += 1

        return prob_map

    def get_best_target(ai_shots, prob_map, last_hit, consecutive_hits):
        # Nếu có nhiều điểm trúng liên tiếp, ưu tiên tìm theo hướng của tàu
        if consecutive_hits:
            xs = [x for x, y in consecutive_hits]
            ys = [y for x, y in consecutive_hits]

            # Nếu các điểm trúng nằm trên cùng một hàng
            if all(y == ys[0] for y in ys):
                row = ys[0]
                min_x, max_x = min(xs), max(xs)
                # Thử bắn các ô tiếp theo theo hướng ngang
                if max_x + 1 < GRID_SIZE and ai_shots[row][max_x + 1] == 0:
                    return (max_x + 1, row)
                if min_x - 1 >= 0 and ai_shots[row][min_x - 1] == 0:
                    return (min_x - 1, row)

            # Nếu các điểm trúng nằm trên cùng một cột
            elif all(x == xs[0] for x in xs):
                col = xs[0]
                min_y, max_y = min(ys), max(ys)
                # Thử bắn các ô tiếp theo theo hướng dọc
                if max_y + 1 < GRID_SIZE and ai_shots[max_y + 1][col] == 0:
                    return (col, max_y + 1)
                if min_y - 1 >= 0 and ai_shots[min_y - 1][col] == 0:
                    return (col, min_y - 1)

        # Nếu có một điểm trúng đơn lẻ, ưu tiên tìm xung quanh
        if last_hit:
            lx, ly = last_hit
            # Kiểm tra 4 hướng xung quanh với trọng số cao hơn
            directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
            possible_moves = []

            for dx, dy in directions:
                nx, ny = lx + dx, ly + dy
                if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and ai_shots[ny][nx] == 0:
                    possible_moves.append((nx, ny))

            if possible_moves:
                # Ưu tiên các ô có xác suất cao
                best_moves = []
                max_prob = -1
                for x, y in possible_moves:
                    if prob_map[y][x] > max_prob:
                        max_prob = prob_map[y][x]
                        best_moves = [(x, y)]
                    elif prob_map[y][x] == max_prob:
                        best_moves.append((x, y))

                return random.choice(best_moves) if best_moves else None

        # Nếu không có điểm trúng hoặc không tìm thấy hướng tốt
        # Tìm ô có xác suất cao nhất
        max_prob = -1
        best_moves = []

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if ai_shots[y][x] == 0 and prob_map[y][x] > max_prob:
                    max_prob = prob_map[y][x]
                    best_moves = [(x, y)]
                elif ai_shots[y][x] == 0 and prob_map[y][x] == max_prob:
                    best_moves.append((x, y))

        return random.choice(best_moves) if best_moves else None

    def ai_move(ai_shots, player_grid, player_ships_locations, last_hit=None, consecutive_hits=[], tracking_targets=[]):


        if ai_level == "easy":
            # Chế độ dễ: bắn ngẫu nhiên
            while True:
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                if ai_shots[y][x] == 0:
                    return (x, y)

        elif ai_level == "normal":
            # Chế độ thường: bắn ngẫu nhiên nhưng ưu tiên các ô xung quanh khi bắn trúng
            if last_hit:
                lx, ly = last_hit
                possible_moves = []
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = lx + dx, ly + dy
                    if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and ai_shots[ny][nx] == 0:
                        possible_moves.append((nx, ny))
                if possible_moves:
                    return random.choice(possible_moves)

            # Nếu không có ô lân cận hợp lệ, bắn ngẫu nhiên
            while True:
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                if ai_shots[y][x] == 0:
                    return (x, y)

        else:  # hard mode
            # Tính toán kích thước tàu còn lại chưa bị bắn chìm
            remaining_ships = []
            for i, ship_locations in enumerate(player_ships_locations):
                if not all(ai_shots[y][x] == 1 for x, y in ship_locations):
                    ship_size = ships_data[i][0]
                    remaining_ships.append(ship_size)

            # Tạo bản đồ xác suất
            prob_map = get_ship_probability_map(ai_shots, remaining_ships)

            # Ưu tiên theo cụm tracking
            if tracking_targets:
                sorted_clusters = sorted(tracking_targets, key=lambda c: -len(c))

                for cluster in sorted_clusters:
                    xs = [x for x, y in cluster]
                    ys = [y for x, y in cluster]

                    if len(cluster) >= 2:
                        if all(y == ys[0] for y in ys):  # nằm ngang
                            row = ys[0]
                            min_x, max_x = min(xs), max(xs)
                            for dx in [-1, 1]:
                                nx = max_x + dx if dx > 0 else min_x + dx
                                if 0 <= nx < GRID_SIZE and ai_shots[row][nx] == 0:
                                    return (nx, row)
                        elif all(x == xs[0] for x in xs):  # nằm dọc
                            col = xs[0]
                            min_y, max_y = min(ys), max(ys)
                            for dy in [-1, 1]:
                                ny = max_y + dy if dy > 0 else min_y + dy
                                if 0 <= ny < GRID_SIZE and ai_shots[ny][col] == 0:
                                    return (col, ny)
                    else:
                        # Chỉ có 1 điểm, thử 4 hướng
                        x, y = cluster[0]
                        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                            nx, ny = x + dx, y + dy
                            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and ai_shots[ny][nx] == 0:
                                return (nx, ny)

            # Nếu không có cụm nghi ngờ, dùng bản đồ xác suất
            target = get_best_target(ai_shots, prob_map, last_hit, consecutive_hits)

            if target:
                return target

            # Nếu không tìm thấy mục tiêu, bắn ngẫu nhiên
            while True:
                x, y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
                if ai_shots[y][x] == 0:
                    return (x, y)

    def draw_grid(grid, offset_x, offset_y, shots, ship_locations, show_ships=False, cell_size=CELL_SIZE,
                  is_ai_grid=False, sunk_ships=None, ships_orientation=None, ships_start_pos=None):
        try:
            fire_image = pygame.image.load("assets/images/fire/fire.png").convert_alpha()
            scaled_fire = pygame.transform.scale(fire_image, (cell_size, cell_size))
            miss_image = pygame.image.load("assets/images/fire/bluetoken.png").convert_alpha()
            scaled_miss = pygame.transform.scale(miss_image, (cell_size, cell_size))

            draw_grid_with_labels(screen, offset_x, offset_y, GRID_SIZE, cell_size)


        except pygame.error as e:
            print(f"Error loading fire/miss images: {e}")
            # Tạo các hình ảnh mặc định nếu không tìm thấy file
            fire_image = pygame.Surface((cell_size, cell_size))
            fire_image.fill((255, 0, 0))
            scaled_fire = fire_image
            miss_image = pygame.Surface((cell_size, cell_size))
            miss_image.fill((0, 0, 255))
            scaled_miss = miss_image

        # try:
        #     grid_bg = pygame.image.load("assets/images/grids/grid.png").convert()
        #     scaled_bg = pygame.transform.scale(grid_bg, ((GRID_SIZE + 1) * cell_size, (GRID_SIZE + 1) * cell_size))
        #     screen.blit(scaled_bg, (offset_x, offset_y))
        # except pygame.error as e:
        #     print(f"Error loading grid background image: {e}")

        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                draw_x = offset_x + (x + 1) * cell_size
                draw_y = offset_y + (y + 1) * cell_size
                rect = pygame.Rect(draw_x, draw_y, cell_size, cell_size)
                # pygame.draw.rect(screen, GRAY, rect, 1)

        # Draw sunk ships
        if sunk_ships:
            for i, is_sunk in enumerate(sunk_ships):
                if is_sunk:
                    # Get ship info
                    ship_size = ships_data[i][0]
                    direction = ships_orientation[i]
                    start_x, start_y = ships_start_pos[i]

                    # Load destroyed ship image
                    destroyed_path_h, destroyed_path_v = ships_destroyed[i][2], ships_destroyed[i][3]
                    current_destroyed_path = destroyed_path_h if direction == "H" else destroyed_path_v

                    try:
                        ship_image = pygame.image.load(current_destroyed_path).convert_alpha()
                        scaled_ship = pygame.transform.scale(
                            ship_image,
                            (ship_size * cell_size if direction == "H" else cell_size,
                             cell_size if direction == "H" else ship_size * cell_size)
                        )
                        ship_x = offset_x + (start_x + 1) * cell_size
                        ship_y = offset_y + (start_y + 1) * cell_size
                        screen.blit(scaled_ship, (ship_x, ship_y))
                    except pygame.error as e:
                        print(f"Error loading destroyed ship image: {current_destroyed_path} - {e}")

        # Draw active ships
        if show_ships:
            for i, locations_set in enumerate(ship_locations):
                if not locations_set or sunk_ships[i]:  # Skip if ship is empty or sunk
                    continue
                ship_size = ships_data[i][0]  # Sử dụng kích thước gốc của tàu
                is_horizontal = ships_orientation[i] == "H"

                _, _, path_h, path_v = ships_data[i]
                current_image_path = path_h if is_horizontal else path_v

                try:
                    ship_image = pygame.image.load(current_image_path).convert_alpha()
                    scaled_ship = pygame.transform.scale(
                        ship_image,
                        (ship_size * cell_size if is_horizontal else cell_size,
                         cell_size if is_horizontal else ship_size * cell_size)
                    )
                    ship_x = offset_x + (ships_start_pos[i][0] + 1) * cell_size
                    ship_y = offset_y + (ships_start_pos[i][1] + 1) * cell_size
                    screen.blit(scaled_ship, (ship_x, ship_y))
                except pygame.error as e:
                    print(f"Error loading ship image: {current_image_path} - {e}")

        # Draw hits and misses over everything else
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                draw_x = offset_x + (x + 1) * cell_size
                draw_y = offset_y + (y + 1) * cell_size
                rect = pygame.Rect(draw_x, draw_y, cell_size, cell_size)
                if shots[y][x] == 1:  # Hit
                    screen.blit(scaled_fire, rect.topleft)
                elif shots[y][x] == -1:  # Miss
                    screen.blit(scaled_miss, rect.topleft)

    def draw_grid_with_labels(screen, offset_x, offset_y, grid_size, cell_size):
        font = pygame.font.Font(None, 28)
        label_color = (0, 255, 255)  # Xanh neon
        grid_bg_color = (5, 20, 60)  # Xanh đậm (giống ảnh)
        label_bg_color = (10, 30, 80)  # Nền cho vùng nhãn A–J và 1–10

        # Nền cho toàn bộ khu vực lưới (bao gồm nhãn A–J + 1–10)
        full_width = (grid_size + 1) * cell_size
        full_height = (grid_size + 1) * cell_size
        pygame.draw.rect(screen, label_bg_color, (offset_x, offset_y, full_width, full_height))

        # Nền cho từng ô
        for y in range(grid_size):
            for x in range(grid_size):
                rect = pygame.Rect(
                    offset_x + (x + 1) * cell_size,
                    offset_y + (y + 1) * cell_size,
                    cell_size,
                    cell_size
                )
                pygame.draw.rect(screen, grid_bg_color, rect)  # Nền xanh đậm
                pygame.draw.rect(screen, (255, 255, 255), rect, 1)  # Viền trắng

        # Vẽ chữ cái A–J (cột)
        for i in range(grid_size):
            label = chr(ord('A') + i)
            text = font.render(label, True, label_color)
            text_rect = text.get_rect(
                center=(
                    offset_x + (i + 1) * cell_size + cell_size // 2,
                    offset_y + cell_size // 2
                )
            )
            screen.blit(text, text_rect)

        # Vẽ số 1–10 (hàng)
        for i in range(grid_size):
            label = str(i + 1)
            text = font.render(label, True, label_color)
            text_rect = text.get_rect(
                center=(
                    offset_x + cell_size // 2,
                    offset_y + (i + 1) * cell_size + cell_size // 2
                )
            )
            screen.blit(text, text_rect)

    def placing_ships_phase(screen, ships_data, player_grid, player_ships_locations, CELL_SIZE, player_offset_x,
                            GRID_SIZE,
                            draw_text, can_place_ship, place_ship):
        placing_ships = True
        current_ship = 0
        ship_direction = "H"
        x_pos, y_pos = 0, 0
        player_ships_placed = [False] * len(ships_data)

        start_time = pygame.time.get_ticks()
        placement_time_limit = 15000  # 15 giây
        show_unfinished_message_time = 0

        logo_margin_top = 30
        grid_top = logo_margin_top + 100  # Lùi toàn bộ xuống 100px từ logo

        while placing_ships:
            try:
                background_image = pygame.image.load("assets/images/background/game.jpg").convert()
                screen.blit(background_image, (0, 0))
            except:
                screen.fill(WHITE)

            # Logo
            try:
                logo_image_original = pygame.image.load("assets/images/logo/logo_game.png").convert_alpha()
                logo_image = pygame.transform.scale(logo_image_original, (
                    logo_image_original.get_width() // 5, logo_image_original.get_height() // 5))
                logo_rect = logo_image.get_rect(center=(WIDTH // 2, logo_margin_top + logo_image.get_height() // 2))
                screen.blit(logo_image, logo_rect)
            except:
                draw_text("BATTLESHIP", WIDTH // 2 - 100, logo_margin_top + 10, WHITE)

            # Text Player (điều chỉnh vị trí)
            draw_text("PLAYER", player_offset_x + grid_pixel_width // 2, grid_top - 30, WHITE)

            # Grid
            draw_grid(player_grid, player_offset_x, grid_top, [[0] * GRID_SIZE for _ in range(GRID_SIZE)],
                      player_ships_locations, show_ships=True, cell_size=CELL_SIZE,
                      sunk_ships=player_sunk_ships, ships_orientation=player_ships_orientation,
                      ships_start_pos=player_ships_start_pos)

            # Hiển thị số tàu còn lại cần đặt
            remaining_ships = len(ships_data) - current_ship
            if remaining_ships > 0:
                draw_text(f"Remaining ships: {remaining_ships}", WIDTH - 200, HEIGHT - 50, WHITE)

            # Countdown timer
            elapsed_time = pygame.time.get_ticks() - start_time
            remaining_time = max(0, (placement_time_limit - elapsed_time) // 1000)
            draw_text(f"Time: {remaining_time}s", WIDTH - 150, 20, WHITE)

            if show_unfinished_message_time > 0 and pygame.time.get_ticks() - show_unfinished_message_time < 2000:
                draw_text("PLEASE PLACE ALL SHIPS!", WIDTH // 2 - 150, HEIGHT - 80, WHITE)

            if current_ship < len(ships_data):
                ship_size, _, path_h, path_v = ships_data[current_ship]
                current_image_path = path_h if ship_direction == "H" else path_v
                try:
                    original_image = pygame.image.load(current_image_path).convert_alpha()

                    if ship_direction == "H":
                        # For horizontal ships, draw the entire ship at once
                        scaled_ship = pygame.transform.scale(
                            original_image,
                            (ship_size * CELL_SIZE, CELL_SIZE)
                        )
                        draw_x = player_offset_x + (x_pos + 1) * CELL_SIZE
                        draw_y = grid_top + (y_pos + 1) * CELL_SIZE
                        screen.blit(scaled_ship, (draw_x, draw_y))
                    else:
                        # For vertical ships, draw the entire ship at once
                        scaled_ship = pygame.transform.scale(
                            original_image,
                            (CELL_SIZE, ship_size * CELL_SIZE)
                        )
                        draw_x = player_offset_x + (x_pos + 1) * CELL_SIZE
                        draw_y = grid_top + (y_pos + 1) * CELL_SIZE
                        screen.blit(scaled_ship, (draw_x, draw_y))
                except pygame.error as e:
                    print(f"Error loading ship image: {current_image_path} - {e}")
                    return False

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.KEYDOWN:
                    if current_ship < len(ships_data):
                        ship_size, *_ = ships_data[current_ship]
                        if event.key == pygame.K_LEFT:
                            x_pos = max(0, x_pos - 1)
                        elif event.key == pygame.K_RIGHT:
                            x_pos = min(GRID_SIZE - 1, x_pos + 1)
                        elif event.key == pygame.K_UP:
                            y_pos = max(0, y_pos - 1)
                        elif event.key == pygame.K_DOWN:
                            y_pos = min(GRID_SIZE - 1, y_pos + 1)
                        elif event.key == pygame.K_SPACE:
                            ship_direction = "V" if ship_direction == "H" else "H"
                            if ship_direction == "H":
                                x_pos = min(x_pos, GRID_SIZE - 1)
                            else:
                                y_pos = min(y_pos, GRID_SIZE - 1)
                        elif event.key == pygame.K_RETURN:
                            if can_place_ship(player_grid, x_pos, y_pos, ship_size, ship_direction):
                                coords = place_ship(player_grid, x_pos, y_pos, ship_size, ship_direction)
                                player_ships_locations[current_ship] = set(coords)
                                player_ships_placed[current_ship] = True
                                player_ships_orientation[current_ship] = ship_direction
                                player_ships_start_pos[current_ship] = (x_pos, y_pos)
                                current_ship += 1
                                if current_ship >= len(ships_data):
                                    return True

            # Nếu hết thời gian, tự động đặt các tàu còn lại
            if elapsed_time >= placement_time_limit and current_ship < len(ships_data):
                # Hiển thị thông báo đang random đặt tàu
                draw_text("Auto placing remaining ships...", WIDTH // 2 - 150, HEIGHT // 2, WHITE)
                pygame.display.flip()

                while current_ship < len(ships_data):
                    ship_size = ships_data[current_ship][0]
                    placed = False
                    attempts = 0
                    while not placed and attempts < 100:
                        # Random vị trí và hướng
                        x = random.randint(0, GRID_SIZE - ship_size)
                        y = random.randint(0, GRID_SIZE - ship_size)
                        direction = random.choice(["H", "V"])

                        if can_place_ship(player_grid, x, y, ship_size, direction):
                            coords = place_ship(player_grid, x, y, ship_size, direction)
                            player_ships_locations[current_ship] = set(coords)
                            player_ships_placed[current_ship] = True
                            player_ships_orientation[current_ship] = direction
                            player_ships_start_pos[current_ship] = (x, y)
                            placed = True
                        attempts += 1

                    if not placed:
                        print(f"Could not place ship {current_ship}")
                        return False
                    current_ship += 1

                    # Vẽ lại màn hình sau mỗi lần đặt tàu
                    screen.blit(background_image, (0, 0))
                    draw_grid(player_grid, player_offset_x, grid_top, [[0] * GRID_SIZE for _ in range(GRID_SIZE)],
                              player_ships_locations, show_ships=True, cell_size=CELL_SIZE,
                              sunk_ships=player_sunk_ships,
                              ships_orientation=player_ships_orientation,
                              ships_start_pos=player_ships_start_pos)
                    pygame.display.flip()
                    pygame.time.wait(500)  # Đợi 0.5 giây giữa mỗi lần đặt tàu
                return True

            pygame.display.flip()
        return True

    def add_to_tracking_targets(tracking_targets, hit_coord):
        for cluster in tracking_targets:
            if any(abs(hit_coord[0] - x) + abs(hit_coord[1] - y) == 1 for x, y in cluster):
                cluster.append(hit_coord)
                return
        tracking_targets.append([hit_coord])

    def remove_cluster_with_sunk(tracking_targets, ship_cells):
        tracking_targets[:] = [cluster for cluster in tracking_targets if
                               not all(cell in ship_cells for cell in cluster)]

    def game_loop(screen, player_grid, ai_grid, player_shots, ai_shots, player_ships_locations, ai_ships_locations,
                  ships_data, CELL_SIZE, player_offset_x, ai_offset_x, GRID_SIZE, WIDTH, HEIGHT, draw_text, handle_shot,
                  ai_move):
        running = True
        player_turn = True
        game_over = False
        winner = None

        # Tải trước ảnh victory và defeat
        try:
            victory_img = pygame.image.load("assets/images/logo/victory.png").convert_alpha()
            defeat_img = pygame.image.load("assets/images/logo/defeat.png").convert_alpha()
            # Scale ảnh để vừa với màn hình
            result_width = 400  # Điều chỉnh kích thước theo ý muốn
            victory_height = int(result_width * (victory_img.get_height() / victory_img.get_width()))
            defeat_height = int(result_width * (defeat_img.get_height() / defeat_img.get_width()))
            victory_img = pygame.transform.scale(victory_img, (result_width, victory_height))
            defeat_img = pygame.transform.scale(defeat_img, (result_width, defeat_height))
        except Exception as e:
            print(f"Error loading result images: {e}")
            victory_img = None
            defeat_img = None

        # Chế độ test (bỏ comment dòng dưới để test giao diện thắng/thua)
        # game_over, winner = True, "Player"  # hoặc "AI" để test màn hình thua

        logo_margin_top = 30
        grid_top = logo_margin_top + 100

        ai_last_hit = None
        ai_consecutive_hits = []
        # Mỗi phần tử là một danh sách các tọa độ nghi ngờ cùng thuộc một tàu
        tracking_targets = []  # Danh sách các cụm điểm nghi ngờ
        delay_time = 1.5
        # Track which ships have been sunk
        player_sunk_ships = [False] * len(ships_data)
        ai_sunk_ships = [False] * len(ships_data)
        last_turn_time = 0

        while running:
            current_time = time.time()
            try:
                background = pygame.image.load("assets/images/background/game.jpg").convert()
                screen.blit(background, (0, 0))
            except:
                screen.fill((255, 255, 255))  # WHITE

            def draw_game_info(screen, grid_size, ship_count, difficulty):
                font = pygame.font.Font(None, 21)
                text_color = (255, 255, 255)  # Trắng

                lines = [
                    f"GRID: {grid_size}x{grid_size}",
                    f"SHIPS: {ship_count}",
                    f"MODE: {difficulty.upper()}",
                ]

                x, y = 15, 15  # Góc trên bên trái

                for i, line in enumerate(lines):
                    text_surf = font.render(line, True, text_color)
                    screen.blit(text_surf, (x, y + i * (font.get_height() + 4)))

            # Logo
            try:
                logo_img = pygame.image.load("assets/images/logo/logo_game.png").convert_alpha()
                logo_img = pygame.transform.scale(logo_img, (logo_img.get_width() // 5, logo_img.get_height() // 5))
                logo_rect = logo_img.get_rect(center=(WIDTH // 2, logo_margin_top + logo_img.get_height() // 2))
                screen.blit(logo_img, logo_rect)
            except:
                draw_text("BATTLESHIP", WIDTH // 2 - 100, logo_margin_top + 10, (255, 255, 255))  # WHITE

            if not game_over:
                # Điều chỉnh vị trí text Player và Computer
                draw_text("PLAYER", player_offset_x + grid_pixel_width // 2, grid_top - 30, WHITE)
                draw_text("COMPUTER", ai_offset_x + grid_pixel_width // 2, grid_top - 30, WHITE)
                draw_game_info(screen, GRID_SIZE, SHIP_COUNT, ai_level)

                # Draw player grid
                draw_grid(player_grid, player_offset_x, grid_top, ai_shots, player_ships_locations, show_ships=True,
                          cell_size=CELL_SIZE, sunk_ships=player_sunk_ships,
                          ships_orientation=player_ships_orientation,
                          ships_start_pos=player_ships_start_pos)

                # Draw AI grid
                draw_grid(ai_grid, ai_offset_x, grid_top, player_shots, ai_ships_locations,
                          show_ships=False, cell_size=CELL_SIZE, sunk_ships=ai_sunk_ships,
                          ships_orientation=ai_ships_orientation, ships_start_pos=ai_ships_start_pos)

                # Kiểm tra nếu tất cả các tàu đã bị đánh chìm
                if all(ai_sunk_ships):
                    game_over = True
                    winner = "Player"
                elif all(player_sunk_ships):
                    game_over = True
                    winner = "AI"

            else:
                # Vẽ background mờ
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.fill((0, 0, 0))
                overlay.set_alpha(128)  # Độ trong suốt 50%
                screen.blit(overlay, (0, 0))

                if winner == "Player":
                    if victory_img:
                        result_rect = victory_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        screen.blit(victory_img, result_rect)
                else:
                    if defeat_img:
                        result_rect = defeat_img.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                        screen.blit(defeat_img, result_rect)
                pygame.display.flip()

                # Hiển thị thông báo "Press ENTER to play again, ESC to exit"
                text = "Press ENTER to play again, ESC to exit"
                text_render = pygame.font.Font(None, 36).render(text, True, (255, 255, 255))
                text_rect = text_render.get_rect(center=(WIDTH // 2, HEIGHT - 100))
                screen.blit(text_render, text_rect)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif not game_over and event.type == pygame.MOUSEBUTTONDOWN and player_turn and (
                        current_time - last_turn_time >= delay_time):
                    mx, my = event.pos
                    # Tính toán vị trí click chính xác hơn
                    if ai_offset_x + CELL_SIZE <= mx < ai_offset_x + CELL_SIZE + GRID_SIZE * CELL_SIZE and \
                            grid_top + CELL_SIZE <= my < grid_top + CELL_SIZE + GRID_SIZE * CELL_SIZE:
                        gx = (mx - ai_offset_x - CELL_SIZE) // CELL_SIZE
                        gy = (my - grid_top - CELL_SIZE) // CELL_SIZE
                        if 0 <= gx < GRID_SIZE and 0 <= gy < GRID_SIZE and player_shots[gy][gx] == 0:
                            hit, sunk, ship_idx = handle_shot(ai_grid, player_shots, ai_ships_locations, gx, gy)
                            last_turn_time = current_time

                            if sunk and ship_idx >= 0:
                                ai_sunk_ships[ship_idx] = True

                            if not hit:
                                player_turn = False

                elif game_over:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            return True  # Quay lại chơi lại
                        elif event.key == pygame.K_ESCAPE:
                            return False

            if not game_over and not player_turn and (current_time - last_turn_time >= delay_time):
                ai_target = ai_move(ai_shots, player_grid, player_ships_locations, ai_last_hit, ai_consecutive_hits,
                                    tracking_targets)
                if ai_target:
                    ax, ay = ai_target
                    hit, sunk, ship_idx = handle_shot(player_grid, ai_shots, player_ships_locations, ax, ay)
                    last_turn_time = current_time
                    if hit:
                        print(f"AI hit your ship at {ax}, {ay}!")
                        ai_last_hit = (ax, ay)
                        ai_consecutive_hits.append((ax, ay))
                        add_to_tracking_targets(tracking_targets, (ax, ay))

                        if sunk and ship_idx >= 0:
                            print("AI destroyed your ship!")

                            player_sunk_ships[ship_idx] = True
                            ai_last_hit = None
                            ai_consecutive_hits = []
                            remove_cluster_with_sunk(tracking_targets, player_ships_locations[ship_idx])

                    else:
                        print(f"AI missed at {ax}, {ay}.")
                        ai_last_hit = None
                        ai_consecutive_hits = []
                        player_turn = True

            pygame.display.flip()

    player_grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    ai_grid, ai_ships_locations = ai_place_ships()
    player_ships_locations = [set() for _ in ships_data]

    if not placing_ships_phase(screen, ships_data, player_grid, player_ships_locations, CELL_SIZE,
                               player_offset_x, GRID_SIZE, draw_text, can_place_ship, place_ship):
        return

    player_shots = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    ai_shots = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]

    game_loop(screen, player_grid, ai_grid, player_shots, ai_shots, player_ships_locations, ai_ships_locations,
              ships_data, CELL_SIZE, player_offset_x, ai_offset_x, GRID_SIZE, WIDTH, HEIGHT,
              draw_text, handle_shot, ai_move)


if __name__ == "__main__":
    start_game(GRID_SIZE, SHIP_COUNT, ai_level)
