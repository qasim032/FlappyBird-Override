import pygame as pg
import sys
import random

# Initialize pygame modules 
pg.init() 

# Constants
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 499
FPS = 30
BIRD_WIDTH = 50
BIRD_HEIGHT = 35
GROUND_HEIGHT = 112
PIPE_GAP = 150
PIPE_SPEED = 6
PIPE_FREQUENCY = 2200  # milliseconds
GRAVITY = 1
FLAP_POWER = -10
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Creating the game window 
window = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption('Flappy Bird by Qasim')
clock_fps = pg.time.Clock()

# Initialize font for score display
font = pg.font.Font(None, 36)
big_font = pg.font.Font(None, 48)

# Loading images with error handling
try:
    bird = pg.image.load('images/bird.png').convert_alpha()
    bg_image = pg.image.load('images/background.jpg').convert()
    ground_image = pg.image.load('images/base.jpg').convert()
    pipe_image = pg.image.load('images/pipe.png').convert_alpha()
    message = pg.image.load("images/message.jpg").convert()
except pg.error as e:
    print(f"Error loading images: {e}")
    print("Make sure all image files are in the 'images' folder")
    pg.quit()
    sys.exit()

# Scale and prepare images
pipe_flipped = pg.transform.flip(pipe_image, False, True)
bird = pg.transform.scale(bird, (BIRD_WIDTH, BIRD_HEIGHT))

# Game variables
def reset_game():
    global bird_x, bird_y, bird_velocity, pipes, last_pipe_time, score, scored_pipes, game_started, game_over
    bird_x = int(WINDOW_WIDTH / 5)
    bird_y = int(WINDOW_HEIGHT / 2)
    bird_velocity = 0
    pipes = []
    last_pipe_time = pg.time.get_ticks()
    score = 0
    scored_pipes = set()
    game_started = False
    game_over = False

# Initialize game state
ground_y = WINDOW_HEIGHT - GROUND_HEIGHT
reset_game()

# Creating new pipes
def create_pipe():
    pipe_height = random.randint(120, 300)
    x_pos = WINDOW_WIDTH + 10
    top_rect = pipe_flipped.get_rect(midbottom=(x_pos, pipe_height - PIPE_GAP // 2))
    bottom_rect = pipe_image.get_rect(midtop=(x_pos, pipe_height + PIPE_GAP // 2))
    return (top_rect, bottom_rect)

# Collision detection
def check_collision():
    bird_rect = pg.Rect(bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT)
    
    # Check ground collision
    if bird_y >= ground_y - BIRD_HEIGHT:
        return True
    
    # Check ceiling collision
    if bird_y <= 0:
        return True
    
    # Check pipe collisions
    for top_pipe, bottom_pipe in pipes:
        if bird_rect.colliderect(top_pipe) or bird_rect.colliderect(bottom_pipe):
            return True
    
    return False

# Score checking
def update_score():
    global score
    bird_rect = pg.Rect(bird_x, bird_y, BIRD_WIDTH, BIRD_HEIGHT)
    
    for i, (top_pipe, bottom_pipe) in enumerate(pipes):
        if (top_pipe.right < bird_rect.left and 
            i not in scored_pipes):
            score += 1
            scored_pipes.add(i)

# Draw text helper function
def draw_text(text, font, color, x, y, center=False):
    text_surface = font.render(text, True, color)
    if center:
        text_rect = text_surface.get_rect(center=(x, y))
        window.blit(text_surface, text_rect)
    else:
        window.blit(text_surface, (x, y))

# Main game loop
while True:
    current_time = pg.time.get_ticks()
    
    # Event handling
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_SPACE:
                if not game_started and not game_over:
                    # Start the game
                    bird_velocity = FLAP_POWER
                    game_started = True
                elif game_started and not game_over:
                    # Flap during game
                    bird_velocity = FLAP_POWER
                elif game_over:
                    # Restart game
                    reset_game()
                    
    # Game logic (only when game is active)
    if game_started and not game_over:
        # Bird physics
        bird_velocity += GRAVITY
        bird_y += bird_velocity
        
        # Add new pipes
        if current_time - last_pipe_time > PIPE_FREQUENCY:
            pipes.append(create_pipe())
            last_pipe_time = current_time
        
        # Move pipes
        for pipe in pipes:
            pipe[0].centerx -= PIPE_SPEED 
            pipe[1].centerx -= PIPE_SPEED
        
        # Remove off-screen pipes and update scored_pipes set
        pipes_to_remove = []
        for i, pipe in enumerate(pipes):
            if pipe[0].right <= 0:
                pipes_to_remove.append(i)
        
        # Remove pipes and adjust scored_pipes indices
        for i in reversed(pipes_to_remove):
            pipes.pop(i)
            # Remove scored pipe indices that are no longer valid
            scored_pipes = {idx - 1 if idx > i else idx for idx in scored_pipes if idx != i}
            scored_pipes.discard(-1)  # Remove any -1 values
        
        # Update score
        update_score()
        
        # Check for collisions
        if check_collision():
            game_over = True
    
    # Drawing everything
    window.blit(bg_image, (0, 0))
    
    # Draw start message
    if not game_started and not game_over:
        window.blit(message, (0, 0))
        draw_text("Press SPACE to start!", font, WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 100, center=True)
    
    # Draw pipes
    for top_pipe, bottom_pipe in pipes:
        window.blit(pipe_flipped, top_pipe)
        window.blit(pipe_image, bottom_pipe)
    
    # Draw bird
    window.blit(bird, (bird_x, bird_y))
    
    # Draw ground
    window.blit(ground_image, (0, ground_y))
    
    # Draw score during game
    if game_started:
        draw_text(f"Score: {score}", font, WHITE, 10, 10)
    
    # Draw game over screen
    if game_over:
        # Semi-transparent overlay
        overlay = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        window.blit(overlay, (0, 0))
        
        # Game over text
        draw_text("GAME OVER", big_font, WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 - 50, center=True)
        draw_text(f"Final Score: {score}", font, WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2, center=True)
        draw_text("Press SPACE to restart", font, WHITE, WINDOW_WIDTH//2, WINDOW_HEIGHT//2 + 50, center=True)
    
    # Update display
    pg.display.update()
    clock_fps.tick(FPS)        