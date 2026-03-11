import pygame
import sys
import random
import math

# --- 1. CORE INITIALIZATION ---
pygame.init()
WIDTH = 1200
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("VOLT JUMP: THE COMPLETE JIBAN KRISHNA MANNA EDITION")

# --- 2. THE COMPLETE COLOR PALETTE ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 0, 0)
CYAN = (0, 255, 255)
GOLD = (255, 215, 0)
ROAD_GREY = (50, 50, 50)
SKY_DAY = (135, 206, 235)
SKY_EVENING = (255, 140, 0)
SKY_NIGHT = (20, 25, 50)
SUN_YELLOW = (255, 255, 120)
MOON_WHITE = (240, 240, 240)
MTN_DARK = (60, 60, 80)
TREE_BROWN = (100, 70, 40)
TREE_GREEN = (34, 139, 34)

# --- 3. TYPOGRAPHY (FONTS) ---
font_ui = pygame.font.SysFont("Arial", 30, bold=True)
font_dev = pygame.font.SysFont("Arial", 22, bold=True, italic=True)
font_big = pygame.font.SysFont("Impact", 95)

# --- 4. GLOBAL GAME STATE VARIABLES ---
player_x = 160
player_y = HEIGHT - 150
y_velocity = 0
gravity = 0.98
jump_power = -21
on_ground = True
animation_timer = 0

score = 0           # Distance in meters
energy = 0          # Coins collected
current_speed = 10.5 # Initial running speed
game_active = True

# Obstacle Containers
cars = []
birds = []
coins = []

# SMART SPAWN CONTROL (The Fix for the Bird/Car overlap)
car_spawn_timer = 0
bird_spawn_timer = 0
safe_gap_timer = 0 # Prevents both spawning at once

# Scenery Elements
mountains = [[i * 400, random.randint(200, 350)] for i in range(4)]
trees = [[i * 300, 480] for i in range(5)]

