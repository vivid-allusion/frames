# PRD Template - Batch Processing Tools

## 01. Project Definition

### 01.1 Project Description

[Describe what the tool does in 1-2 sentences]

### 01.2 Core Features

[List main features as bullet points]

### 01.3 Specific Requirements

[List technical and business requirements]

### 01.4 Project Context

**Choose ONE:**

#### Option A: Personal Tool (LLM-Operated)

- **Users**: Just me (developer/owner)
- **Operation**: Claude Code or other LLM operates on my behalf
- **Documentation**: LLM-readable (clear docstrings and comments)
- **Testing**: I test manually myself - no automated tests, no test frameworks, no test suites
- **CI/CD**: Not needed (no team, no external deployment)
- **Simplification Impact**:
  - No user documentation needed
  - No automated testing whatsoever
  - No test files or test directories
  - No release management
  - No external integrations
  - Focus exclusively on building functional scripts

#### Option B: Team/Public Tool

- **Users**: Multiple developers or end users
- **Operation**: Direct usage or automated deployment
- **Documentation**: User guides, API docs, examples
- **Testing**: Automated test suite with coverage
- **CI/CD**: Required for quality assurance
- **Requirements**:
  - Comprehensive documentation
  - Automated testing
  - Version management
  - Error recovery mechanisms
  - User support features

### 01.5 Error Handling Strategy

- **Corrupted input**: Skip file, log error, continue processing
- **API rate limit**: Exponential backoff with retry
- **Output exists**: Create new timestamped folder
- **Missing field**: Use defaults or fail with clear message

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
- Functions under 50 lines

**Error Handling**

- Custom exceptions with clear messages
- Fail fast with actionable errors
- Continue processing on individual failures
- Structured logging with Loguru

**Dependencies**

- Pin exact versions in requirements.txt
- Use standard library when sufficient
- Popular libraries (pandas, requests) over custom code
- Virtual environment isolation

**File Processing**

- Show progress for long operations
- Process in chunks for memory efficiency
- Write to temp files first
- Handle encoding issues gracefully

**Testing & Documentation**

For Personal Tools (Option A):

- Build functional scripts - I test them manually myself
- No automated tests, no test frameworks, no test files
- LLM-readable docstrings in all functions
- Clear inline comments for complex logic
- .env.example with required variables

For Team/Public Tools (Option B):

- Automated test suite with coverage
- README with comprehensive usage examples
- API documentation
- User guides and troubleshooting

---

## 03. Dependencies

### Dependencies

#### Folder Structure

```plaintext
project_root/
├── src/                    # Source code
├── docs/                   # Documentation (if needed)
├── scripts/                # Utility scripts (if needed)
├── .env.example           # Environment template
├── requirements.txt        # Python dependencies
└── USER-FILES/            # Data processing folders
    ├── 00.KB/             # Knowledge base
    ├── 01.CONFIG/         # Tool configuration
    ├── 02.STANDBY/        # Files ready for processing
    ├── 03.PROFILES/       # Processing profiles
    ├── 04.INPUT/          # Active input
    ├── 05.OUTPUT/         # Generated outputs
    ├── 06.DONE/           # Processed files
    └── 07.TEMP/           # Temporary files
```

---

## 04. Input/Output Pattern for Batch Processing Projects

### 04.1 Purpose and Scope

This pattern defines how **user organize his data files** for batch processing tools. It establishes folder conventions that scripts follow, keeping code simple while providing consistent data management.

**Key principle**: Users manage data organization; scripts follow folder conventions

### 04.2 Standard Folder Structure

