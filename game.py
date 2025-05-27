import pygame
import sys
import random

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Coconut Catching Game 🥥 - Impossible Mode")

# Load images
try:
    background_raw = pygame.image.load("assets/background.jpg").convert()
    basket_img = pygame.image.load("assets/basket.png").convert_alpha()
    monkey_img = pygame.image.load("assets/monkey.png").convert_alpha()
    coconut_img = pygame.image.load("assets/coconut.png").convert_alpha()
except pygame.error as e:
    print(f"Error loading image: {e}")
    pygame.quit()
    sys.exit()

# Scale background
def scale_background(img, screen_width, screen_height):
    img_w, img_h = img.get_size()
    scale = min(screen_width / img_w, screen_height / img_h)
    new_size = (int(img_w * scale), int(img_h * scale))
    scaled_img = pygame.transform.scale(img, new_size)
    x = (screen_width - new_size[0]) // 2
    y = (screen_height - new_size[1]) // 2
    return scaled_img, x, y

background, bg_x, bg_y = scale_background(background_raw, WIDTH, HEIGHT)

# Resize sprites
basket_img = pygame.transform.scale(basket_img, (120, 80))
monkey_img = pygame.transform.smoothscale(monkey_img, (150, 200))
coconut_img = pygame.transform.scale(coconut_img, (40, 40))

# Colors
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MENU_BG = (0, 0, 0, 180)
HOVER_COLOR = (0, 100, 0, 150)
SHADOW = (0, 0, 0, 150)

# Fonts
font = pygame.font.SysFont('Arial', 24, bold=True)
menu_font = pygame.font.SysFont('Arial', 30, bold=True)

# UI Elements
stage_button_rects = [pygame.Rect(10, 10 + i*40, 120, 30) for i in range(3)]
score_rect = pygame.Rect(WIDTH//2 - 100, 10, 200, 30)
pause_menu_rect = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 150, 400, 300)

# Game state
in_game = False
paused = False
show_about = False
current_stage = None
score = 0
selected_option = 0

difficulty_options = ["Noob", "Pro", "Master"]
menu_options = ["Resume", "Restart", "About Us", "Exit"]
spawn_intervals = [1500, 1000, 400]  # Master drops faster

# Player
unit_x = WIDTH // 2
move_speed = 7
ground_y = HEIGHT - 80

# Basket position
basket_offset_x = 60
basket_base_y = ground_y - 80
basket_y = basket_base_y

# Monkey position
monkey_offset_x = -40
monkey_base_y = ground_y - 200
monkey_y = monkey_base_y

# Jumping
vertical_velocity = 0
jump_power = -15
gravity = 1
is_jumping = False

# Coconut logic
coconuts = []
coconut_speed = 5
SPAWN_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SPAWN_EVENT, 1500)

# Functions
def draw_grass():
    pygame.draw.rect(screen, GREEN, (0, ground_y, WIDTH, 80))

def draw_score():
    text = font.render(f"Score: {score}", True, WHITE)
    shadow = font.render(f"Score: {score}", True, SHADOW)
    screen.blit(shadow, (score_rect.x + 2, score_rect.y + 2))
    screen.blit(text, score_rect.topleft)

def draw_stage_selector():
    mouse_pos = pygame.mouse.get_pos()
    for i, rect in enumerate(stage_button_rects):
        color = HOVER_COLOR if rect.collidepoint(mouse_pos) else MENU_BG
        pygame.draw.rect(screen, color, rect, border_radius=6)
        label = font.render(difficulty_options[i], True, WHITE)
        screen.blit(label, (rect.x + 10, rect.y + 5))