# --- 5. THE MASTER GAME LOOP ---
while True:
    # --- A. SKY DYNAMICS (DAY-NIGHT FEATURE) ---
    if score < 450:
        current_sky = SKY_DAY
        celestial_color = SUN_YELLOW
        celestial_pos = (WIDTH - 150, 100)
    elif score < 900:
        current_sky = SKY_EVENING
        celestial_color = (255, 120, 60)
        celestial_pos = (WIDTH - 150, 130)
    else:
        current_sky = SKY_NIGHT
        celestial_color = MOON_WHITE
        celestial_pos = (WIDTH - 150, 80)
    
    screen.fill(current_sky)
    pygame.draw.circle(screen, celestial_color, celestial_pos, 60)

    # --- B. PARALLAX BACKGROUND RENDERING ---
    for m in mountains:
        if game_active:
            m[0] -= current_speed * 0.15
        if m[0] < -400: m[0] = WIDTH
        pygame.draw.polygon(screen, MTN_DARK, [(m[0], 540), (m[0]+200, 540-m[1]), (m[0]+400, 540)])

    pygame.draw.rect(screen, ROAD_GREY, (0, HEIGHT - 60, WIDTH, 60)) # Road Surface
    pygame.draw.line(screen, WHITE, (0, HEIGHT - 60), (WIDTH, HEIGHT - 60), 5) # Road Shoulder

    for t in trees:
        if game_active:
            t[0] -= current_speed * 0.4
        if t[0] < -120: t[0] = WIDTH
        pygame.draw.rect(screen, TREE_BROWN, (t[0]+20, 485, 12, 55))
        pygame.draw.polygon(screen, TREE_GREEN, [(t[0]-15, 485), (t[0]+26, 395), (t[0]+67, 485)])

    # --- C. INPUT HANDLING (PC & MOBILE READY) ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # JUMP CONTROL (Touch or Space)
        if event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
            if game_active and on_ground:
                y_velocity = jump_power
                on_ground = False
            
            # RESTART LOGIC
            if not game_active:
                player_y, y_velocity, score, energy, current_speed, game_active = HEIGHT-150, 0, 0, 0, 10.5, True
                cars, birds, coins = [], [], []
                car_spawn_timer, bird_spawn_timer, safe_gap_timer = 0, 0, 0

    # --- D. THE CORE ENGINE (LOGIC & PHYSICS) ---
    if game_active:
        # Player Physics Engine
        y_velocity += gravity
        player_y += y_velocity
        if player_y >= HEIGHT - 150:
            player_y = HEIGHT - 150
            on_ground = True
            y_velocity = 0
        
        # SPEED & DISTANCE EVOLUTION
        score += (current_speed / 70) 
        current_speed += 0.0028 # Faster acceleration for more thrill
        animation_timer += (current_speed * 0.022) # Limbs sync with speed
        
        car_spawn_timer += 1
        bird_spawn_timer += 1
        safe_gap_timer += 1

        # --- SMART SPAWNING LOGIC (NO OVERLAP FIX) ---
        # Spawn Car only if bird timer is safe
        if random.randint(1, 70) == 1 and car_spawn_timer > 100 and safe_gap_timer > 50:
            cars.append([WIDTH, HEIGHT - 110, 95, 52, random.choice([(0, 100, 200), (180, 0, 0), (40, 40, 40)])])
            car_spawn_timer = 0
            safe_gap_timer = 0 # Reset gap to prevent bird spawning immediately

        # Spawn Bird only if car timer is safe
        if random.randint(1, 140) == 1 and bird_spawn_timer > 180 and safe_gap_timer > 60:
            birds.append([WIDTH, random.randint(240, 380), 48, 25])
            bird_spawn_timer = 0
            safe_gap_timer = 0 # Reset gap to prevent car spawning immediately

        # Spawn Coins
        if random.randint(1, 100) == 1:
            coins.append([WIDTH, random.randint(250, 450), 30, 30])

        # Hitbox Processing
        p_hitbox = pygame.Rect(player_x + 12, player_y + 12, 26, 68)

        # Move & Check Cars
        for c in cars[:]:
            c[0] -= current_speed
            if p_hitbox.colliderect(pygame.Rect(c[0], c[1], c[2], c[3])):
                game_active = False
            if c[0] < -160: cars.remove(c)

        # Move & Check Birds
        for b in birds[:]:
            b[0] -= (current_speed + 3.5) # Birds fly slightly faster than cars
            if p_hitbox.colliderect(pygame.Rect(b[0], b[1], b[2], b[3])):
                game_active = False
            if b[0] < -120: birds.remove(b)

        # Move & Check Coins
        for co in coins[:]:
            co[0] -= current_speed
            if p_hitbox.colliderect(pygame.Rect(co[0], co[1], co[2], co[3])):
                energy += 1
                coins.remove(co)
            elif co[0] < -60: coins.remove(co)

    # --- E. RENDERING THE HUMAN (DETAILED ANIMATION) ---
    px, py = player_x + 25, player_y
    leg_swing = math.sin(animation_timer * 6) * 32
    arm_swing = math.cos(animation_timer * 6) * 26

    # Head & Body
    pygame.draw.circle(screen, BLACK, (px, py + 15), 15, 2) 
    pygame.draw.circle(screen, CYAN, (px, py + 15), 12) 
    pygame.draw.line(screen, CYAN, (px, py + 27), (px, py + 65), 9) 

    if on_ground:
        pygame.draw.line(screen, BLACK, (px, py + 35), (px + arm_swing, py + 55), 4) # Arms
        pygame.draw.line(screen, CYAN, (px, py + 65), (px + leg_swing, py + 95), 8) # Leg Front
        pygame.draw.line(screen, CYAN, (px, py + 65), (px - leg_swing, py + 95), 8) # Leg Back
    else:
        # Dynamic Jump Pose
        pygame.draw.line(screen, BLACK, (px, py + 35), (px + 24, py + 12), 4)
        pygame.draw.line(screen, CYAN, (px, py + 65), (px + 14, py + 88), 8)

    # --- F. RENDERING OBSTACLES & ITEMS ---
    for c in cars:
        pygame.draw.rect(screen, c[4], (c[0], c[1], c[2], c[3]), border_radius=12)
        pygame.draw.circle(screen, BLACK, (c[0] + 24, c[1] + 52), 15) # Wheel 1
        pygame.draw.circle(screen, BLACK, (c[0] + 71, c[1] + 52), 15) # Wheel 2
    
    for b in birds:
        pygame.draw.ellipse(screen, (70, 70, 70), (b[0], b[1], 48, 20)) # Body
        wing_y_anim = math.sin(animation_timer * 9) * 16
        pygame.draw.line(screen, BLACK, (b[0]+24, b[1]+10), (b[0]+6, b[1]-wing_y_anim), 3) # Wing L
        pygame.draw.line(screen, BLACK, (b[0]+24, b[1]+10), (b[0]+42, b[1]-wing_y_anim), 3) # Wing R

    for co in coins:
        pygame.draw.circle(screen, GOLD, (co[0]+15, co[1]+15), 16)
        pygame.draw.circle(screen, WHITE, (co[0]+10, co[1]+10), 7) # Shine

    # --- G. UI OVERLAY & CREDITS (ALL FEATURES) ---
    screen.blit(font_ui.render(f"DISTANCE: {int(score)} m", True, BLACK), (50, 40))
    screen.blit(font_ui.render(f"COINS: {energy}", True, (135, 85, 0)), (50, 85))
    screen.blit(font_ui.render(f"SPEED: {int(current_speed * 4.2)} km/h", True, (0, 110, 0)), (50, 130))
    
    # PERMANENT CREDIT
    screen.blit(font_dev.render("Developed by Jiban Krushna Manna", True, BLACK), (WIDTH - 365, HEIGHT - 35))

    if not game_active:
        # Crash Screen Rendering
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 40)) # Light red death tint
        screen.blit(overlay, (0,0))
        screen.blit(font_big.render("SYSTEM CRASHED", True, RED), (WIDTH//2 - 310, HEIGHT//2 - 70))
        screen.blit(font_ui.render("TAP SCREEN OR PRESS SPACE TO REBOOT", True, BLACK), (WIDTH//2 - 240, HEIGHT//2 + 50))

    # --- 6. DISPLAY UPDATE ---
    pygame.display.flip()
    pygame.time.Clock().tick(60)