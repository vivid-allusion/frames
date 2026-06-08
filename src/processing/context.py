"""Processing context dataclasses for encapsulating parameters."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
# Progress handling moved to utils.progress


@dataclass
class ProcessingContext:
    """Encapsulates all parameters needed for processing a file-model combination."""

    prompt_file: Path
    relative_path: Path
    prompts: List[str]
    model_id: str
    params: Dict[str, Any]  # All profile parameters passed through unchanged
    pricing: Dict[str, Any]
    profile_name: str
    output_dir: Path
    prompt_prefix: str = ""
    prompt_suffix: str = ""
    delay_between_requests: float = 0


@dataclass
class CombinationProcessingContext:
    """Context for processing a single combination of file and model."""

    model_info: Dict[str, Any]
    prompt_file_tuple: Tuple[Path, Path]
    output_dir: Path
    combination_num: int
    total_combinations: int
    progress: Optional[Any] = None
    task_id: Optional[int] = None


@dataclass
class BatchProcessingContext:
    """Context for processing a batch of models."""

    prompt_files: List[Tuple[Path, Path]]
    models: List[Dict[str, Any]]
    output_dir: Path
    progress: Optional[Any] = None
    task_id: Optional[int] = None
    start_combination: int = 1


@dataclass
class ProcessorConfig:
    """Configuration for BatchProcessor initialization."""

    api_client: Any  # ReplicateClient
    output_writer: Any  # OutputWriter
    reporter: Any  # Reporter
    save_payloads: bool = True
    dry_run: bool = False
    no_progress: bool = False
