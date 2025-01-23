import pygame

# pygame.mixer.music.set_endevent(pygame.USEREVENT + 1)
#
# from radio_tab import handle_music_end

def handle_keys(event):

    output = None

    if event.key == pygame.K_LEFT:
        output = 'left'
    elif event.key == pygame.K_RIGHT:
        output = 'right'
    elif event.key == pygame.K_UP:
        output = 'up'
    elif event.key == pygame.K_DOWN:
        output = 'down'
    elif event.key == pygame.K_w:
        output = 'w'
    elif event.key == pygame.K_s:
        output = 's'
    elif event.key == pygame.K_a:
        output = 'a'
    elif event.key == pygame.K_d:
        output = 'd'
    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
        output = 'zoomin'
    elif event.key == pygame.K_MINUS:
        output = 'zoomout'
    elif event.key == pygame.K_j:
        output = 'sub_tab_left'  # Add navigation for sub-tab down
    elif event.key == pygame.K_k:
        output = 'sub_tab_right'  # Add navigation for sub-tab up
    return output

def handle_events():
    """
    Handle keyboard input events.
    Returns:
        str: A string indicating the direction ('left', 'right', 'up', 'down'), or None if no direction keys were pressed.
    """
    output = None

    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            output = handle_keys(event)
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        # if event.type == pygame.USEREVENT + 1:
        #     handle_music_end()

    return output
