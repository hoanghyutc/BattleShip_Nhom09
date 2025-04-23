import pygame
import Menu

def start_guide():
    pygame.init()

    WIDTH, HEIGHT = 900, 600
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Hướng dẫn chơi - Battleship")

    # Màu sắc
    WHITE = (255, 255, 255)
    NAVY_BLUE = (0, 48, 73)
    HOVER_BLUE = (0, 80, 120)
    GOLD = (255, 215, 0)

    # Font chữ
    font = pygame.font.Font("assets/fonts/Debrosee-ALPnL.ttf", 35)

    # Tải ảnh nền và ảnh hướng dẫn
    try:
        background_image = pygame.image.load("assets/images/background/game.jpg").convert()
        background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

        guide_image = pygame.image.load("assets/images/background/guide.png").convert_alpha()
        guide_width = 700
        guide_height = int(guide_width * (guide_image.get_height() / guide_image.get_width()))
        guide_image = pygame.transform.scale(guide_image, (guide_width, guide_height))

        guide_background = pygame.Surface((guide_width + 40, guide_height + 40), pygame.SRCALPHA)
        guide_background.fill((255, 255, 255, 200))  # Trắng mờ
    except Exception as e:
        print(f"Error loading images: {e}")
        background_image = None
        guide_image = None

    # Nút Back
    button_width, button_height = 200, 50
    back_button = pygame.Rect(50, HEIGHT - 80, button_width, button_height)

    def draw_button(button, text):
        mouse_pos = pygame.mouse.get_pos()
        hover = button.collidepoint(mouse_pos)
        color = HOVER_BLUE if hover else NAVY_BLUE
        pygame.draw.rect(screen, color, button, border_radius=10)
        pygame.draw.rect(screen, WHITE, button, 2, border_radius=10)
        if hover:
            pygame.draw.rect(screen, GOLD, button, 3, border_radius=12)
        text_render = font.render(text, True, WHITE)
        text_rect = text_render.get_rect(center=button.center)
        screen.blit(text_render, text_rect)

    running = True
    while running:
        if background_image:
            screen.blit(background_image, (0, 0))
        else:
            screen.fill(WHITE)

        # Vẽ ảnh hướng dẫn trực tiếp, không có nền mờ
        if guide_image:
            guide_rect = guide_image.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(guide_image, guide_rect)

        # Vẽ nút Back
        draw_button(back_button, "Back")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    running = False
                    Menu.main_menu()

        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    start_guide()
