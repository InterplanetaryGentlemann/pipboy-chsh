import random
import pygame
import math
import sys

# Initialize pygame
pygame.init()

# Set up the screen
screen_width, screen_height = 800, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Fallout 4 Pip-Boy Radio Waveform")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Parameters for the sine wave
f0 = 5         # Initial frequency (Hz)
alpha = 0.5    # Frequency change rate (Hz per second)
amplitude = 100  # Amplitude of the sine wave
speed = 2      # Horizontal speed of the waveform movement
sampling_rate = 1000  # Number of points per second

# Time-related variables
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

def generate_wave(time):
    """Generate the y-values of the sine wave at a given time."""
      # Initial frequency (Hz)
    t = (time - start_time) / 1000  # Convert time to seconds
    frequency = f0 + alpha * t  # Linearly changing frequency
    return amplitude * math.sin(2 * math.pi * frequency * t)

def draw_wave():
    global f0, amplitude
    """Draw the sine wave on the screen."""
    time = pygame.time.get_ticks()
    f0 = random.randint(1, 10)
    # Clear the screen
    screen.fill(BLACK)

    # Draw the sine wave
    for x in range(screen_width):
        # Generate y value for the sine wave at this x (time)
        y = generate_wave(time + x * speed)
        
        # Map the y value to the screen's height
        screen_y = int(screen_height / 2 + y)
        
        # Draw the waveform (a simple line from the previous point to the current one)
        if x > 0:
            pygame.draw.line(screen, WHITE, (x - 1, last_y), (x, screen_y), 1)
        
        last_y = screen_y
    
    pygame.display.flip()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the wave each frame
    draw_wave()

    # Limit frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()
import random
import pygame
import math
import sys

# Initialize pygame
pygame.init()

# Set up the screen
screen_width, screen_height = 800, 400
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Fallout 4 Pip-Boy Radio Waveform")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Parameters for the sine wave
f0 = 5         # Initial frequency (Hz)
alpha = 0.5    # Frequency change rate (Hz per second)
amplitude = 100  # Amplitude of the sine wave
speed = 2      # Horizontal speed of the waveform movement
sampling_rate = 1000  # Number of points per second

# Time-related variables
clock = pygame.time.Clock()
start_time = pygame.time.get_ticks()

def generate_wave(time):
    """Generate the y-values of the sine wave at a given time."""
      # Initial frequency (Hz)
    t = (time - start_time) / 1000  # Convert time to seconds
    frequency = f0 + alpha * t  # Linearly changing frequency
    return amplitude * math.sin(2 * math.pi * frequency * t)

def draw_wave():
    global f0, amplitude
    """Draw the sine wave on the screen."""
    time = pygame.time.get_ticks()
    f0 = random.randint(1, 10)
    # Clear the screen
    screen.fill(BLACK)

    # Draw the sine wave
    for x in range(screen_width):
        # Generate y value for the sine wave at this x (time)
        y = generate_wave(time + x * speed)
        
        # Map the y value to the screen's height
        screen_y = int(screen_height / 2 + y)
        
        # Draw the waveform (a simple line from the previous point to the current one)
        if x > 0:
            pygame.draw.line(screen, WHITE, (x - 1, last_y), (x, screen_y), 1)
        
        last_y = screen_y
    
    pygame.display.flip()

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw the wave each frame
    draw_wave()

    # Limit frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
sys.exit()




----------------------------------------------------------------------------------------------------



import pygame
import math
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 400

# Colors
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pip-Boy Radio Waveform")

# Frame rate
FPS = 60
clock = pygame.time.Clock()

# Signal parameters
amplitude = HEIGHT // 4  # Maximum amplitude of the waveform
offset = HEIGHT // 2     # Vertical center of the waveform
speed = 2                # Speed at which the wave moves left

# Time step for frequency variation
dt = 0.1

def frequency_variation(t):
    """Define the frequency variation function f(t)."""
    return 2 + math.sin(t * 0.1) * 1.5  # Example: oscillates between 0.5 and 3.5 Hz

def signal_value(t, frequency_func):
    """Compute s(t) = sin(2π∫f(t) dt)."""
    integral = sum(frequency_func(i * dt) * dt for i in range(int(t / dt)))
    return math.sin(2 * math.pi * integral)

# Time variable for frequency modulation
time_elapsed = 0

# Waveform storage for smooth animation
waveform = [0] * WIDTH

running = True
while running:
    screen.fill(BLACK)

    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update waveform
    time_elapsed += dt
    new_value = signal_value(time_elapsed, frequency_variation)
    waveform.pop(0)  # Remove the oldest value
    waveform.append(new_value)  # Add the new value

    # Draw the waveform
    for x in range(WIDTH - 1):
        y1 = offset - int(waveform[x] * amplitude)
        y2 = offset - int(waveform[x + 1] * amplitude)
        pygame.draw.line(screen, GREEN, (x, y1), (x + 1, y2), 2)

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(FPS)

# Quit Pygame
pygame.quit()