```plaintext
project_root/
├── .gitignore                                        
└── USER-FILES/
    ├── 00.KB/                                         # Knowledge base and reference materials
    │   ├── reference_doc1.md                          # Reference document one
    │   ├── reference_doc2.md                          # Reference document two
    │   └── reference_doc3.md                          # Reference document three
    ├── 01.CONFIG/                                     # Configuration files for processing tools
    │   ├── config_file1.json                          # Configuration file one
    │   ├── config_file2.json                          # Configuration file two
    │   └── config_file3.json                          # Configuration file three
    ├── 02.STANDBY/                                    # Files ready for processing (ignored by script)
    │   ├── filename_example_1.ext                     # Example file one
    │   └── filename_example_2.ext                     # Example file two
    ├── 03.PROFILES/                                   # Configuration profiles for processing parameters
    │   └── profile.yaml                               # Configuration profile for each run
    ├── 04.INPUT/                                      # Active input folder (script processes this)
    │   └── filename_example_3.ext                     # Example input file
    ├── 05.OUTPUT/                                     # Generated output files and folders
    │   └── {YYMMDD}_{HHMMSS}/                         # Folder created for each script run
    │       ├── {filename_example_3}/                  # Folder created for each processed file from input
    │       │   ├── {counter}_{filename_example_3}.ext # Processed file
    │       │   ├── {filename_example_3}.log           # Detailed Loguru log file
    │       │   └── {filename_example_3}_summary.md    # Human-readable summary log
    │       └── {filename_example_3}_FAILURE.md        # Error details (if task in script run fails)
    ├── 06.DONE/                                       # Processed input files (ignored by script)
    │   ├── filename_example_4.ext                     # Example of processed file
    │   └── filename_example_5.ext                     # Example of processed file
    └── 07.TEMP/                                       # Temporary working files and reports
        ├── refactor_report.md                          # Refactoring analysis report
        └── cleanup_report.md                          # Cleanup operation report
```

### 04.3 Processing Flow Diagrams

#### Before Processing

```plaintext
02.STANDBY/ → 04.INPUT/ → [Script Processing] → 05.OUTPUT/{timestamp}/
```

#### After Processing

```plaintext
04.INPUT/ → 06.DONE/ (archived)
05.OUTPUT/{timestamp}/ (results preserved)
```

#### File Processing States

```plaintext
[New Files] → [02.STANDBY] → [04.INPUT] → [Processing] → [05.OUTPUT] → [06.DONE]
     ↓              ↓              ↓              ↓              ↓              ↓
   Prepare      Ready for      Active         Script         Results       Archived
   Files        Processing     Processing     Running        Generated     Files
```

### 04.4 Folder Descriptions

| Folder      | Purpose                        | Script Access |
| ----------- | ------------------------------ | ------------- |
| 00.KB       | Knowledge base, reference docs | Read-only     |
| 01.CONFIG   | Tool settings (JSON)           | Read-only     |
| 02.STANDBY  | Staging area for files         | Ignored       |
| 03.PROFILES | Processing profiles (YAML)     | Read-only     |
| 04.INPUT    | Active processing queue        | Read-only     |
| 05.OUTPUT   | Timestamped results            | Write-only    |
| 06.DONE     | Processed file archive         | Ignored       |
| 07.TEMP     | Working files, reports         | Read/Write    |

### 04.5 User Workflow

#### Basic Processing Flow

1. **Prepare Files**: Place files in `02.STANDBY/` when ready for processing
2. **Move to Input**: Move files from `02.STANDBY/` to `04.INPUT/` to start processing
3. **Run Script**: Execute the processing script with desired profile
4. **Check Output**: Results appear in `05.OUTPUT/{timestamp}/`
5. **Archive**: Move processed files from `04.INPUT/` to `06.DONE/`

#### Example Workflow

**Standard Processing**

1. Place files in `02.STANDBY/`
2. Move to `04.INPUT/`
3. Select profile from `03.PROFILES/`
4. Run script
5. Check results in `05.OUTPUT/{timestamp}/`
6. Archive to `06.DONE/`### 04.7 Configuration Management

| Directory   | Format   | Purpose                                |
| ----------- | -------- | -------------------------------------- |
| 01.CONFIG   | JSON     | Tool settings, API configs             |
| 03.PROFILES | YAML     | Processing parameters, transformations |
| 00.KB       | Markdown | Reference docs, guidelines             |

### 04.8 Output Organization

- Each processing run creates a timestamped folder in `05.OUTPUT/`
- Each processed file gets its own subfolder with logs and results
- Failed files are logged with detailed error information
- Summary reports provide human-readable processing results

### 04.9 Key Principles#### Data Organization

