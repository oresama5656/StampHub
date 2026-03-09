from abc import ABC, abstractmethod

class TaskBase(ABC):
    def __init__(self, name, description, config_manager):
        self.name = name
        self.description = description
        self.config = config_manager
        self.is_enabled = True
        self.status = "Pending"  # Pending, Running, Success, Failed

    @abstractmethod
    def execute(self, input_dir, output_dir):
        """
        Execute the task. 
        Implementations should read from input_dir and write to output_dir.
        Return True if successful, False otherwise.
        """
        pass

    def enable(self):
        self.is_enabled = True

    def disable(self):
        self.is_enabled = False
