import typing

# Type alias for easier use
EntityData = typing.Dict[str, typing.Any]

class GameState:
    """
    Manages the centralized state of all entities and game-wide variables.
    This class is created as an instance once and used globally.
    """
    # Holds all entity states
    # Key: Entity ID (int), Value: {x, y, status, brain_data, etc.}
    entities: typing.Dict[int, EntityData] = {}
    
    # Counter for assigning unique Entity IDs
    _next_entity_id: int = 1

    def add_entity(self, initial_data: EntityData) -> int:
        """
        Adds a new entity to the state and returns its unique ID.
        """
        entity_id = GameState._next_entity_id
        # Define a standard initial structure for every entity
        entity_data: EntityData = {
            "id": entity_id,
            "x": 0,
            "y": 0,
            "status": "Existing",
            "brain_active": False,
            **initial_data # Merge initial user data (like name)
        }
        self.entities[entity_id] = entity_data
        GameState._next_entity_id += 1
        return entity_id

    def update_entity(self, entity_id: int, updates: EntityData):
        """
        Updates the data for a specific entity ID.
        """
        if entity_id in self.entities:
            self.entities[entity_id].update(updates)

    def get_entity_ids(self) -> typing.List[int]:
        """
        Returns a list of all current entity IDs.
        """
        return list(self.entities.keys())

    def get_entity_data(self, entity_id: int) -> EntityData:
        """
        Returns the full data dictionary for a single entity.
        Returns an empty dict if ID is not found.
        """
        return self.entities.get(entity_id, {})

# Create a single instance of the Game State for global use
game_state = GameState()
