## Agent Behaviour Rules

### General Behavior

- MUST: Ask for clarification when requirements are ambiguous
- MUST: Verify all changes work before confirming completion
- SHOULD: Run tests before committing code
- SHOULD: Provide clear explanations for complex changes
- SHOULD NOT: Make assumptions about file locations or project structure

### Error Handling

- MUST: Report errors with full context to the user
- MUST: Continue processing other items when individual items fail
- SHOULD: Suggest solutions when errors occur
- SHOULD: Validate inputs before processing
- SHOULD NOT: Silently ignore errors or warnings

## USER-FILES Protection Rules

### ABSOLUTE FORBIDDEN - USER-FILES/04.INPUT/
- MUST NEVER: Create ANY files in USER-FILES/04.INPUT/ for ANY reason
- MUST NEVER: Delete ANY files from USER-FILES/04.INPUT/ 
- MUST NEVER: Modify ANY files in USER-FILES/04.INPUT/
- MUST NEVER: Move or rename ANY files in USER-FILES/04.INPUT/
- MUST NEVER: Write test files, example files, or ANY files to USER-FILES/04.INPUT/
- CAN ONLY: Read files from USER-FILES/04.INPUT/ - nothing else

### General USER-FILES Rules
- MUST: Never create files in USER-FILES/ without explicit permission
- MUST: Never delete files in USER-FILES/ without explicit permission  
- MUST: Never modify existing files in USER-FILES/ without explicit permission
- MUST: Never move or rename files in USER-FILES/ without explicit permission
- MUST: Never auto-archive or auto-organize files in USER-FILES/
- MUST: Leave input files exactly where they are after processing
- MUST: Ask "May I create/modify/delete/move [specific file] in USER-FILES?" before any operation
- SHOULD: Treat USER-FILES/ as external user data that you DO NOT manage
- SHOULD: Only read from USER-FILES/04.INPUT/ and write to USER-FILES/05.OUTPUT/
- SHOULD NOT: Use USER-FILES/07.TEMP/ when user says "save to temp" - use project root instead
- SHOULD NOT: Implement any "cleanup" or "archiving" features for USER-FILES

## Project Structure Rules

- MUST: Read inputs only from USER-FILES/04.INPUT/
- MUST: Write outputs only to USER-FILES/05.OUTPUT/ with timestamps
- MUST: Use YYMMDD_HHMMSS format for output directories
- SHOULD: Preserve input directory structure in outputs
- SHOULD: Store configurations in appropriate USER-FILES subdirectories

## Python Code Standards

- MUST: Use type hints for all function signatures
- MUST: Use pathlib.Path for file operations (not os.path)
- SHOULD: Keep functions under 50 lines
- SHOULD: Format with black and lint with ruff
- SHOULD: Add docstrings for all public functions

## Testing Standards

- MUST: Write tests for critical functionality
- SHOULD: Test happy paths and edge cases
- SHOULD: Mock external dependencies
- SHOULD: Keep tests fast and focused
- SHOULD NOT: Test implementation details

## API Integration

- MUST: Implement rate limiting for external APIs
- MUST: Set timeouts on all requests
- SHOULD: Add retry logic with exponential backoff
- SHOULD: Log API interactions for debugging
- SHOULD NOT: Hardcode API keys or secrets

## Configuration Management

- MUST: Use environment variables for sensitive data
- MUST: Validate configuration at startup
- SHOULD: Provide sensible defaults
- SHOULD: Separate tool config from processing profiles
- SHOULD: Support different environments (dev/test/prod)

## Dependency Management

- MUST: Pin exact versions in requirements.txt
- MUST: Use virtual environments
- SHOULD: Separate dev and production dependencies
- SHOULD: Document required environment variables
- SHOULD: Keep dependencies minimal

## Error Recovery

