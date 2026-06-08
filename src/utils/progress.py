"""Progress visualization with alive-progress."""

from alive_progress import alive_bar


class AliveProgressWrapper:
    """Wrapper to make alive-progress compatible with existing Progress interface."""

    def __init__(self):
        self.bar = None
        self.total = 0
        self.current = 0

    def add_task(self, description: str, total: int) -> int:
        """Add a task and return task ID."""
        self.total = total
        self.description = description
        print(f"\n🚀 Starting: {description} ({total} items)")
        self.bar = alive_bar(
            total, title=description, bar="filling", spinner="dots_waves"
        )
        self.progress_context = self.bar.__enter__()
        return 0  # Single task ID

    def update(self, task_id: int, advance: int = 1, description: str = ""):
        """Update progress."""
        if self.progress_context:
            self.current += advance
            self.progress_context()
            if description:
                print(f"✅ Progress: {self.current}/{self.total} - {description}")
            else:
                print(f"✅ Progress: {self.current}/{self.total} completed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.bar:
            self.bar.__exit__(exc_type, exc_val, exc_tb)
            print(f"\n🎉 Completed: {self.description}")


def create_progress_bar() -> AliveProgressWrapper:
    """
    Create an alive-progress bar for batch processing.

    Returns:
        Configured AliveProgressWrapper instance
    """
    return AliveProgressWrapper()
