import pygame
import os
import time
import numpy as np
from settings import *
from Map import *
from Player import *
from Raycaster import *

class GameRecorder:
    def __init__(self, save_directory="training_data"):
        # Create directories for saving data if they don't exist
        self.save_directory = save_directory
        self.images_dir = os.path.join(save_directory, "images")
        self.actions_dir = os.path.join(save_directory, "actions")
        
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.actions_dir, exist_ok=True)
        
        self.frame_count = 0
        self.session_id = int(time.time())  # Use timestamp as session ID
        self.action_log = []
        
    def capture_frame(self, screen):
        # Convert Pygame surface to numpy array
        screenshot = pygame.surfarray.array3d(screen)
        screenshot = np.transpose(screenshot, (1, 0, 2))  # Rearrange to standard image format
        
        # Save screenshot as numpy array
        filename = f"{self.session_id}_{self.frame_count:06d}"
        np.save(os.path.join(self.images_dir, filename), screenshot)
        
        return filename
    
    def record_action(self, action_dict, filename):
        # Record action along with the corresponding frame filename
        self.action_log.append({
            'frame': filename,
            'actions': action_dict
        })
        
        # Every 100 frames, save the action log to disk to prevent data loss
        if len(self.action_log) >= 100:
            self.save_actions()
            self.action_log = []
    
    def save_actions(self):
        if not self.action_log:
            return
            
        # Save action log as numpy array
        actions_filename = f"{self.session_id}_{self.frame_count//100:04d}_actions"
        np.save(os.path.join(self.actions_dir, actions_filename), np.array(self.action_log, dtype=object))
    
    def increment_frame(self):
        self.frame_count += 1
        
    def cleanup(self):
        # Save any remaining actions before quitting
        self.save_actions()

# Initialize pygame and game components
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

map = Map()
player = Player()
raycaster = Raycaster(player, map)

background_image = pygame.image.load("background.png")

# Initialize recorder
recorder = GameRecorder()

# Set recording parameters
recording_frequency = 4  # Capture every 4th frame for efficiency
recording_enabled = True

clock = pygame.time.Clock()
running = True

while running:
    clock.tick(60)
    
    # Track current actions
    current_actions = {
        'forward': False,
        'backward': False,
        'left': False,
        'right': False,
        'turn_left': False,
        'turn_right': False,
        # Add any other actions your game uses
    }
    
    # Process events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Toggle recording with R key
                recording_enabled = not recording_enabled
                print(f"Recording {'enabled' if recording_enabled else 'disabled'}")
    
    # Get keyboard state for action recording
    keys = pygame.key.get_pressed()
    current_actions['forward'] = keys[pygame.K_w] or keys[pygame.K_UP]
    current_actions['backward'] = keys[pygame.K_s] or keys[pygame.K_DOWN]
    current_actions['left'] = keys[pygame.K_a]
    current_actions['right'] = keys[pygame.K_d]
    current_actions['turn_left'] = keys[pygame.K_LEFT]
    current_actions['turn_right'] = keys[pygame.K_RIGHT]
    
    # Update game state
    player.update()
    raycaster.castAllRays()
    
    # Render game
    screen.blit(background_image, (0, 0, 10, 10))
    raycaster.render(screen)
    
    # Record data at specified frequency
    if recording_enabled and recorder.frame_count % recording_frequency == 0:
        frame_filename = recorder.capture_frame(screen)
        recorder.record_action(current_actions, frame_filename)
    
    # Display recording status
    if recording_enabled:
        font = pygame.font.SysFont(None, 24)
        status_text = font.render(f"Recording: Frame {recorder.frame_count}", True, (255, 0, 0))
        screen.blit(status_text, (10, 10))
    
    pygame.display.update()
    recorder.increment_frame()

# Clean up
recorder.cleanup()
pygame.quit()