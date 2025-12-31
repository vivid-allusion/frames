"""Output context dataclasses for encapsulating parameters."""
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Union


@dataclass
class ImageSaveContext:
    """Encapsulates all parameters needed for saving an image."""
    image_url: str
    timestamp: str
    prompt_file_name: str
    model_name: str
    output_dir: Path
    relative_path: Optional[Path] = None
    payload: Optional[Dict[str, Any]] = None
