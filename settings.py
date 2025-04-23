import pygame
import Menu
def start_settings():
    pygame.init()
    pygame.mixer.init()

    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Battleship - Settings")

    # Màu sắc
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    NAVY_BLUE = (0, 48, 73)
    HOVER_BLUE = (0, 80, 120)
    GOLD = (255, 215, 0)
    TEXT_GOLD = (255, 215, 0)

    # Font chữ
    try:
        title_font = pygame.font.Font("assets/fonts/Debrosee-ALPnL.ttf", 72)
        button_font = pygame.font.Font("assets/fonts/Arial.ttf", 24)
    except:
        title_font = pygame.font.Font(None, 72)
        button_font = pygame.font.Font(None, 24)

    # Tải ảnh nền
    try:
        background_image = pygame.image.load("assets/images/background/game.jpg").convert()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))  # Màu đen với độ trong suốt 50%
    except:
        background_image = None
        overlay = None

    # Tải âm thanh
    try:
        click_sound = pygame.mixer.Sound("assets/sounds/click.wav")
        click_sound.set_volume(0.5)
        hover_sound = pygame.mixer.Sound("assets/sounds/hover.wav")
        hover_sound.set_volume(0.3)
    except:
        click_sound = None
        hover_sound = None

    # Các tùy chọn
    grid_sizes = [(5, "5x5"), (8, "8x8"), (10, "10x10")]
    ship_counts = [(2, "2 ships"), (3, "3 ships"), (4, "4 ships")]
    difficulty_levels = [("easy", "EASY"), ("normal", "NORMAL"), ("hard", "HARD")]

    # Tạo các nút
    button_width, button_height = 140, 45  # Giảm kích thước nút
    spacing = 20
    vertical_spacing = 60  # Tăng khoảng cách giữa các nhóm
    start_y = 180  # Bắt đầu thấp hơn một chút

    # Nút kích thước bảng (nằm ngang)
    grid_buttons = []
    total_width = (button_width + spacing) * len(grid_sizes) - spacing
    start_x = (WIDTH - total_width) // 2
    for i, (size, text) in enumerate(grid_sizes):
        button = pygame.Rect(
            start_x + i * (button_width + spacing),
            start_y,
            button_width,
            button_height
        )
        grid_buttons.append((button, size, text))

    # Nút số lượng tàu (nằm ngang)
    ship_buttons = []
    total_width = (button_width + spacing) * len(ship_counts) - spacing
    start_x = (WIDTH - total_width) // 2
    for i, (count, text) in enumerate(ship_counts):
        button = pygame.Rect(
            start_x + i * (button_width + spacing),
            start_y + button_height + vertical_spacing,
            button_width,
            button_height
        )
        ship_buttons.append((button, count, text))

    # Nút chế độ chơi (nằm ngang)
    difficulty_buttons = []
    total_width = (button_width + spacing) * len(difficulty_levels) - spacing
    start_x = (WIDTH - total_width) // 2
    for i, (level, text) in enumerate(difficulty_levels):
        button = pygame.Rect(
            start_x + i * (button_width + spacing),
            start_y + 2 * (button_height + vertical_spacing),
            button_width,
            button_height
        )
        difficulty_buttons.append((button, level, text))

    # Nút back
    back_button = pygame.Rect(WIDTH // 2 - button_width // 2, 
                            start_y + 3 * (button_height + vertical_spacing), 
                            button_width, 
                            button_height)

    # Biến để lưu lựa chọn
    selected_grid_size = 10  # Mặc định
    selected_ship_count = 4  # Mặc định
    selected_difficulty = "normal"  # Mặc định

    def draw_button(button, text, default_color, hover_color, is_selected=False):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button.collidepoint(mouse_pos)
        color = hover_color if is_hovered else default_color

        pygame.draw.rect(screen, color, button, border_radius=12)
        pygame.draw.rect(screen, WHITE, button, 2, border_radius=12)

        if is_hovered or is_selected:
            pygame.draw.rect(screen, GOLD, button, 3, border_radius=12)

        # Đảm bảo text là str
        if not isinstance(text, str):
            text = str(text)

        text_render = button_font.render(text, True, WHITE)
        text_rect = text_render.get_rect(center=button.center)
        screen.blit(text_render, text_rect)

    running = True
    while running:
        # Vẽ nền
        if background_image:
            screen.blit(background_image, (0, 0))
            if overlay:
                screen.blit(overlay, (0, 0))
        else:
            screen.fill(BLACK)

        # Tiêu đề
        title_text = title_font.render("SETTINGS", True, GOLD)
        title_rect = title_text.get_rect(center=(WIDTH // 2, 80))
        screen.blit(title_text, title_rect)

        # Vẽ tiêu đề cho các phần
        grid_title = button_font.render("Grid Size", True, WHITE)
        grid_title_rect = grid_title.get_rect(center=(WIDTH // 2, start_y - 30))
        screen.blit(grid_title, grid_title_rect)

        ship_title = button_font.render("Number of Ships", True, WHITE)
        ship_title_rect = ship_title.get_rect(center=(WIDTH // 2, start_y + button_height + vertical_spacing - 30))
        screen.blit(ship_title, ship_title_rect)

        difficulty_title = button_font.render("Difficulty", True, WHITE)
        difficulty_title_rect = difficulty_title.get_rect(center=(WIDTH // 2, start_y + 2 * (button_height + vertical_spacing) - 30))
        screen.blit(difficulty_title, difficulty_title_rect)

        # Vẽ các nút kích thước bảng
        for button, size, text in grid_buttons:
            draw_button(button, text, NAVY_BLUE, HOVER_BLUE, size == selected_grid_size)

        # Vẽ các nút số lượng tàu
        for button, count, text in ship_buttons:
            draw_button(button, text, NAVY_BLUE, HOVER_BLUE, count == selected_ship_count)

        # Vẽ các nút chế độ chơi
        for button, level, text in difficulty_buttons:
            draw_button(button, text, NAVY_BLUE, HOVER_BLUE, level == selected_difficulty)

        # Vẽ nút back
        draw_button(back_button, "BACK", NAVY_BLUE, HOVER_BLUE)

        # Kiểm tra hover và phát âm thanh
        mouse_pos = pygame.mouse.get_pos()
        for button, size, text in grid_buttons:
            if button.collidepoint(mouse_pos) and hover_sound:
                hover_sound.play()
                break
        for button, count, text in ship_buttons:
            if button.collidepoint(mouse_pos) and hover_sound:
                hover_sound.play()
                break
        for button, level, text in difficulty_buttons:
            if button.collidepoint(mouse_pos) and hover_sound:
                hover_sound.play()
                break
        if back_button.collidepoint(mouse_pos) and hover_sound:
            hover_sound.play()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if click_sound:
                    click_sound.play()

                # Kiểm tra các nút kích thước bảng
                for button, size, text in grid_buttons:
                    if button.collidepoint(event.pos):
                        selected_grid_size = size

                # Kiểm tra các nút số lượng tàu
                for button, count, text in ship_buttons:
                    if button.collidepoint(event.pos):
                        selected_ship_count = count

                # Kiểm tra các nút chế độ chơi
                for button, level, text in difficulty_buttons:
                    if button.collidepoint(event.pos):
                        selected_difficulty = level

                # Kiểm tra nút back
                if back_button.collidepoint(event.pos):
                    # pygame.quit()
                    return selected_grid_size, selected_ship_count, selected_difficulty

        pygame.display.flip()

    pygame.quit()
    return selected_grid_size, selected_ship_count, selected_difficulty


if __name__ == '__main__':
    start_settings()
