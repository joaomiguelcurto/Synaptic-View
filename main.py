import time

from game.renderer import PygameRenderer
from gui.variable_monitor import VariableMonitor
from core.state import game_state
from core.config import CELL_SIZE

def main():
    """
    The main function to initialize and run the game with a Tkinter monitor 
    running on a separate thread.
    """
    print("Starting Synaptic View...")
    
    # --- PRE-POPULATE GAME STATE WITH ENTITIES ---
    
    # Helper to find the center of a grid cell (e.g., cell at col 3, row 5)
    def get_center_coords(col, row):
        return (col * CELL_SIZE + CELL_SIZE / 2, row * CELL_SIZE + CELL_SIZE / 2)

    # Entity 1:
    x1, y1 = get_center_coords(3, 5)
    e1_id = game_state.add_entity({"x": x1, "y": y1, "name": "First Agent", "manual_spawn": True, "status": "Spawned"})
    
    # Entity 2:
    x2, y2 = get_center_coords(10, 8)
    e2_id = game_state.add_entity({"x": x2, "y": y2, "name": "Second Agent", "manual_spawn": True, "status": "Spawned"})
    
    print(f"Entities added: {e1_id}, {e2_id}")

    # Initialize and START the Tkinter Monitor in its own thread
    monitor = VariableMonitor()
    monitor.start_monitor_thread()
    
    time.sleep(1) # Give monitor time to fully start (Python doesnt like to do stuff too fast lmao)
    
    if not monitor.is_running:
        print("Error: Tkinter monitor failed to start. Exiting.")
        return

    # Initialize the Pygame Renderer, passing the monitor and state instances
    renderer = PygameRenderer(monitor=monitor, game_state_instance=game_state)
    
    # Run the Pygame Main Loop (this is the main thread)
    print("Pygame Renderer is running...")
    renderer.run()
    
    print("Game session and monitor ended.")

if __name__ == "__main__":
    main()