- MUST: Log errors with full context
- MUST: Provide user-friendly error messages
- SHOULD: Support recovery from partial failures
- SHOULD: Create detailed failure reports
- SHOULD NOT: Stop entire process for single item failures

## File Processing

- MUST: Never modify original input files
- MUST: Never move input files after processing
- MUST: Create timestamped output directories
- MUST: Input files stay in USER-FILES/04.INPUT/ permanently
- SHOULD: Show progress for long operations
- SHOULD: Support dry-run mode
- SHOULD: Process files in configurable batches
- SHOULD NOT: Auto-archive processed files to USER-FILES/06.DONE/

## Known Issues & Technical Notes

### Configuration Notes
- README mentions `models.yaml` but it's not implemented - model configs are in profile YAML files
- Profile YAML files support `prompt_prefix` and `prompt_suffix` fields
- Use `delay_between_requests` in profiles for rate limiting

### Quote Handling
- Prompts are kept exactly as written in input files
- JSON escaping in saved payloads is normal JSON syntax (not sent to API)
- Clean prompt handling implemented in Replicate client

### Output Format
- Payloads are saved as Markdown files (`.md`) with JSON in codeblocks
- Use `--no-save-payloads` flag to disable payload saving
- Default behavior is to save payloads

### ✅ MAJOR MILESTONE: True Model Agnosticism Achieved
**All 16 planned tasks completed successfully!**

#### Core Implementation Changes
- **API Client**: Implemented pure parameter pass-through (lines 79-82 in src/api/client.py)
- **Processor**: Eliminated parameter extraction (line 141 in src/processing/processor.py)
- **Validator**: Replaced ImageValidator with GenericValidator
- **Context**: Removed `image_input`/`output_format` fields from ProcessingContext
- **Profiles**: All moved to new agnostic format with parameters section
- **Tests**: Created comprehensive agnosticism test suite
- **Documentation**: README updated with model agnosticism principles

#### The Manifesto Test Results
**Question**: Can you add a new model by only creating a profile?
**Answer**: ✅ YES! - `nano-banano_9x16_barkbus.yaml` works without code changes

#### Architecture Status
- **Model Agnosticism**: ✅ Successfully implemented
- **Parameter Pass-through**: ✅ Pure pass-through achieved
- **Zero Code Dependencies**: ✅ Any parameter name supported
- **Backward Compatibility**: ✅ All existing profiles updated

### ⚠️ Outstanding Critical Issues (Discovered 2025-10-15)

#### 🔴 Blocking Issues
1. **Missing replicate dependency**: `replicate>=1.0.0` not installed in environment
2. **Broken venv paths**: Virtual environment points to non-existent locations

#### 🟡 Cleanup Needed
3. **GenericValidator unused in production**: `src/processing/validator.py` — only referenced by 5 test files. Consider moving to `tests/helpers.py`.
4. **Test infrastructure**: 10 test files use manual `sys.path.insert` — needs `conftest.py` + pytest config

#### 🟢 Validation Required
5. **End-to-end testing**: Need real API call validation
6. **Profile discovery**: Confirm new agnostic format works with discovery module

### Implementation Principles Achieved
Follows AI Model Agnosticism Manifesto perfectly:
- "The script orchestrates. The profile configures. The API validates."
- No hardcoded model logic anywhere in codebase
- All profile parameters passed to API unchanged
- Any future parameter automatically supported

## Single-Profile Processing (2025-06-08)

### Feature Complete (100%)
- **Matrix Pattern Removed**: `MatrixProcessor` → `BatchProcessor`. Tool now processes all inputs against exactly one profile per run.
- **Class Rename**: `src/processing/processor.py` — `MatrixProcessor` → `BatchProcessor`. All "matrix" terminology purged from codebase.
- **Entry Point**: `python3 run.py` still works — `run.py` calls `src.main_simple` → `src.orchestrator` → `BatchProcessor`.

