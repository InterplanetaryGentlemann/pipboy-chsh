import pygame

def handle_keyboard():
    """
    Handle keyboard input events.
    Returns:
        str: A string indicating the direction ('left', 'right', 'up', 'down'), or None if no direction keys were pressed.
    """
    direction = None

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                direction = 'left'
            elif event.key == pygame.K_RIGHT:
                direction = 'right'
            elif event.key == pygame.K_UP:
                direction = 'up'
            elif event.key == pygame.K_DOWN:
                direction = 'down'
            elif event.key == pygame.K_w:
                direction = 'w'
            elif event.key == pygame.K_s:
                direction = 's'
            elif event.key == pygame.K_a:
                direction = 'a'
            elif event.key == pygame.K_d:
                direction = 'd'
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                direction = 'zoomin'
            elif event.key == pygame.K_MINUS:
                direction = 'zoomout'


    return direction
