"""Progress visualization with rich."""
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TimeRemainingColumn,
    MofNCompleteColumn
)
from rich.console import Console


def create_progress_bar() -> Progress:
    """
    Create a rich progress bar for matrix processing.
    
    Returns:
        Configured Progress instance
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeRemainingColumn(),
        console=Console(stderr=True),
        transient=False
    )