def show_pause_menu():
    menu_surface = pygame.Surface(pause_menu_rect.size, pygame.SRCALPHA)
    menu_surface.fill(MENU_BG)
    screen.blit(menu_surface, pause_menu_rect.topleft)

    title = menu_font.render("Paused", True, WHITE)
    screen.blit(title, (pause_menu_rect.centerx - title.get_width()//2, pause_menu_rect.top + 20))

    mouse_pos = pygame.mouse.get_pos()
    for i, option in enumerate(menu_options):
        opt_rect = pygame.Rect(pause_menu_rect.left + 60, pause_menu_rect.top + 80 + i*50, 280, 40)
        if opt_rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, HOVER_COLOR, opt_rect, border_radius=6)
        color = WHITE if i == selected_option else (180, 180, 180)
        text = font.render(option, True, color)
        screen.blit(text, (opt_rect.x + 10, opt_rect.y + 10))

def show_about_screen():
    screen.fill(BLACK)
    lines = [
        "Coconut Catching Game 🥥",
        "Created by Manav",
        "",
        "Catch falling coconuts!",
        "Use A/D or arrow keys to move",
        "Click stage selector to change difficulty",
        "Press SPACE to jump",
        "",
        "In Master mode, good luck...",
        "",
        "Press ESC to return..."
    ]
    for i, line in enumerate(lines):
        rendered = menu_font.render(line, True, WHITE)
        screen.blit(rendered, (WIDTH//2 - rendered.get_width()//2, 100 + i * 35))

def reset_game(stage_index):
    global score, coconuts, unit_x, coconut_speed, in_game, basket_y, monkey_y, vertical_velocity, is_jumping
    score = 0
    coconuts.clear()
    unit_x = WIDTH // 2
    basket_y = basket_base_y
    monkey_y = monkey_base_y
    vertical_velocity = 0
    is_jumping = False
    pygame.time.set_timer(SPAWN_EVENT, spawn_intervals[stage_index])
    
    if stage_index == 0:
        coconut_speed = 5
    elif stage_index == 1:
        coconut_speed = 10
    elif stage_index == 2:
        coconut_speed = random.randint(18, 30)  # Extreme speed!
    
    in_game = True

# Main loop
clock = pygame.time.Clock()
running = True

while running:
    if show_about:
        show_about_screen()
    else:
        screen.fill(BLACK)
        screen.blit(background, (bg_x, bg_y))
        draw_grass()

        if in_game and not paused:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                unit_x -= move_speed
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                unit_x += move_speed
            unit_x = max(100, min(unit_x, WIDTH - 100))
            unit_x = pygame.mouse.get_pos()[0]
            if keys[pygame.K_SPACE] and not is_jumping:
                vertical_velocity = jump_power
                is_jumping = True

        if is_jumping:
            vertical_velocity += gravity
            basket_y += vertical_velocity
            monkey_y += vertical_velocity
            if basket_y >= basket_base_y:
                basket_y = basket_base_y
                monkey_y = monkey_base_y
                vertical_velocity = 0
                is_jumping = False

        basket_pos = (unit_x - basket_offset_x, basket_y)
        monkey_pos = (unit_x + monkey_offset_x, monkey_y)
        screen.blit(monkey_img, monkey_pos)
        screen.blit(basket_img, basket_pos)

        draw_stage_selector()
        draw_score()

        if in_game and not paused:
            for c in coconuts[:]:
                speed = 0
                if current_stage == 0:
                    speed = 5
                elif current_stage == 1:
                    speed = 10
                elif current_stage == 2:
                    speed = random.randint(20, 40)  # INSANE SPEED!

                c[1] += speed
                basket_rect = pygame.Rect(basket_pos[0], basket_pos[1],
                                         basket_img.get_width(), basket_img.get_height())
                coconut_rect = pygame.Rect(c[0], c[1],
                                           coconut_img.get_width(), coconut_img.get_height())

                if basket_rect.colliderect(coconut_rect):
                    coconuts.remove(c)
                    score += 1
                elif c[1] > HEIGHT:
                    coconuts.remove(c)
                else:
                    screen.blit(coconut_img, c)

        if paused:
            show_pause_menu()

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if show_about:
                    show_about = False
                    paused = True
                elif in_game:
                    paused = not paused

            if paused:
                if event.key == pygame.K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == pygame.K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == pygame.K_RETURN:
                    choice = menu_options[selected_option]
                    if choice == "Resume":
                        paused = False
                    elif choice == "Restart":
                        reset_game(current_stage)
                        paused = False
                    elif choice == "About Us":
                        show_about = True
                        paused = False
                    elif choice == "Exit":
                        running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not in_game and not show_about:
                for i, rect in enumerate(stage_button_rects):
                    if rect.collidepoint(event.pos):
                        current_stage = i
                        reset_game(i)
                        break
            elif paused:
                for i, option in enumerate(menu_options):
                    opt_rect = pygame.Rect(pause_menu_rect.left + 60,
                                           pause_menu_rect.top + 80 + i*50, 280, 40)
                    if opt_rect.collidepoint(event.pos):
                        selected_option = i
                        choice = menu_options[i]
                        if choice == "Resume":
                            paused = False
                        elif choice == "Restart":
                            reset_game(current_stage)
                            paused = False
                        elif choice == "About Us":
                            show_about = True
                            paused = False
                        elif choice == "Exit":
                            running = False

        elif event.type == SPAWN_EVENT and in_game and not paused and not show_about:
            x = random.randint(40, WIDTH - 60)
            coconuts.append([x, -40])

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()