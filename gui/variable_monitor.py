import tkinter as tk
import threading
import time
from core import config
from typing import Dict, Any, List, Optional, Callable

class VariableMonitor:
    """
    A threaded Tkinter monitor that displays global metrics and 
    the details of every single selected entity from a scrollable dropdown list.
    """
    def __init__(self, initial_data: Optional[Dict[str, Any]] = None):
        self.root: Optional[tk.Tk] = None
        self.monitor_thread: Optional[threading.Thread] = None
        self.monitored_data: Dict[str, Any] = initial_data or {}
        self.variable_labels: Dict[str, tk.Label] = {}
        self.is_running: bool = False
        
        # --- Tkinter State Variables ---
        self.entity_var: Optional[tk.StringVar] = None 
        self.entity_menu: Optional[tk.OptionMenu] = None
        self.entity_ids: List[str] = ["Game Metrics"] # Default options in dropdown
        self.select_callback: Optional[Callable[[Optional[int]], None]] = None # To communicate selection back

        # Frame and Canvas instances for the scrollable list
        self.canvas: Optional[tk.Canvas] = None
        self.content_frame: Optional[tk.Frame] = None

    def _setup_gui(self):
        """Sets up the Tkinter GUI elements (should be called by the thread)."""
        self.root = tk.Tk()
        self.root.title(config.MONITOR_CAPTION)
        self.is_running = True
        self.root.geometry("400x500")
        
        # Initialize Tkinter variables now that the root exists
        self.entity_var = tk.StringVar(self.root)
        self.entity_var.set("Game Metrics") # Initial default selection
        # Trace runs a callback whenever the variable is written to (example, when selection changes)
        self.entity_var.trace_add("write", self._on_entity_select)

        # --- Dropdown Menu Frame ---
        control_frame = tk.Frame(self.root, padx=5, pady=5)
        control_frame.pack(fill=tk.X)
        
        tk.Label(control_frame, text="Monitor Target:").pack(side=tk.LEFT, padx=5)
        
        # Initial Dropdown menu (will be dynamically updated)
        self.entity_menu = tk.OptionMenu(control_frame, self.entity_var, *self.entity_ids)
        self.entity_menu.config(width=20)
        self.entity_menu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # --- Scrollable Container Setup ---
        main_frame = tk.Frame(self.root, padx=5, pady=5)
        main_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL)
        
        self.canvas = tk.Canvas(main_frame, yscrollcommand=scrollbar.set, bg='#212121')
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Inner Frame where all labels will be placed
        self.content_frame = tk.Frame(self.canvas, bg='#212121')
        self.canvas.create_window((0, 0), window=self.content_frame, anchor="nw")

        self.content_frame.bind("<Configure>", self._on_frame_configure)
        
        self._populate_variables(self.monitored_data)

        # --- END CONTAINER SETUP ---

        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        print("Tkinter Monitor is running...")
        self.root.mainloop()
        self.is_running = False

    def _on_frame_configure(self, event: Optional[tk.Event] = None):
        """Update the scrollregion on the canvas when the inner frame content changes."""
        if self.canvas:
            self.canvas.update_idletasks() # Ensure frame size is calculated
            self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def _on_entity_select(self, *args):
        """
        Callback when the dropdown value changes. Informs the Pygame loop.
        """
        selected = self.entity_var.get() if self.entity_var else "Game Metrics"
        
        target_id: Optional[int] = None
        
        if selected.isdigit():
            target_id = int(selected)
        elif selected == "Game Metrics":
            target_id = None 
        
        # Communicate the selection back to the main Pygame thread via callback
        if self.select_callback:
            # We schedule this call to run on the main thread if possible, 
            # though the callback should be thread-safe regardless.
            self.select_callback(target_id)
    
    def _populate_variables(self, data: Dict[str, Any]):
        """Creates labels for new variables or updates text for existing ones."""
        # Clear all existing widgets before repopulating
        if self.content_frame:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
            self.variable_labels = {} # Reset labels dictionary
            
            for i, (key, value) in enumerate(data.items()):
                key_str = str(key)
                
                # Key Label (Variable Name)
                key_label = tk.Label(self.content_frame, text=f"{key_str}:", anchor='w', 
                                     font=('Inter', 10), fg='#A9A9A9', bg='#212121', padx=5, pady=2)
                key_label.grid(row=i, column=0, sticky='w')

                # Value Label (The changing data)
                value_label = tk.Label(self.content_frame, text=str(value), anchor='w', 
                                       font=('Inter', 10, 'bold'), fg='#4CAF50', bg='#212121', padx=5, pady=2)
                value_label.grid(row=i, column=1, sticky='w')
                
                # Store the value label for future updates (though we clear and rebuild now)
                self.variable_labels[key_str] = value_label
        
        self._on_frame_configure() # Recalculate scroll region

    def start_monitor_thread(self):
        """Starts the Tkinter GUI in a separate thread."""
        self.monitor_thread = threading.Thread(target=self._setup_gui, daemon=True)
        self.monitor_thread.start()
        
        # Wait some time for the monitor to start and initialize self.root
        while not self.root and self.monitor_thread and self.monitor_thread.is_alive():
            time.sleep(0.01)

    def update_entity_list(self, new_entity_ids: List[int]):
        """
        Safely updates the list of available entity IDs for the dropdown.
        Called from the Pygame thread.
        """
        if self.is_running and self.root:
            # Schedule the update to run on the Tkinter thread
            self.root.after(0, lambda: self._apply_entity_list_update(new_entity_ids))
    
    def _apply_entity_list_update(self, new_entity_ids: List[int]):
        """
        Internal function to rebuild the dropdown options on the Tkinter thread.
        """
        if not self.entity_menu: return

        new_ids_str = ["Game Metrics"] + [str(i) for i in sorted(new_entity_ids)]
        
        # Only update if the list has actually changed
        if new_ids_str == self.entity_ids:
            return

        self.entity_ids = new_ids_str
        
        # Rebuild the Option Menu
        menu = self.entity_menu["menu"]
        menu.delete(0, "end")
        
        current_selection = self.entity_var.get() if self.entity_var else "Game Metrics"

        for entity_id in self.entity_ids:
            # Use tk._setit to ensure the command correctly sets the variable
            menu.add_command(label=entity_id, 
                             command=tk._setit(self.entity_var, entity_id))
        
        # Restore or set default selection
        if self.entity_var and current_selection not in self.entity_ids:
            self.entity_var.set(self.entity_ids[0])
            
    def update_data(self, new_data: Dict[str, Any]):
        """
        Safely updates the monitored data dictionary from the Pygame thread.
        """
        if self.is_running and self.root:
            # Schedule the display update to run on the Tkinter thread
            self.root.after(0, lambda: self._populate_variables(new_data))
        
    def stop(self):
        """Stops the Tkinter loop safely."""
        if self.root:
            self.root.quit()
