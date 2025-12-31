# Replicate Text-to-Image Generation Tool

## 🎯 Purpose
A **model-agnostic** Python wrapper for Replicate's text-to-image API that processes multiple prompts through any AI model in a matrix fashion. Following the [AI Model Agnosticism Manifesto](USER-FILES/07.TEMP/ADD%20IMAGE%20REF/ai_model_agnosticism_manifesto.md), this tool supports any model through profiles only - no code changes required.

## ✨ Model Agnosticism Principles

This tool implements **true model agnosticism** following these core principles:

1. **Profiles are the Source of Truth**: All model behavior is defined in YAML profiles
2. **No Hardcoded Model Logic**: Zero conditional logic based on model names or parameters
3. **Pure Parameter Pass-through**: All profile parameters are sent to APIs unchanged
4. **API-driven Validation**: Let APIs validate AND filter parameters, not the script

### ⚠️ **Important: API Parameter Filtering**

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
endpoint: "any/model-name"
parameters:
  any_parameter: "any_value"
  future_parameters: ["work", "automatically"]
  model_specific_options: {"complex": "structures"}
```

**The test**: Can you add a new model by only creating a profile? ✅ Yes!

## 🏡 Architecture

### Core Components

1. **Main Entry Point** (`src/main.py`)
   - Command-line argument parsing
   - Orchestrates the entire workflow
   - Handles dry-run and cost estimation modes
   - Progress tracking with Rich library

2. **Authentication** (`src/auth/`)
   - **1Password CLI integration** for secure API key management
   - Supports `REPLICATE_API_TOKEN` environment variable
   - Configuration via `auth.yaml`

3. **Configuration** (`src/config/`)
   - YAML-based configuration system
   - Model registry with endpoints and pricing
   - Profile management for different generation parameters
   - Validation of all configurations

4. **Processing** (`src/processing/`)
   - **Discovery**: Finds prompt files and profiles automatically
   - **Matrix Processor**: Processes all combinations of prompts × models
   - Sequential processing to avoid rate limits
   - Fail-fast philosophy for error handling

5. **API Client** (`src/api/client.py`)
   - **Model-agnostic** wrapper around `replicate` library
   - Pure parameter pass-through (no filtering or validation)
   - Retry logic with exponential backoff
   - Rate limit handling

6. **Output Management** (`src/output/`)
   - Image downloading and validation with Pillow
   - Organized file naming with timestamps
   - Report generation (success/failure/cost)
   - Subfolder structure: `promptfile_X_profile`

## 📁 Directory Structure

```
00.fal-text->image-tool/
├── src/                    # Source code
│   ├── main.py            # Entry point
│   ├── api/               # FAL API client
│   ├── auth/              # Authentication
│   ├── config/            # Configuration loading
│   ├── processing/        # Core processing logic
│   ├── output/            # Output writing
│   └── utils/             # Utilities (logging, progress)
├── USER-FILES/            # User data (protected)
│   ├── 00.KB/            # Knowledge base
│   ├── 01.CONFIG/        # Configuration files
│   │   ├── config.yaml   # Main settings
│   │   └── models.yaml   # Model registry
│   ├── 02.STANDBY/       # Unused files
│   ├── 03.PROFILES/      # Generation profiles
│   ├── 04.INPUT/         # Input prompt files
│   ├── 05.OUTPUT/        # Generated images
│   ├── 06.DONE/          # Archived (not used)
│   └── 07.TEMP/          # Temporary files
└── logs/                  # Application logs
```

## 🚀 Usage

### Basic Workflow

1. **Setup Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # or venv\\Scripts\\activate on Windows
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Install 1Password CLI (recommended)
   brew install --cask 1password-cli  # macOS
   
   # OR set environment variable directly
   export REPLICATE_API_TOKEN=r8_your-token-here
   ```

2. **Configure Models** (`USER-FILES/01.CONFIG/models.yaml`)
   ```yaml
   models:
     flux-schnell:
       endpoint: "fal-ai/flux/schnell"
       description: "FLUX Schnell - Fast generation"
       pricing:
         base_cost: 0.003
   ```

3. **Create Profiles** (`USER-FILES/03.PROFILES/profile.yaml`)
   ```yaml
   # Model endpoint (required)
   endpoint: "google/nano-banana"
   
   # Description (optional)
   description: "Gemini 2.5 Flash Image Generation"
   
   # All parameters passed directly to API (examples only!)
   parameters:
     aspect_ratio: "match_input_image"
     image_urls: ["https://example.com/reference.png"]
     output_format: "png"
     any_future_param: "automatically_supported"
   
   # Prompt modifications (optional)
   prompt_prefix: "High quality, "
   prompt_suffix: ", professional photo"
   ```

4. **Add Prompts** (`USER-FILES/04.INPUT/prompts.txt`)
   ```
   A serene mountain landscape at sunset
   A futuristic cityscape with flying cars
   ```