- Users control where files are placed
- Scripts follow the established folder conventions
- Clear separation between input, output, and configuration

#### Processing Safety

- Original files are never modified in place
- All outputs are generated in timestamped folders
- Failed processing doesn't affect successful results

#### Configuration Separation

- Tool configuration (how the script works) vs. processing profiles (how to process data)
- Reference materials kept separate from operational files
- Clear distinction between temporary and permanent files

### 04.10 Implementation Details

#### Logging Strategy

Each processing run generates log files organized by processed file:

**Per-File Logs (inside {filename_example_3}/ folder)**

- **Verbose Log (Loguru)** - Detailed metadata, statistics, error details for debugging
- **Summary Log (Markdown)** - Concise summary of outcomes and issues requiring attention

**Script-Level Logs (at {YYMMDD}_{HHMMSS}/ level)**

- **FAILURE.md** - If script fails, creates error details and solutions at script run level

#### File Naming and Organization

**Input Preservation**: Original folder structure is preserved in outputs.

**Timestamped Outputs**: Format `YYMMDD_HHMMSS` prevents overwrites.

**Output Directory Naming**

- **Format**: `YYMMDD_HHMMSS` (e.g., `250720_185910`)
- **No descriptive prefixes**: Avoid names like `batch_`, `processed_`, or `code_blocks_fixed_`
- **Consistency**: All processing tools use the same timestamp-only format
- **Per-file organization**: Each processed file gets its own folder with logs

**File Naming**: Maintain original names with transformation indicators.

#### Error Handling and Recovery

- **Graceful Degradation**: Continue processing despite individual failures

- **Clear Error Reporting**: Both machine and human-readable logs

- **Recovery Options**: Retry, skip, or continue from interruption

- **Performance**: Parallel processing with progress reporting

#### Processing Modes

- **Analysis Mode**: Examine files without modification, generate reports

- **Transformation Mode**: Process according to profiles, output to timestamped folders#### Technical Implementation

**Script Flow**: CONFIG → PROFILES → INPUT → OUTPUT/{timestamp}/

**File Formats**: CONFIG (JSON), PROFILES (YAML), KB (Markdown)

**Logging**: Loguru (technical) + Markdown (summaries)

**Error Handling**: Continue on failure, detailed logs, retry support

**Performance**: Parallel processing, progress reporting, memory efficiency

### 04.11 Version Control Guidelines

#### Directory Exclusion

#### Rationale for Exclusion

1. **Repository Size Management**: Input files may contain large datasets, and output files are generated content that can be very large
2. **Data Privacy**: Input files may contain sensitive or proprietary information that shouldn't be shared
3. **Reproducibility**: Output files are regenerated each time the script runs, so they don't need version control
4. **Focus on Code**: Version control should focus on the processing logic, not the data being processed

**Data Management**

- **Never commit input data** unless it's small, non-sensitive example files
- **Never commit output files** as they are regenerated content
- **Document input format** in README files instead of committing sample data
- **Use .gitkeep files** in empty directories if needed for project structure
- **Include USER-FILES directories** in project documentation so users know where to place files

**Project Structure**

- **Maintain folder structure** even when empty
- **Use .gitkeep files** in empty directories to preserve structure
- **Document the pattern** in project README files
- **Include setup instructions** for new users**Folder Preservation**: Use .gitkeep files in empty directories

#### Security Considerations

**Sensitive Data**

- **Never commit API keys** or sensitive credentials
- **Use environment variables** for sensitive configuration
- **Document required environment variables** in README files
- **Use .env files** for local development (add to .gitignore)

**Data Privacy**

- **Review input files** before committing any examples
- **Anonymize sample data** if needed for documentation
- **Use synthetic data** for examples when possible
- **Document data requirements** without exposing sensitive information

**How to Run the Script**

- **Main entry point**: `python3 -m src.main` (with venv activated)
- **Wrapper script**: Always provide `run.py` that handles complete environment setup:
  - Creates virtual environment if it doesn't exist
  - Activates the virtual environment
  - Installs/updates dependencies from requirements.txt
  - Runs the main entry point
- **Usage**: `python3 run.py` handles all setup automatically - no manual steps required

