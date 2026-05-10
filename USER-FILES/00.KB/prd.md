# PRD - Image-to-Image Processing Tool Migration

## 01. Project Definition

### 01.1 Project Description

Migrate the existing text-to-image API caller tool to an image-to-image processing tool. The tool will process Markdown files containing image URLs and text prompts, send them to the Replicate Nano Banana Pro API endpoint, and download the generated images using a matrix processing pattern (all inputs × all profiles).

### 01.2 Core Features

- **Markdown Input Processing**: Read and parse Markdown files from `USER-FILES/04.INPUT/` containing image URLs and text prompts
- **Image URL Extraction**: Extract image URLs from standard Markdown image syntax `![image](URL)`
- **Prompt Extraction**: Extract text content from the first code block in the Markdown file
- **Profile-Based Configuration**: Support multiple YAML profiles with different parameters, endpoints, and optional reference images
- **Image URL Array Support**: Combine markdown image URLs with optional profile reference images into array format for API payload
- **Matrix Processing**: Process all input Markdown files against all active profiles systematically
- **Replicate API Integration**: Send properly formatted JSON payloads to Replicate's Nano Banana Pro endpoint
- **Image Download**: Retrieve generated images from Replicate servers
- **Timestamped Output**: Save results to `USER-FILES/05.OUTPUT/{YYMMDD_HHMMSS}/` with consistent naming
- **Comprehensive Logging**: Generate detailed logs and human-readable summaries per processed file

### 01.3 Specific Requirements

#### Input Requirements
- **File Format**: Markdown (`.md`) files only - remove all `.txt` file support
- **Markdown Structure**: 
  - Must contain at least one `![image](URL)` syntax for image URL extraction
  - Must contain at least one code block with text prompt content
  - Metadata lines (e.g., "IMAGE SOURCE:", "TEXT SOURCE:") are informational only and ignored by the script
- **Input Location**: `USER-FILES/04.INPUT/` directory
- **File Discovery**: Use natural sorting (natsort) for deterministic processing order

#### Parsing Requirements
- **Image URL Extraction**: 
  - Extract URL from first `![image](URL)` syntax found in Markdown
  - Ignore subsequent image references
  - Fail fast with clear error if no image URL found
- **Prompt Extraction**: 
  - Extract content from first code block found (any language identifier or none)
  - Fail fast with clear error if no code block found or code block is empty
  - Apply `prompt_prefix` and `prompt_suffix` from profile YAML to extracted text

#### Profile Configuration Requirements
- **Required Fields**: 
  - `model_id`: Replicate model endpoint identifier
  - `parameters`: Dictionary of model-specific parameters
- **Optional Fields**:
  - `image_input`: Reference image URL to combine with markdown image
  - `prompt_prefix`: Text to prepend to extracted prompt
  - `prompt_suffix`: Text to append to extracted prompt
  - `delay_between_requests`: Rate limiting delay (seconds)
  - `pricing`: Cost tracking information