5. **Run Generation**
   ```bash
   # Normal run
   python -m src.main
   
   # Cost estimation only
   python -m src.main --cost-estimation
   
   # Dry run (no API calls)
   python -m src.main --dry-run
   
   # Debug mode (saves API calls)
   python -m src.main --debug
   
   # Verbose logging
   python -m src.main --verbose
   
   # No progress bar
   python -m src.main --no-progress
   ```

## 🔄 Processing Flow

1. **Load Configuration**: Read `config.yaml` and `models.yaml`
2. **Authenticate**: Get FAL API key from environment
3. **Discover Inputs**: Find all `.txt` files in `04.INPUT/`
4. **Discover Profiles**: Load all `.yaml` files from `03.PROFILES/`
5. **Matrix Processing**: For each prompt file × each active model:
   - Create output subfolder (`promptfile_X_profile`)
   - Generate images for each line in the prompt file
   - Save with descriptive filename
   - Track costs and failures
6. **Generate Reports**: Create summary reports in output folder

## 📊 Output Structure

```
USER-FILES/05.OUTPUT/
└── YYMMDD_HHMMSS/                    # Timestamped session folder
    ├── prompt01_X_flux_tiny_landscape/  # Combination subfolder
    │   ├── 001_142530__Line1_flux-schnell_360x240.jpeg
    │   ├── 002_142532__Line2_flux-schnell_360x240.jpeg
    │   └── ...
    ├── COST-ESTIMATION.md             # Cost breakdown
    ├── GENERATION-REPORT.md           # Success summary
    └── FAILURE-REPORT.md              # Error details (if any)
```

## 🔧 Configuration Files

### config.yaml
- **wrapper**: Timeout, retries, wait times
- **queue**: Rate limit handling
- **notifications**: Success/failure alerts

### models.yaml
- Model nicknames → FAL endpoints mapping
- Pricing information per model
- Cost calculation settings

### Profile YAML
**⚠️ Important**: Parameters are **examples only** - any parameter can be used!

- `endpoint`: Replicate model identifier (required)
- `parameters`: Any parameters supported by the model (passed through unchanged)
- `description`, `pricing`: Optional metadata
- `prompt_prefix/suffix`: Text modifications (optional)

**The script supports ANY parameter combination** - if a model needs it, add it to the profile.

**⚠️ Parameter Filtering**: APIs may silently filter out unsupported parameters. Check your payload logs if parameters seem to be ignored - this usually means the model doesn't support them.

## 🛡️ Error Handling

- **Fail-fast philosophy**: Stops on first error
- **Retry logic**: Exponential backoff for transient failures
- **Rate limiting**: Automatic delay when rate limited
- **Image validation**: Verifies all downloads with Pillow
- **Detailed logging**: Full error context in logs

## 📈 Cost Tracking

- Calculates costs based on `models.yaml` pricing
- `--cost-estimation` mode for pre-run estimates
- Generates detailed cost reports
- Tracks per-model and total costs

## 🔍 Debug Features

- `--debug` flag saves all API requests/responses
- Verbose logging with `--verbose`
- Progress bars with Rich library
- Detailed failure reports

## 🚫 Protection Rules

- Never modifies files in `USER-FILES/` without permission
- Input files remain in `04.INPUT/` (not moved after processing)
- Only reads from `04.INPUT/` and writes to `05.OUTPUT/`
- No automatic archiving or cleanup

## 📦 Dependencies

- **replicate**: Official Replicate Python client
- **loguru**: Advanced logging
- **rich**: Terminal formatting and progress bars
- **Pillow**: Image validation
- **PyYAML**: Configuration parsing
- **requests**: HTTP client for downloads
- **natsort**: Natural sorting of files
- **python-dotenv**: Environment variable management (deprecated)

## 🎯 Key Features

1. **✨ True Model Agnosticism**: Support any Replicate model through profiles only
2. **Matrix Processing**: Automatically processes all prompt × model combinations
3. **Zero Code Changes**: Add new models via YAML profiles, never touch code
4. **Pure Parameter Pass-through**: All profile parameters sent to API unchanged
5. **Cost Management**: Pre-run estimation and tracking
6. **Robust Error Handling**: API-driven validation, detailed reporting
7. **Sequential Processing**: Avoids rate limits
8. **Organized Output**: Clear folder structure with descriptive names
9. **Multiple Modes**: Dry-run, cost estimation, debug
10. **Progress Tracking**: Visual feedback during processing

## 💡 Tips

- Start with `--cost-estimation` to preview costs
- Use `--dry-run` to test configuration
- Enable `--debug` when troubleshooting API issues
- Keep prompts concise (one per line)
- Use profiles to test different model parameters
- Check logs in `logs/` folder for detailed information
- **Parameter Filtering**: If parameters seem ignored, check payload logs for filtering warnings
- **Model Compatibility**: Verify model documentation for supported parameters

## 🔐 Authentication

**Primary method**: 1Password CLI integration
1. Configure `auth.yaml` with vault/item details
2. Script automatically retrieves `REPLICATE_API_TOKEN`

**Fallback method**: Environment variable
- Set `REPLICATE_API_TOKEN` directly
- No `.env` file support (deprecated for security)
