# Replicate Image-to-Image Generation Tool

## Purpose
A **model-agnostic** Python wrapper for Replicate's image generation API that processes markdown prompt files in a batch fashion against a single active profile. Following the [AI Model Agnosticism Manifesto](USER-FILES/07.TEMP/ADD%20IMAGE%20REF/ai_model_agnosticism_manifesto.md), this tool supports any model through profiles only - no code changes required.

## Model Agnosticism Principles

This tool implements **true model agnosticism** following these core principles:

1. **Profiles are the Source of Truth**: All model behavior is defined in YAML profiles
2. **No Hardcoded Model Logic**: Zero conditional logic based on model names or parameters
3. **Pure Parameter Pass-through**: All profile parameters are sent to APIs unchanged
4. **API-driven Validation**: Let APIs validate and filter parameters, not the script

### API Parameter Filtering

While our tool passes all parameters from profiles directly to APIs, **the APIs themselves may filter out unsupported parameters**. This means:

- Your profile might include `image_urls` parameter
- Our tool correctly sends it to the API
- The API silently filters it out if the model doesn't support it
- Only supported parameters reach the actual model

**This is expected behavior** - it allows true agnosticism while letting each API/model define its own parameter support.

### Adding New Models

To support any new model, simply create a profile YAML file - **no code changes required**:

```yaml
# USER-FILES/03.PROFILES/new-model.yaml
model_id: "any/model-name"
parameters:
  any_parameter: "any_value"
  future_parameters: ["work", "automatically"]
  model_specific_options: {"complex": "structures"}
```

**The test**: Can you add a new model by only creating a profile? Yes!

## Architecture

### Core Components

1. **Main Entry Point** (`src/main_simple.py`)
   - Command-line argument parsing
   - Orchestrates the entire workflow
   - Handles dry-run and cost estimation modes
   - Progress tracking with Rich library

   A legacy `src/main.py` is kept for compatibility but `src/main_simple.py` is the recommended entry point.

2. **Authentication** (`src/auth/`)
   - **1Password CLI integration** for secure API key management
   - Supports `REPLICATE_API_TOKEN` environment variable
   - Configuration via `auth.yaml`

3. **Configuration** (`src/config/`)
   - YAML-based configuration system
   - Profile management for generation parameters
   - Validation of all configurations
   - No separate model registry — model info lives in profiles

4. **Processing** (`src/processing/`)
   - **Discovery**: Finds markdown files and profiles automatically
   - **BatchProcessor**: Processes all input files against a single active profile
   - Pre-flight markdown validation (validates prompt + image URL structure)
   - Fail-fast philosophy for error handling

5. **API Client** (`src/api/client.py`)
   - **Model-agnostic** wrapper around `replicate` library
   - Pure parameter pass-through (no filtering or validation)
   - Retry logic with exponential backoff
   - Rate limit handling

6. **Output Management** (`src/output/`)
   - Image downloading and validation with Pillow
   - PNG conversion via `--force-png` flag
   - Organized file naming with timestamps
   - Payloads saved as Markdown files (`.md` with JSON in codeblocks)
   - Report generation (success/failure/cost)

7. **Convenience Wrapper** (`run.py`)
   - Zero-step environment setup — creates venv, installs deps, runs `src.main_simple`
   - Usage: `python3 run.py [args]`

## Directory Structure

```
img-to-img/
├── run.py                   # Convenience wrapper
├── src/
│   ├── main_simple.py      # Entry point (recommended)
│   ├── main.py             # Legacy entry point (kept for compatibility)
│   ├── cli.py              # CLI argument parsing
│   ├── orchestrator.py     # Pipeline orchestration
│   ├── api/
│   │   └── client.py       # Replicate API client
│   ├── auth/               # Authentication (1Password)
│   ├── config/             # Configuration loading & validation
│   ├── processing/         # BatchProcessor, discovery, validator
│   ├── output/             # Image writing, reports, context
│   └── utils/              # Logging, progress, path resolution
├── USER-FILES/             # User data (protected)
│   ├── 01.CONFIG/
│   │   └── config.yaml     # Main settings
│   ├── 03.PROFILES/        # Generation profiles (YAML)
│   ├── 04.INPUT/           # Input markdown files
│   ├── 05.OUTPUT/          # Generated images
│   └── 07.TEMP/            # Temporary files
├── logs/                   # Application logs
├── requirements.txt
├── AGENTS.md
└── LICENSE
```

## Usage

### Basic Workflow

1. **Setup Environment**
   ```bash
   # Using the convenience wrapper (recommended)
   python3 run.py --dry-run

   # Or manually:
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt

   # Set API token via 1Password (recommended) or environment
   export REPLICATE_API_TOKEN=r8_your-token-here
   ```

2. **Create a Profile** (`USER-FILES/03.PROFILES/my-profile.yaml`)
   ```yaml
   # Model identifier (required)
   model_id: "black-forest-labs/flux-schnell"

   # Description (optional)
   description: "FLUX Schnell - Fast generation"

   # All parameters passed directly to API (examples only!)
   parameters:
     aspect_ratio: "1:1"
     output_format: "png"
     any_future_param: "automatically_supported"

   # Prompt modifications (optional)
   prompt_prefix: "High quality, "
   prompt_suffix: ", professional photo"
   ```

3. **Add Markdown Prompts** (`USER-FILES/04.INPUT/portrait.md`)
   ```markdown
   A cinematic portrait in soft lighting

   ![reference](https://example.com/portrait.jpg)
   ```

   Each markdown file must contain at least 2 lines: a prompt (line 1) and an image URL (line 2).