### Architectural Changes
- **Single-profile discovery**: `ConfigLoader.load_active_profile()` (was `load_active_profiles()`) searches `03.PROFILES/` first, falls back to `01.CONFIG/`. Fails fast on 0 or >1 profiles via `sys.exit(1)`.
- **Removed outer loop**: `BatchProcessor.process_all()` accepts a single `profile: Dict` instead of `active_models: List[Dict]`. No cartesian product.
- **Dead method deleted**: `_process_model_batch()` removed — processing loop now inline in `process_all()`.
- **Output dir naming**: `YYMMDD_HHMMSS_IMG-TO-IMG` (was `YYMMDD_HHMMSS_IMAGE`).
- **Orchestrator**: All functions (`discover_inputs_and_profiles`, `initialize_services`, `execute_processing`, `estimate_costs`, `generate_final_reports`) updated for single `profile: Dict` parameter.
- **Cost estimation**: N files × 1 profile (was N × M).

### Files Touched
| File | Change |
|------|--------|
| `src/config/loader.py` | `load_active_profiles()` → `load_active_profile()`, 01.CONFIG fallback |
| `src/processing/processor.py` | Class rename + outer loop removal |
| `src/processing/context.py` | Docstring only |
| `src/orchestrator.py` | All function signatures updated |
| `src/main_simple.py` | Import rename, `active_models` → `profile` |
| `src/main.py` | Same changes (legacy duplicate) |
| `src/utils/path_resolver.py` | `_IMAGE` → `_IMG-TO-IMG` |
| `src/utils/progress.py` | Docstring only |

### Untouched (verified)
`src/api/client.py`, `src/output/writer.py`, `src/processing/discovery.py`, `src/auth/`

### Pending Minor Cleanup (low priority, non-blocking)
1. ~~Remove dead `BatchProcessingContext` class from `src/processing/context.py`~~ **DONE (2026-06-08)**
2. ~~Remove dead `GenericValidator` import/instantiation from `src/processing/processor.py`~~ **DONE (2026-06-08)**  
3. ~~Add `01.CONFIG/` fallback to legacy `main.py`'s inline discovery~~ **OBSOLETE** (`main.py` deleted 2026-06-08)

## Refactoring Completion (2026-06-08)

### Major Cleanup Complete — 40+ Tasks, 731 Lines Removed (13.9%)

#### What Was Done
- **Deleted files**: `src/main.py` (354L duplicate), `src/auth/env.py` (32L dead .env auth)
- **Dead code removed**: 18 items (~620 lines) including:
  - Fake filtering detection (`_detect_filtering`, `_get_filtered_parameters`) from `src/api/client.py`
  - `BatchProcessingContext` dataclass from `src/processing/context.py`
  - 3 dead exception classes from `src/exceptions.py`
  - 3 dead ConfigLoader getter methods
  - `validate_operational_requirements()` from `src/processing/validator.py`
  - `validate_single_custom_input_path()` and `validate_path_exists()` from `src/utils/path_resolver.py`
  - 3 unreferenced constants from `src/constants.py`
  - Dead `self.debug` flag and `self.validator` from `src/processing/processor.py`
  - Dead `load_auth_config` re-export from `src/auth/onepassword.py`
- **Unused imports removed**: 27 across 14 files
- **Bugs fixed**: 3
  - `src/cli.py`: `--save-payloads` flag had inverted behavior (fixed to `--no-save-payloads`)
  - `test_custom_paths.py:137`: `_IMAGE` → `_IMG-TO-IMG` assertion
  - `test_custom_paths.py:13`: Import of deleted `validate_single_custom_input_path` removed
- **Tests unblocked**: 5 broken tests fixed (sys.path, renamed classes, removed params, deleted functions)
- **Structural improvements**:
  - `save_image()`: 8 params → 1 (`ImageSaveContext` dataclass)
  - `_validate_single_profile()`: complexity 18 → declarative `PARAMETER_VALIDATION_RULES` dict
  - `_save_payload()`: dead filtering detection branch removed
  - `generate_image()`: simplified from 74L → 47L after removing no-op filtering checks
  - `src/auth/__init__.py`: simplified to pure re-export (removed dead .env fallback)

