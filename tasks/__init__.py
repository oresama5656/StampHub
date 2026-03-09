from .split_task import SplitTask
from .remove_bg_task import RemoveBgTask
from .trim_task import TrimTask
from .format_task import FormatTask

# Map task IDs from the GUI to their respective classes
TASK_REGISTRY = {
    "split": SplitTask,
    "remove_bg": RemoveBgTask,
    "trim": TrimTask,
    "format": FormatTask
}