4. **Run Generation**
   ```bash
   # Using convenience wrapper
   python3 run.py

   # Cost estimation only
   python3 run.py --cost-estimation

   # Dry run (no API calls)
   python3 run.py --dry-run

   # Debug mode (saves API requests/responses)
   python3 run.py --debug

   # Convert all output images to PNG
   python3 run.py --force-png

   # Disable payload saving
   python3 run.py --no-save-payloads

   # No progress bar
   python3 run.py --no-progress
   ```

## Processing Flow

1. **Load Configuration**: Read `config.yaml`
2. **Authenticate**: Get Replicate API key from 1Password
3. **Pre-flight Validation**: Validate all markdown files have correct prompt + image URL structure
4. **Discover Inputs**: Find all `.md` files in `04.INPUT/`
5. **Discover Profiles**: Load `.yaml` files from `03.PROFILES/`, require exactly one active profile
6. **Batch Processing**: For each markdown file:
   - Extract prompt text and image URLs from markdown
   - Generate image via Replicate API
   - Save image with descriptive filename
   - Save payload as Markdown file (`.md`) alongside image
   - Track costs and failures
7. **Generate Reports**: Create summary reports in output folder

## Output Structure

```
USER-FILES/05.OUTPUT/
└── YYMMDD_HHMMSS_IMG-TO-IMG/         # Timestamped session folder
    ├── my_prompt-YYMMDD_HHMMSS.png    # Generated image
    ├── my_prompt-YYMMDD_HHMMSS.md     # API payload (if saved)
    ├── COST-ESTIMATION.md             # Cost breakdown
    ├── GENERATION-REPORT.md           # Success summary
    └── FAILURE-REPORT.md              # Error details (if any)
```

## Configuration Files

### config.yaml
- **wrapper**: Timeout, retries, wait times
- **queue**: Rate limit handling
- **notifications**: Success/failure alerts

### Profile YAML

**Important**: Parameters are **examples only** - any parameter can be used!

- `model_id`: Replicate model identifier (required)
- `parameters`: Any parameters supported by the model (passed through unchanged)
- `description`: Optional metadata
- `prompt_prefix` / `prompt_suffix`: Text modifications (optional)
- `delay_between_requests`: Rate limiting delay in seconds (optional)
- `pricing.base_cost`: Per-generation cost for estimation (optional)

**The script supports ANY parameter combination** - if a model needs it, add it to the profile.

**Parameter Filtering**: APIs may silently filter out unsupported parameters. Check your payload logs (.md files) if parameters seem to be ignored - this usually means the model doesn't support them.

## Error Handling

- **Fail-fast philosophy**: Stops on first error
- **Retry logic**: Exponential backoff for transient failures
- **Rate limiting**: Automatic delay when rate limited
- **Pre-flight validation**: Catches malformed markdown files before API calls
- **Image validation**: Verifies all downloads with Pillow
- **Detailed logging**: Full error context in logs

## Cost Tracking

- Calculates costs based on profile `pricing.base_cost`
- `--cost-estimation` mode for pre-run estimates
- Generates detailed cost reports
- Tracks per-file and total costs

## Debug Features

- `--debug` flag saves all API requests/responses
- Payloads automatically saved as Markdown (`.md`) alongside images
- Disable payload saving with `--no-save-payloads`
- Progress bars with Rich library
- Detailed failure reports

## Protection Rules

- Never modifies files in `USER-FILES/` without permission
- Input files remain in `04.INPUT/` (not moved after processing)
- Only reads from `04.INPUT/` and writes to `05.OUTPUT/`
- No automatic archiving or cleanup

## Dependencies

- **replicate**: Official Replicate Python client
- **loguru**: Advanced logging
- **rich**: Terminal formatting and progress bars
- **Pillow**: Image validation and PNG conversion
- **PyYAML**: Configuration parsing
- **requests**: HTTP client for image downloads
- **natsort**: Natural sorting of files

## Key Features

1. **True Model Agnosticism**: Support any Replicate model through profiles only
2. **Batch Processing**: All input files processed sequentially against a single profile
3. **Zero Code Changes**: Add new models via YAML profiles, never touch code
4. **Pure Parameter Pass-through**: All profile parameters sent to API unchanged
5. **PNG Conversion**: Automatically convert any output format to PNG via `--force-png`
6. **Pre-flight Validation**: Validates markdown file structure before any API calls
7. **Cost Management**: Pre-run estimation and tracking
8. **Robust Error Handling**: API-driven validation, detailed reporting
9. **Sequential Processing**: Avoids rate limits
10. **Payload Logging**: Save API payloads as Markdown for inspection
11. **Multiple Modes**: Dry-run, cost estimation, debug

## Tips

- Start with `--cost-estimation` to preview costs
- Use `--dry-run` to test configuration
- Enable `--debug` when troubleshooting API issues
- Use `--force-png` if you need consistent PNG output
- Disable payload saving with `--no-save-payloads` to reduce clutter
- Use profiles to test different model parameters
- Check logs in `logs/` folder for detailed information
- **Parameter Filtering**: If parameters seem ignored, check payload logs for filtering warnings
- **Model Compatibility**: Verify model documentation for supported parameters

## Authentication

**Primary method**: 1Password CLI integration
1. Configure `auth.yaml` with vault/item details
2. Script automatically retrieves `REPLICATE_API_TOKEN`

**Fallback method**: Environment variable
- Set `REPLICATE_API_TOKEN` directly
- No `.env` file support (deprecated for security)
