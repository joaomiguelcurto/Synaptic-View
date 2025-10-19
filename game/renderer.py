import pygame
from typing import Optional, Dict, Any

# Import necessary package components
from core import config
from core.state import GameState, game_state 
from game.grid import Grid # NEW IMPORT

class PygameRenderer:
    """
    Handles the initialization, drawing, and updating of the Pygame window.
    """
    def __init__(self, monitor: Any = None, game_state_instance: Optional[GameState] = None):
        self.monitor = monitor
        self.state = game_state_instance or game_state
        self.selected_entity_id: Optional[int] = None 
        
        pygame.init()

        self.screen = pygame.display.set_mode((config.GAME_SCREEN_WIDTH, config.GAME_SCREEN_HEIGHT))
        pygame.display.set_caption("Synaptic View Simulation")
        
        self.clock = pygame.time.Clock()
        self.is_running = True
        self.frame_count = 0  
        
        # --- NEW: Grid Initialization ---
        self.grid = Grid() 
        
        # Global Metrics Cache (updated to reflect new data)
        self.global_metrics: Dict[str, Any] = {
            "Frame Count": 0,
            "Current FPS": 0.0,
            "Total Entities": 0,
            "System Status": "Running"
        }
        
        if self.monitor:
            self.monitor.select_callback = self.set_selected_entity

    def set_selected_entity(self, entity_id: Optional[int]):
        """Callback function invoked by the Tkinter thread."""
        self.selected_entity_id = entity_id
        print(f"Renderer: Monitoring target switched to: {entity_id}")

    def update_global_metrics(self, key: str, value: Any):
        """Helper method to update a single variable in the global metrics cache."""
        self.global_metrics[key] = value

    def handle_events(self):
        """Handles user input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_running = False

    def update(self):
        """
        Update the state of game objects (movement, logic).
        """
        self.frame_count += 1
        
        # --- 1. Entity Movement Logic ---
        move_speed = 1.5 # Pixels per frame
        
        for entity_id, data in self.state.entities.items():
            
            # Simple Movement: Entity travels in a square pattern across the screen
            if data['x'] < config.GAME_SCREEN_WIDTH - config.CELL_SIZE:
                new_x = data['x'] + move_speed
                new_y = data['y'] 
            else:
                # Reset or change direction (simple wrap-around for demonstration)
                new_x = 0 + move_speed
                new_y = data['y'] 
                
            updates: Dict[str, Any] = {
                'x': new_x, 
                'y': new_y,
                # Also send its current grid index for monitoring
                'grid_col': self.grid.screen_to_grid(new_x, new_y)[0],
                'grid_row': self.grid.screen_to_grid(new_x, new_y)[1],
            }
            
            # Use state manager to save updates
            self.state.update_entity(entity_id, updates)

        
        # --- 2. Prepare Global Monitor Data & Entity List ---
        self.update_global_metrics("Frame Count", self.frame_count)
        self.update_global_metrics("Current FPS", round(self.clock.get_fps(), 1))
        self.update_global_metrics("Total Entities", len(self.state.entities))
        
        if self.monitor and self.frame_count % 60 == 0:
            self.monitor.update_entity_list(self.state.get_entity_ids())
        
        
        # --- 3. Determine and Send Data to Monitor ---
        if self.monitor and self.frame_count % 15 == 0:
            data_to_send = self.global_metrics if self.selected_entity_id is None else self.state.get_entity_data(self.selected_entity_id)
            self.monitor.update_data(data_to_send)


    def draw(self):
        """
        Draw all game elements onto the screen.
        """
        # 1. Draw the Grid/Map
        self.grid.draw(self.screen)
        
        # 2. Draw all entities
        for entity_id, data in self.state.entities.items():
            
            # Center of the entity is at (x, y) coordinates from state
            pos_x = data['x']
            pos_y = data['y']
            
            # Use a slightly smaller radius than the cell size for clarity
            radius = config.CELL_SIZE // 4 
            
            # Determine color
            is_selected = self.selected_entity_id == entity_id
            color = config.YELLOW if not is_selected else config.BLUE
            
            # Draw the entity as a circle
            pygame.draw.circle(self.screen, color, (int(pos_x), int(pos_y)), radius)

        pygame.display.flip()

    def run(self):
        """The main game loop."""
        while self.is_running:
            self.handle_events()
            self.update()
            self.draw()
            
            self.clock.tick(config.FPS)
        
        if self.monitor:
            self.monitor.stop()
        pygame.quit()