#### Project Metrics (Post-Refactor)
| Metric | Before | After |
|--------|--------|-------|
| Total files | 42 | 38 |
| Total LOC | 5,264 | 4,533 |
| src/ LOC | ~2,900 | 2,308 |
| Unused imports | 27 | 0 |
| Dead code | ~620 lines | 0 |
| Known bugs | 2 | 0 |
| Broken tests | 5 | 0 |

#### Remaining Known Technical Debt (intentionally deferred)
- `_call_with_retry()`: 69L, complexity 8 — acceptable for retry loop
- `_process_single_combination()`: 65L, complexity 7 — previously refactored
- `initialize_services()` / `generate_final_reports()` / `save_reports()`: 4-5 params — acceptable
- `ReplicateClient.__init__()`: 5 params — future ClientConfig dataclass candidate
- `get_active_models()` in `src/processing/discovery.py`: misnamed (returns profiles, not models)
- `create_progress_bar()` in `src/utils/progress.py`: bypasses AliveProgressWrapper API
- `scripts/append_camera_dolly.py`: manual argv parsing (not argparse)
- No conftest.py / pytest configuration — tests use manual sys.path manipulation
- Typing modernization: `Optional[X]` → `X | None` etc. (cosmetic, Python 3.9+)
- Duplicate `OP_CLI = shutil.which("op")` in `auth.py` and `session_manager.py`
- Redundant `ensure_op_cli()` call — `get_api_key()` calls it, then `ensure_op_auth()` calls it again
- `src/auth/onepassword.py` is a pure re-export (10L) — could inline into `src/auth/__init__.py`
- `USER-FILES/03.PROFILES/` is empty — tool needs at least 1 profile to function

## Error-to-Image Rendering (2026-07-06)

### Feature Complete (100%)
- API errors are classified as recoverable (model rejection: NSFW, content policy, etc.) or fatal (auth, network)
- Recoverable errors render as red-text-on-black-background error images using PIL default font
- Error images saved as `_ERROR.png` alongside successful outputs
- Script continues processing after recoverable errors
- Reports: `SUCCESS.md` (all clean), `PARTIAL_SUCCESS.md` (mixed), `FAILURE.md` (all failed)
- Resolution sourced from profile YAML `parameters.width`/`parameters.height`, fallback 1024x1024

### Files Touched
| File | Change |
|------|--------|
| `src/output/error_image.py` | New: `generate_error_image()`, `get_image_resolution()` |
| `src/exceptions.py` | Added `RecoverableAPIError`, `FatalAPIError` |
| `src/api/client.py` | Added `_classify_and_raise()` with keyword matching |
| `src/processing/processor.py` | Catch `RecoverableAPIError` → render error image → continue |
| `src/output/writer.py` | Added `save_error_image()` method |
| `src/output/reporter.py` | Added `PARTIAL_SUCCESS.md`, derive report type from counts |
| `src/orchestrator.py` | Updated exit code logic for partial success |

### Known Issues from Post-Feature Audit (2026-07-06)
1. Error classification default is too permissive: unexpected errors (no keyword match) raised as `RecoverableAPIError` — could mask real infrastructure problems
2. `FileNotFoundError` in `orchestrator.py:50` escapes the custom exception handler in `main_simple.py` — should use `ConfigurationError`
3. `processor.py:105` instantiates `InputDiscovery` with dummy dir just to call `load_prompts()` — should be @staticmethod
4. `reporter.py:162` references `total_models` key never populated in summary — legacy from multi-profile era
5. `error_image.py:29` hardcodes `char_width = 8` — fragile PIL default font assumption
6. `src/exceptions.py` has 5 unnecessary `pass` statements after class docstrings
