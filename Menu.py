import pygame
import BattleShip
import Guide
import settings
import os
GRID_SIZE = 10
SHIP_COUNT = 4
DIFFICULTY = "normal"

def main_menu():
    global GRID_SIZE, SHIP_COUNT, DIFFICULTY
    # Khởi tạo pygame
    pygame.init()
    pygame.mixer.init()

    # Kích thước màn hình
    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Battleship - Menu")

    # Màu sắc
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    # Màu nút chính - xanh dương hải quân
    NAVY_BLUE = (0, 48, 73)
    # Màu viền và highlight
    GOLD = (255, 215, 0)
    # Màu hover
    HOVER_BLUE = (0, 80, 120)
    # Màu text
    # Màu text
    TEXT_GOLD = (255, 215, 0)

    pygame.mixer.music.load("assets/sounds/battle.wav")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play(-1, 0.0)
    # Font chữ
    try:
        title_font = pygame.font.Font("assets/fonts/Debrosee-ALPnL.ttf", 72)
        button_font = pygame.font.Font("assets/fonts/Debrosee-ALPnL.ttf", 36)
    except:
        title_font = pygame.font.Font(None, 72)
        button_font = pygame.font.Font(None, 36)

    # Tải ảnh nền menu
    try:
        background_image = pygame.image.load("assets/images/background/game.jpg").convert()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))
        # Tạo hiệu ứng mờ cho background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        # overlay.fill((0, 0, 0, 128))  # Màu đen với độ trong suốt 50%

        # Tải logo
        logo_image = pygame.image.load("assets/images/logo/logo_game.png").convert_alpha()
        # Scale logo với tỷ lệ phù hợp
        logo_width = 300  # Điều chỉnh kích thước theo ý muốn
        logo_height = int(logo_width * (logo_image.get_height() / logo_image.get_width()))
        logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
    except:
        background_image = None
        overlay = None
        logo_image = None

    # Tải âm thanh
    try:
        click_sound = pygame.mixer.Sound("assets/sounds/click.wav")
        hover_sound = pygame.mixer.Sound("assets/sounds/hover.wav")
        background_music = pygame.mixer.Sound("assets/sounds/battle.wav")
        background_music.play(-1)  # Phát lặp lại
    except:
        click_sound = None
        hover_sound = None
        background_music = None

    # Tạo các nút menu
    button_width, button_height = 300, 70
    start_button = pygame.Rect(WIDTH // 2 - button_width // 2, 260, button_width, button_height)
    guide_button = pygame.Rect(WIDTH // 2 - button_width // 2, 350, button_width, button_height)
    settings_button = pygame.Rect(WIDTH // 2 - button_width // 2, 440, button_width, button_height)

    # Biến để kiểm tra hover
    last_hovered = None

    def draw_button(button, text, default_color, hover_color, icon=None):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = button.collidepoint(mouse_pos)
        color = hover_color if is_hovered else default_color

        # Vẽ nút với hiệu ứng bo góc
        pygame.draw.rect(screen, color, button, border_radius=12)

        # Vẽ viền trắng cho tất cả các nút
        pygame.draw.rect(screen, WHITE, button, 2, border_radius=12)
        # Vẽ viền nút khi hover
        if is_hovered:
            pygame.draw.rect(screen, GOLD, button, 3, border_radius=12)

        # Vẽ icon nếu có
        if icon:
            icon_rect = icon.get_rect(center=(button.left + 40, button.centery))
            screen.blit(icon, icon_rect)

        # Vẽ text
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

        if logo_image:
            logo_rect = logo_image.get_rect(center=(WIDTH // 2, 100))
            screen.blit(logo_image, logo_rect)
        else:
            title_text = title_font.render("BATTLESHIP", True, GOLD)
            title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
            screen.blit(title_text, title_rect)

        # Vẽ subtitle
        subtitle_text = button_font.render("MENU", True, WHITE)
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, 170))
        screen.blit(subtitle_text, subtitle_rect)

        draw_button(start_button, "PLAY GAME", NAVY_BLUE, HOVER_BLUE)
        draw_button(guide_button, "GUIDE", NAVY_BLUE, HOVER_BLUE)
        draw_button(settings_button, "SETTINGS", NAVY_BLUE, HOVER_BLUE)

        # Kiểm tra hover và phát âm thanh
        mouse_pos = pygame.mouse.get_pos()
        current_hovered = None
        if start_button.collidepoint(mouse_pos):
            current_hovered = "start"
        elif guide_button.collidepoint(mouse_pos):
            current_hovered = "guide"
        elif settings_button.collidepoint(mouse_pos):
            current_hovered = "settings"

        if current_hovered != last_hovered and hover_sound:
            hover_sound.play()
        last_hovered = current_hovered

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if click_sound:
                    click_sound.play()
                if start_button.collidepoint(event.pos):
                    try:
                        # Cập nhật giá trị trong BattleShip trước khi bắt đầu game
                        BattleShip.start_game(GRID_SIZE, SHIP_COUNT, DIFFICULTY)
                    except AttributeError:
                        print("Error: BattleShip.py does not have a start_game() function.")
                elif guide_button.collidepoint(event.pos):
                    try:
                        Guide.start_guide()
                    except AttributeError:
                        print("Error: Guide.py does not have a start_guide() function.")
                elif settings_button.collidepoint(event.pos):
                    try:
                        # Lấy cài đặt mới từ settings
                        new_grid_size, new_ship_count, new_difficulty = settings.start_settings()
                        # Cập nhật biến toàn cục
                        GRID_SIZE = new_grid_size
                        SHIP_COUNT = new_ship_count
                        DIFFICULTY = new_difficulty
                    except AttributeError:
                        print("Error: settings.py does not have a start_settings() function.")

        pygame.display.flip()

        if background_music:
            pygame.mixer.music.stop()
    pygame.quit()

if __name__ == '__main__':
    main_menu()