#### API Payload Requirements
- **Image URL Handling**:
  - If profile has `image_input`: Create array `[markdown_url, profile_url]` (order doesn't matter)
  - If profile lacks `image_input`: Send markdown URL as single-item array `[markdown_url]`
- **Prompt Construction**: Apply prefix/suffix from profile to markdown code block content
- **Parameter Pass-Through**: Include all profile parameters in payload unchanged

#### Output Requirements
- **Naming Convention**: `YYMMDD_HHMMSS_[markdown_filename].png`
  - Example: `250131_143052_example1.png`
- **Output Location**: `USER-FILES/05.OUTPUT/{YYMMDD_HHMMSS}/`
- **Folder Structure**: 
  - Each processing run creates timestamped folder
  - Each processed markdown file gets its own subfolder with outputs and logs

#### Error Handling Requirements
- **Fail Fast Philosophy**: 
  - Missing image URL in markdown: Error out immediately
  - Missing or empty code block: Error out immediately
  - Invalid YAML profile: Error out immediately
  - API authentication failure: Error out immediately
- **Continue on Individual Failures**: 
  - Single file processing failure: Log error, continue with remaining files
  - API rate limit: Implement exponential backoff with retry
  - Network timeout: Retry with backoff, then fail that specific file

#### Backward Compatibility
- **Remove Text File Support**: Completely eliminate `.txt` file processing logic
- **Update Discovery**: Change file discovery from `.txt` to `.md` pattern
- **Profile Compatibility**: Maintain existing YAML profile structure and fields

### 01.4 Project Context

**Personal Tool (LLM-Operated)**

- **Users**: Just me (developer/owner)
- **Operation**: Claude Code operates on my behalf
- **Documentation**: LLM-readable (clear docstrings and comments)
- **Testing**: Manual testing only - no automated tests, no test frameworks, no test suites
- **CI/CD**: Not needed (no team, no external deployment)
- **Simplification Impact**:
  - No user documentation needed
  - No automated testing whatsoever
  - No test files or test directories
  - No release management
  - No external integrations
  - Focus exclusively on building functional scripts

### 01.5 Error Handling Strategy

- **Missing markdown image URL**: Fail immediately with message "No image URL found in {filename}"
- **Missing/empty code block**: Fail immediately with message "No prompt text found in {filename}"
- **Invalid profile YAML**: Fail immediately with validation error details
- **API rate limit**: Exponential backoff (1s, 2s, 4s, 8s) up to 5 retries, then fail that file
- **Network timeout**: Retry once after 5s, then fail that file
- **Output directory exists**: Create new timestamped folder (timestamps prevent collisions)
- **Missing API credentials**: Fail immediately with 1Password authentication instructions

---

## 02. Minimalist Architecture Philosophy

### Core Principles

**Simplicity First**

- One purpose per file
- Self-documenting variable names
- Standard patterns only
- Functions under 50 lines
- No premature abstractions
- No custom frameworks
- Use established libraries over custom code

### Python Implementation Standards

**Code Structure**

- Type hints for all functions
- pathlib.Path for file operations
- One purpose per file
- Functions under 50 lines (soft limit 250 lines per file, hard limit 400 lines per file)

**Error Handling**

- Custom exceptions with clear messages
- Fail fast with actionable errors
- Continue processing on individual file failures
- Structured logging with Loguru

**Dependencies**

- Pin exact versions in requirements.txt
- Use standard library when sufficient
- Popular libraries (requests, replicate SDK) over custom code
- Virtual environment isolation

**File Processing**

- Show progress for long operations (rich progress bars)
- Process files sequentially (deterministic behavior)
- Natural sorting (natsort) for file discovery
- Handle encoding issues gracefully (UTF-8 default)

**Testing & Documentation**

For Personal Tools:

- Build functional scripts - manual testing only
- No automated tests, no test frameworks, no test files
- LLM-readable docstrings in all functions
- Clear inline comments for complex logic
- No README files unless explicitly requested

---

## 03. Dependencies

### Required Python Packages

```
replicate>=1.0.0
pyyaml>=6.0
loguru>=0.7.0
rich>=13.0.0
natsort>=8.4.0
Pillow>=10.0.0
```

### Folder Structure

```plaintext
img-to-img_tool/
├── src/                           # Source code
│   ├── main.py                   # Entry point
│   ├── api/                      # API client modules
│   │   └── client.py            # Replicate API client
│   ├── processing/               # Core processing logic
│   │   ├── discovery.py         # Input/profile discovery
│   │   ├── processor.py         # Matrix processing
│   │   └── validator.py         # Input validation
│   ├── output/                   # Output handling
│   │   └── writer.py            # File writing and organization
│   ├── config/                   # Configuration management
│   │   └── loader.py            # YAML config loading
│   └── auth/                     # Authentication
│       └── onepassword.py       # 1Password CLI integration
├── run.py                         # Wrapper script for zero-setup execution
├── requirements.txt               # Python dependencies
├── .gitignore                    # Version control exclusions
└── USER-FILES/                   # Data processing folders
    ├── 00.KB/                    # Knowledge base
    │   └── prd.md               # This document
    ├── 01.CONFIG/                # Tool configuration
    │   ├── config.yaml          # Main tool settings
    │   └── auth.yaml            # 1Password authentication config
    ├── 02.STANDBY/               # Files ready for processing (user-managed)
    ├── 03.PROFILES/              # Processing profiles (YAML)
    │   └── nano-banano-pro_9x16_2k_RUBEN.yaml
    ├── 04.INPUT/                 # Active input (script reads)
    │   └── example1.md
    ├── 05.OUTPUT/                # Generated outputs (script writes)
    │   └── YYMMDD_HHMMSS/       # Timestamped run folders
    ├── 06.DONE/                  # Processed files archive (user-managed)
    └── 07.TEMP/                  # Temporary files (script read/write)
```

---

## 04. Input/Output Pattern for Batch Processing Projects

### 04.1 Purpose and Scope

This tool follows the standard batch processing pattern where users organize data files in designated folders and the script follows folder conventions. The key principle: **Users manage data organization; scripts follow folder conventions**.

### 04.2 Standard Folder Structure

```plaintext
img-to-img_tool/
├── .gitignore                                        
└── USER-FILES/
    ├── 00.KB/                                         # Knowledge base and reference materials
    │   └── prd.md                                    # This product requirements document
    ├── 01.CONFIG/                                     # Configuration files for processing tools
    │   ├── config.yaml                               # Main tool configuration
    │   └── auth.yaml                                 # 1Password authentication settings
    ├── 02.STANDBY/                                    # Files ready for processing (user-managed, ignored by script)
    │   └── example2.md                               # Staged markdown file
    ├── 03.PROFILES/                                   # Configuration profiles for processing parameters
    │   ├── nano-banano-pro_9x16_2k_RUBEN.yaml       # Active profile
    │   └── nano-banano-pro_16x9_2k_landscape.yaml   # Additional profile
    ├── 04.INPUT/                                      # Active input folder (script processes this)
    │   └── example1.md                               # Markdown file to process
    ├── 05.OUTPUT/                                     # Generated output files and folders
    │   └── 250131_143052/                            # Timestamped folder for each script run
    │       ├── example1/                             # Subfolder for each processed file
    │       │   ├── 250131_143052_example1.png       # Generated image
    │       │   ├── example1.log                     # Detailed Loguru log file
    │       │   └── example1_summary.md              # Human-readable summary
    │       └── example1_FAILURE.md                   # Error details (if processing fails)
    ├── 06.DONE/                                       # Processed input files (user-managed, ignored by script)
    │   └── example0.md                               # Archived processed file
    └── 07.TEMP/                                       # Temporary working files and reports
        └── new_feature_questions.md                  # Clarification questions document
```

### 04.3 Processing Flow Diagrams

#### Before Processing

```plaintext
02.STANDBY/ → (user moves) → 04.INPUT/ → [Script Processing] → 05.OUTPUT/{YYMMDD_HHMMSS}/
```

#### After Processing

```plaintext
04.INPUT/ → (user moves) → 06.DONE/ (archived)
05.OUTPUT/{YYMMDD_HHMMSS}/ (results preserved permanently)
```

#### File Processing States

```plaintext
[New Files] → [02.STANDBY] → [04.INPUT] → [Processing] → [05.OUTPUT] → [06.DONE]
     ↓              ↓              ↓              ↓              ↓              ↓
   Prepare      Ready for      Active         Script         Results       Archived
   Files        Processing     Processing     Running        Generated     Files
```

### 04.4 Folder Descriptions

| Folder      | Purpose                                    | Script Access | Migration Changes          |
| ----------- | ------------------------------------------ | ------------- | -------------------------- |
| 00.KB       | Knowledge base, reference docs, PRD        | Read-only     | Added prd.md               |
| 01.CONFIG   | Tool settings, authentication config       | Read-only     | No changes                 |
| 02.STANDBY  | Staging area for markdown files            | Ignored       | Changed from .txt to .md   |
| 03.PROFILES | Processing profiles (YAML)                 | Read-only     | Added image_input support  |
| 04.INPUT    | Active processing queue (markdown files)   | Read-only     | Changed from .txt to .md   |
| 05.OUTPUT   | Timestamped results (images, logs)         | Write-only    | New naming convention      |
| 06.DONE     | Processed file archive                     | Ignored       | Changed from .txt to .md   |
| 07.TEMP     | Working files, reports, questions          | Read/Write    | No changes                 |

### 04.5 User Workflow

#### Basic Processing Flow

1. **Prepare Files**: Place markdown files in `02.STANDBY/` when ready for processing
2. **Move to Input**: Move markdown files from `02.STANDBY/` to `04.INPUT/` to activate processing
3. **Configure Profiles**: Ensure desired profiles are in `03.PROFILES/` with correct parameters
4. **Run Script**: Execute `python3 run.py` (zero manual setup required)
5. **Check Output**: Results appear in `05.OUTPUT/{YYMMDD_HHMMSS}/`
6. **Archive**: Move processed markdown files from `04.INPUT/` to `06.DONE/`

#### Example Workflow

**Standard Processing**

1. Create markdown file with image URL and prompt text in code block
2. Place file in `02.STANDBY/example1.md`
3. Move to `04.INPUT/example1.md`
4. Run `python3 run.py`
5. Check results in `05.OUTPUT/250131_143052/example1/`
6. Review `example1_summary.md` for processing details
7. Move `04.INPUT/example1.md` to `06.DONE/example1.md`

### 04.6 Configuration Management

| Directory   | Format   | Purpose                                          |
| ----------- | -------- | ------------------------------------------------ |
| 01.CONFIG   | YAML     | Tool settings, API configs, authentication       |
| 03.PROFILES | YAML     | Processing parameters, model settings, endpoints |
| 00.KB       | Markdown | Reference docs, PRD, guidelines                  |

#### Profile YAML Structure

```yaml
# Replicate Profile
model_id: "google/nano-banana-pro"

# Pricing information (optional, for cost tracking)
pricing:
  base_cost: 0.14
  currency: "USD"

# Model parameters (required)
parameters:
  aspect_ratio: "9:16"
  output_format: "png"
  num_images: 1
  resolution: "2K"
  safety_filter_level: "block_only_high"

# Image input configuration (optional)
image_input: "https://f003.backblazeb2.com/file/bites-client-ref/ruben_montage9x16.png"

# Processing options (optional)
delay_between_requests: 1.0

# Prompt modifications (optional)
prompt_suffix: "Provided image shows what Ruben actually looks like."
```

### 04.7 Output Organization

- **Timestamped Folders**: Each processing run creates `05.OUTPUT/YYMMDD_HHMMSS/`
- **Per-File Subfolders**: Each processed markdown file gets its own subfolder
- **Image Naming**: `YYMMDD_HHMMSS_[markdown_filename].png`
- **Logs**: Both detailed Loguru logs and human-readable Markdown summaries
- **Failure Reports**: `[filename]_FAILURE.md` for files that fail processing

### 04.8 Key Principles

#### Data Organization

- Users control where files are placed
- Scripts follow the established folder conventions
- Clear separation between input, output, and configuration

#### Processing Safety

- Original files are never modified in place
- All outputs are generated in timestamped folders
- Failed processing doesn't affect successful results
- Input files remain in `04.INPUT/` until user archives them

#### Configuration Separation

- Tool configuration (how the script works) vs. processing profiles (how to process data)
- Reference materials kept separate from operational files
- Clear distinction between temporary and permanent files

### 04.9 Implementation Details

#### Logging Strategy

Each processing run generates log files organized by processed file:

**Per-File Logs (inside {filename}/ folder)**

- **Verbose Log (Loguru)**: Detailed metadata, API calls, timing, error details for debugging
- **Summary Log (Markdown)**: Concise summary of outcomes, parameters used, issues requiring attention

**Script-Level Logs (at {YYMMDD_HHMMSS}/ level)**

- **FAILURE.md**: If file processing fails, creates error details with markdown filename and solutions

#### File Naming and Organization

**Input Preservation**: Original markdown files remain in `04.INPUT/` until user moves them

**Timestamped Outputs**: Format `YYMMDD_HHMMSS` prevents overwrites

**Output File Naming**

- **Format**: `YYMMDD_HHMMSS_[markdown_filename].png`
- **Example**: `250131_143052_example1.png`
- **Consistency**: All outputs from same run share same timestamp prefix

**Output Directory Naming**

- **Format**: `YYMMDD_HHMMSS` (e.g., `250131_143052`)
- **No descriptive prefixes**: Avoid names like `batch_`, `processed_`, or `img2img_`
- **Consistency**: All processing tools use the same timestamp-only format
- **Per-file organization**: Each processed file gets its own subfolder with logs

#### Error Handling and Recovery

- **Fail Fast**: Missing image URL or prompt causes immediate error with clear message
- **Continue Processing**: Individual file failures don't stop entire batch
- **Clear Error Reporting**: Both machine-readable logs and human-readable summaries
- **Retry Logic**: API rate limits handled with exponential backoff
- **Performance**: Sequential processing with progress reporting via rich library

#### Processing Modes

- **Standard Mode**: Process all markdown files in `04.INPUT/` against all profiles in `03.PROFILES/`
- **Dry Run Mode**: Parse and validate inputs without making API calls
- **Matrix Pattern**: All inputs × All profiles = Total operations

#### Technical Implementation

**Script Flow**: CONFIG → PROFILES → INPUT → PARSE → API → OUTPUT/{timestamp}/

**File Formats**: CONFIG (YAML), PROFILES (YAML), KB (Markdown), INPUT (Markdown), OUTPUT (PNG, MD, LOG)

**Logging**: Loguru (technical logs) + Markdown (summaries)

**Error Handling**: Fail fast on critical errors, continue on individual failures, retry with backoff for rate limits

**Performance**: Sequential processing, progress reporting with rich, natural sorting with natsort

### 04.10 Version Control Guidelines

#### Directory Exclusion

The following directories are excluded from version control:

- `USER-FILES/02.STANDBY/` - User staging area
- `USER-FILES/04.INPUT/` - Active processing queue
- `USER-FILES/05.OUTPUT/` - Generated content
- `USER-FILES/06.DONE/` - User archive
- `USER-FILES/07.TEMP/` - Temporary files

#### Rationale for Exclusion

1. **Repository Size Management**: Input markdown files and output images can be very large
2. **Data Privacy**: Input files may contain sensitive image URLs or prompts
3. **Reproducibility**: Output files are regenerated each time the script runs
4. **Focus on Code**: Version control should focus on the processing logic, not the data

**Data Management**

- **Never commit input data** unless it's small, non-sensitive example files
- **Never commit output files** as they are regenerated content
- **Document input format** in this PRD instead of committing sample data
- **Use .gitkeep files** in empty directories if needed for project structure
- **Include USER-FILES directories** in project documentation so users know where to place files

**Project Structure**

- **Maintain folder structure** even when empty
- **Use .gitkeep files** in empty directories to preserve structure
- **Document the pattern** in this PRD
- **Include setup instructions** for new users

**Folder Preservation**: Use .gitkeep files in empty directories

#### Security Considerations

**Sensitive Data**

- **Never commit API keys** or sensitive credentials
- **Use 1Password CLI** for authentication (REPLICATE_API_TOKEN)
- **Document required environment variables** in auth.yaml
- **Use environment variables** for sensitive configuration

**Data Privacy**

- **Review input files** before committing any examples
- **Anonymize sample data** if needed for documentation
- **Use synthetic data** for examples when possible
- **Document data requirements** without exposing sensitive information

### 04.11 How to Run the Script

- **Main entry point**: `python3 -m src.main` (with venv activated)
- **Wrapper script**: Always use `run.py` that handles complete environment setup:
  - Creates virtual environment if it doesn't exist
  - Activates the virtual environment
  - Installs/updates dependencies from requirements.txt
  - Runs the main entry point
- **Zero-setup usage**: `python3 run.py` handles all setup automatically - no manual steps required

---

## 05. Detailed Technical Specifications

### 05.1 Markdown File Format

#### Required Structure

```markdown
# [Optional Title]

**IMAGE SOURCE:** [Optional metadata for user reference]

![image](https://example.com/image.jpg)

**TEXT SOURCE:** [Optional metadata for user reference]

```text
Your prompt text goes here.
This can be multiple lines.
```
```

#### Parsing Rules

1. **Image URL Extraction**:
   - Search for first occurrence of `![image](URL)` or `![alt-text](URL)`
   - Extract URL from parentheses
   - Ignore all metadata lines ("IMAGE SOURCE:", etc.)
   - Use only first image found, ignore subsequent images
   - Fail immediately if no image syntax found

2. **Prompt Text Extraction**:
   - Search for first code block (triple backticks)
   - Extract all text content between opening and closing backticks
   - Ignore language identifier (can be `text`, `python`, or none)
   - Trim leading/trailing whitespace from extracted content
   - Fail immediately if no code block found or code block is empty

3. **Metadata Lines**: Completely ignored by parser (informational for user troubleshooting only)

### 05.2 API Payload Construction

#### Base Payload Structure

```json
{
  "aspect_ratio": "9:16",
  "image_input": ["https://markdown_url.jpg", "https://profile_url.jpg"],
  "output_format": "png",
  "prompt": "prefix + markdown_codeblock_content + suffix",
  "resolution": "2K",
  "safety_filter_level": "block_only_high",
  "num_images": 1
}
```

#### Image Input Array Logic

**Scenario 1: Profile has `image_input` field**

```python
# Profile YAML
image_input: "https://profile_reference.jpg"

# Markdown file
![image](https://markdown_source.jpg)

# Resulting payload
"image_input": [
    "https://markdown_source.jpg",
    "https://profile_reference.jpg"
]
```

**Scenario 2: Profile lacks `image_input` field**

```python
# Profile YAML
# (no image_input field)

# Markdown file
![image](https://markdown_source.jpg)

# Resulting payload
"image_input": [
    "https://markdown_source.jpg"
]
```

#### Prompt Construction Logic

```python
# Profile YAML
prompt_prefix: "Create a photorealistic image. "
prompt_suffix: " Shot on 35mm film."

# Markdown code block
"""
A man carries heavy bags on a ship dock.
"""

# Resulting payload
"prompt": "Create a photorealistic image. A man carries heavy bags on a ship dock. Shot on 35mm film."
```

**Edge Cases**:
- Empty `prompt_prefix`: Use markdown content + suffix
- Empty `prompt_suffix`: Use prefix + markdown content
- Both empty: Use markdown content verbatim
- Empty markdown content: Fail immediately (no code block or empty code block)

### 05.3 Matrix Processing Logic

#### Discovery Phase

1. Scan `03.PROFILES/` for all `.yaml` and `.yml` files
2. Scan `04.INPUT/` for all `.md` files
3. Apply natural sorting (natsort) to markdown files
4. Validate all profiles have required fields (`model_id`, `parameters`)

#### Processing Phase

```python
for markdown_file in sorted_markdown_files:
    for profile in all_profiles:
        # Parse markdown
        image_url = extract_image_url(markdown_file)
        prompt_text = extract_prompt_text(markdown_file)
        
        # Build payload
        payload = build_payload(profile, image_url, prompt_text)
        
        # Call API
        result = replicate_client.run(profile.model_id, payload)
        
        # Save output
        output_path = f"{timestamp}_{markdown_file.stem}.png"
        save_image(result, output_path)
        
        # Apply rate limiting
        time.sleep(profile.delay_between_requests)
```

#### Output Organization

```
05.OUTPUT/
└── 250131_143052/                    # Timestamp for this run
    ├── example1/                     # Subfolder for example1.md
    │   ├── 250131_143052_example1.png
    │   ├── example1.log
    │   └── example1_summary.md
    └── example2/                     # Subfolder for example2.md
        ├── 250131_143052_example2.png
        ├── example2.log
        └── example2_summary.md
```

### 05.4 Error Handling Specifications

#### Validation Errors (Fail Immediately)

| Error Condition                   | Error Message                                          | Action      |
| --------------------------------- | ------------------------------------------------------ | ----------- |
| No image URL in markdown          | `No image URL found in {filename}.md`                  | sys.exit(1) |
| No code block in markdown         | `No prompt text found in {filename}.md`                | sys.exit(1) |
| Empty code block in markdown      | `Empty prompt in {filename}.md`                        | sys.exit(1) |
| Invalid profile YAML              | `Invalid YAML in {profile_path}: {yaml_error}`         | sys.exit(1) |
| Missing model_id in profile       | `Profile {name} missing required field 'model_id'`     | sys.exit(1) |
| No markdown files in 04.INPUT     | `No .md files found in {input_dir}`                    | sys.exit(1) |
| No profiles in 03.PROFILES        | `No YAML profiles found in {profiles_dir}`             | sys.exit(1) |
| 1Password authentication failure  | `Failed to retrieve API token from 1Password: {error}` | sys.exit(1) |

#### Processing Errors (Log and Continue)

| Error Condition      | Error Message                                    | Action                             |
| -------------------- | ------------------------------------------------ | ---------------------------------- |
| API rate limit       | `Rate limit hit, retrying in {backoff}s`         | Exponential backoff, 5 retries max |
| Network timeout      | `Network timeout for {filename}, retrying once`  | Retry once after 5s                |
| API error response   | `API error for {filename}: {error_details}`      | Log to FAILURE.md, continue        |
| Image download error | `Failed to download image for {filename}: {why}` | Log to FAILURE.md, continue        |

#### Retry Logic

```python
# Exponential backoff for rate limits
retries = 5
backoff_seconds = [1, 2, 4, 8, 16]

for attempt in range(retries):
    try:
        result = api_client.run(payload)
        break
    except RateLimitError:
        if attempt < retries - 1:
            time.sleep(backoff_seconds[attempt])
        else:
            raise  # Final retry failed
```

### 05.5 Output File Specifications

#### Image Files

- **Format**: PNG (forced conversion if API returns other format)
- **Naming**: `YYMMDD_HHMMSS_[markdown_filename].png`
- **Location**: `05.OUTPUT/{YYMMDD_HHMMSS}/{markdown_filename}/`

#### Log Files

**Detailed Log (`{markdown_filename}.log`)**:
- Loguru format with timestamps
- API request/response details
- Parameter values used
- Timing information
- Error stack traces

**Summary Log (`{markdown_filename}_summary.md`)**:
```markdown
# Processing Summary: example1.md

**Timestamp**: 2025-01-31 14:30:52
**Profile**: nano-banano-pro_9x16_2k_RUBEN
**Status**: Success

## Input
- **Markdown File**: example1.md
- **Image URL**: https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png
- **Prompt**: A man carries heavy bags on a ship dock.

## Processing
- **Model**: google/nano-banana-pro
- **Parameters**: aspect_ratio=9:16, resolution=2K, output_format=png
- **API Cost**: $0.14 USD

## Output
- **Generated Image**: 250131_143052_example1.png
- **Processing Time**: 12.3 seconds

## Notes
- No errors encountered
```

**Failure Log (`{markdown_filename}_FAILURE.md`)**:
```markdown
# Processing Failure: example1.md

**Timestamp**: 2025-01-31 14:30:52
**Profile**: nano-banano-pro_9x16_2k_RUBEN
**Status**: Failed

## Error Details
- **Error Type**: APIError
- **Message**: Rate limit exceeded

## Stack Trace
[Full stack trace here]

## Suggested Actions
1. Wait 60 seconds and retry
2. Check API rate limits in 1Password vault
3. Reduce delay_between_requests in profile
```

---

## 06. Migration Implementation Plan

### 06.1 Files to Modify

#### `src/processing/discovery.py`
- **Change**: Replace `.txt` file discovery with `.md` file discovery
- **Lines to modify**: 35-36, 43
- **New logic**: `self.input_dir.rglob("*.md")`

#### `src/processing/processor.py`
- **Add**: Markdown parsing functions
  - `extract_image_url(markdown_content: str) -> str`
  - `extract_prompt_text(markdown_content: str) -> str`
- **Change**: Update prompt loading to call new parsing functions
- **Change**: Update payload construction to build `image_input` array

#### `src/output/writer.py`
- **Change**: Update output filename pattern
- **Old**: `{filename}_{profile}_{timestamp}.png`
- **New**: `{timestamp}_{filename}.png`

### 06.2 New Functions Required

#### Markdown Parsing Module

```python
def extract_image_url(markdown_content: str) -> str:
    """
    Extract first image URL from markdown ![image](URL) syntax.
    
    Args:
        markdown_content: Full markdown file content
        
    Returns:
        Extracted image URL
        
    Raises:
        ValueError: If no image URL found
    """
    import re
    pattern = r'!\[.*?\]\((https?://[^\)]+)\)'
    match = re.search(pattern, markdown_content)
    if not match:
        raise ValueError("No image URL found in markdown")
    return match.group(1)


def extract_prompt_text(markdown_content: str) -> str:
    """
    Extract text content from first code block in markdown.
    
    Args:
        markdown_content: Full markdown file content
        
    Returns:
        Extracted prompt text (stripped of whitespace)
        
    Raises:
        ValueError: If no code block found or code block is empty
    """
    import re
    pattern = r'```[a-zA-Z]*\n(.*?)\n```'
    match = re.search(pattern, markdown_content, re.DOTALL)
    if not match:
        raise ValueError("No code block found in markdown")
    
    content = match.group(1).strip()
    if not content:
        raise ValueError("Empty code block in markdown")
    
    return content
```

#### Payload Construction Update

```python
def build_image_input_array(markdown_url: str, profile_url: str = None) -> list:
    """
    Build image_input array combining markdown and profile URLs.
    
    Args:
        markdown_url: Image URL extracted from markdown
        profile_url: Optional reference image URL from profile
        
    Returns:
        Array of image URLs (always returns array, even for single URL)
    """
    if profile_url:
        return [markdown_url, profile_url]
    else:
        return [markdown_url]
```

### 06.3 Testing Checklist (Manual)

- [ ] Parse example1.md successfully
- [ ] Extract correct image URL from markdown
- [ ] Extract correct prompt text from code block
- [ ] Build payload with profile image_input (array with 2 URLs)
- [ ] Build payload without profile image_input (array with 1 URL)
- [ ] Apply prompt_prefix and prompt_suffix correctly
- [ ] Handle missing image URL (fail fast)
- [ ] Handle missing code block (fail fast)
- [ ] Handle empty code block (fail fast)
- [ ] Generate correct output filename: `YYMMDD_HHMMSS_example1.png`
- [ ] Create timestamped output directory
- [ ] Process multiple markdown files in sequence
- [ ] Matrix processing: 2 markdown files × 2 profiles = 4 operations
- [ ] Natural sorting of markdown files
- [ ] Rate limiting with delay_between_requests
- [ ] Generate detailed logs
- [ ] Generate summary markdown files
- [ ] Handle API rate limit with retry
- [ ] Continue processing after individual file failure
- [ ] No .txt file processing (completely removed)

---

## 07. Reference Materials

### 07.1 Example Payload

This is the target API payload structure based on user specifications:

```json
{
  "aspect_ratio": "16:9",
  "image_input": [
    "https://replicate.delivery/pbxt/OKIOqbsi63QXqRidSeUhK8e31D7N0kPsb1pZKJVVME5snry0/frame_0395.jpg",
    "https://replicate.delivery/pbxt/OKIOq0wMk5MMbevLH7zkhVqYhnfLzQwlPagVHNI6k3vJ8Mu2/Ronny_Dayag.jpg",
    "https://replicate.delivery/pbxt/OKIOpipRdVZ1Gyoh0irSYc6f9ZLdUIDKR1EsOH9prciDcTwm/ari_foldman.png"
  ],
  "output_format": "png",
  "prompt": "Create an exact photorealistic version of the drawing in provided image \"frame_0395.jpg\". The drawing depicts a scene where Ari Foldman is showing a photograph to Ronny Dayag in a Israeli food lab. Provided image \"ari_foldman.png\" shows what Ari actually looks like. Provided image \"Ronny_Dayag.jpg\" shows what Ronny Dayag actually looks like. Shot on 35 mm film in the style of Roger Deakins.",
  "resolution": "2K",
  "safety_filter_level": "block_only_high"
}
```

**Key observations**:
- `image_input` is always an array, even with single URL
- Multiple images are supported by the API
- For this migration: markdown provides 1 URL, profile optionally provides 1 URL = max 2 URLs per request
- All other parameters come from profile YAML unchanged

### 07.2 Example Markdown Input File

File: `USER-FILES/04.INPUT/example1.md`

```markdown
# prompt09.0.png

**IMAGE SOURCE:** prompt09.0.png

![image](https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png)

**TEXT SOURCE:** prompt09.0.txt:

```text
A man carries heavy bags on a ship dock.
```
```

**Parsing results**:
- Image URL: `https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png`
- Prompt text: `A man carries heavy bags on a ship dock.`
- Metadata ignored: All "IMAGE SOURCE:" and "TEXT SOURCE:" lines

### 07.3 Example Profile YAML

File: `USER-FILES/03.PROFILES/nano-banano-pro_9x16_2k_RUBEN.yaml`

```yaml
# Replicate Profile
model_id: "google/nano-banana-pro"

# Pricing information (optional, for cost tracking)
pricing:
  base_cost: 0.14
  currency: "USD"

# Model parameters (required)
parameters:
  aspect_ratio: "9:16"
  output_format: "png"
  num_images: 1
  resolution: "2K"
  safety_filter_level: "block_only_high"

# Image input configuration (optional)
image_input: "https://f003.backblazeb2.com/file/bites-client-ref/ruben_montage9x16.png"

# Processing options (optional)
delay_between_requests: 1.0

# Prompt modifications (optional)
prompt_suffix: "Provided image shows what Ruben actually looks like."
```

**Resulting payload when combined with example1.md**:

```json
{
  "aspect_ratio": "9:16",
  "image_input": [
    "https://f003.backblazeb2.com/file/isof-bucket/batch6_upscaled/prompt09.0.png",
    "https://f003.backblazeb2.com/file/bites-client-ref/ruben_montage9x16.png"
  ],
  "output_format": "png",
  "num_images": 1,
  "prompt": "A man carries heavy bags on a ship dock. Provided image shows what Ruben actually looks like.",
  "resolution": "2K",
  "safety_filter_level": "block_only_high"
}
```

---

## 08. Success Criteria

### 08.1 Functional Requirements

- [ ] Script successfully processes `.md` files from `04.INPUT/`
- [ ] All `.txt` file processing logic removed
- [ ] Markdown image URLs extracted correctly
- [ ] Markdown prompt text extracted correctly
- [ ] Profile YAML files loaded and parsed correctly
- [ ] `image_input` arrays constructed correctly (1 or 2 URLs)
- [ ] Prompt prefix/suffix applied to markdown text
- [ ] API payloads sent to Replicate successfully
- [ ] Images downloaded and saved with correct naming: `YYMMDD_HHMMSS_[filename].png`
- [ ] Output folders created with timestamp: `05.OUTPUT/YYMMDD_HHMMSS/`
- [ ] Detailed logs generated per file
- [ ] Summary markdown files generated per file
- [ ] Failure markdown files generated for errors
- [ ] Matrix processing works: all inputs × all profiles
- [ ] Natural sorting applied to input files
- [ ] Rate limiting respected with `delay_between_requests`

### 08.2 Error Handling Requirements

- [ ] Missing image URL in markdown: Fails immediately with clear message
- [ ] Missing code block in markdown: Fails immediately with clear message
- [ ] Empty code block in markdown: Fails immediately with clear message
- [ ] Invalid profile YAML: Fails immediately with validation details
- [ ] API rate limit: Retries with exponential backoff (5 attempts)
- [ ] Network timeout: Retries once, then logs failure and continues
- [ ] Individual file failure: Logs error, continues processing other files
- [ ] 1Password authentication failure: Fails immediately with instructions

### 08.3 Code Quality Requirements

- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] All functions under 50 lines
- [ ] All files under 250 lines (soft limit) / 400 lines (hard limit)
- [ ] Uses pathlib.Path for all file operations
- [ ] Uses natsort for file discovery
- [ ] Uses loguru for logging
- [ ] Uses rich for progress display
- [ ] No premature abstractions
- [ ] Clear, self-documenting variable names
- [ ] Inline comments for complex logic only

### 08.4 Documentation Requirements

- [ ] This PRD document exists in `USER-FILES/00.KB/prd.md`
- [ ] Docstrings in all functions explain purpose and behavior
- [ ] Inline comments for complex parsing logic
- [ ] No additional documentation required (personal tool)

---

## 09. Future Considerations (Not for Current Implementation)

These are explicitly **NOT** part of this migration and should **NOT** be implemented unless explicitly requested:

- Multiple image support per markdown file (current: first image only)
- Different output formats (current: PNG only)
- Parallel processing (current: sequential only)
- Retry configuration in profiles (current: hardcoded retry logic)
- Custom output naming templates (current: fixed format)
- Dry-run mode for testing (current: live API calls only)
- Cost reporting across runs (current: per-file cost only)
- Auto-archiving to 06.DONE (current: manual user action)
- Markdown validation beyond required fields (current: minimal validation)
- Image URL accessibility checks (current: trust URLs are valid)
- Support for local image files (current: URLs only)
- Batch size limiting (current: process all files found)

**Remember**: Make it work. Keep it simple. Move on.

---

**END OF PRD**
