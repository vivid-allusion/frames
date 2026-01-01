# Pre-flight Markdown Validation

## Overview

The pre-flight validation feature validates all markdown input files **before** any API processing begins. This ensures that all files are properly formatted and contain valid TEXT SOURCE sections, preventing wasted API calls and providing immediate feedback on issues.

## What Gets Validated

For each markdown file in the input directory, the validator checks:

1. **TEXT SOURCE section presence**: File must contain a `**TEXT SOURCE:**` line
2. **Text content**: The text content after TEXT SOURCE must not be empty

## Validation Rules

### ✅ Valid Files

All markdown files must follow this format:

```markdown
# frame_0288.jpg

**IMAGE SOURCE:** frame_0288.jpg

![image](https://f003.backblazeb2.com/file/wbt-bucket/ari_foldman/frame_0288.jpg)

**TEXT SOURCE:** frame_0288.txt:

Ari sits at a bar with drink, looking off camera.
```

```markdown
# Multi-line prompt example

**IMAGE SOURCE:** scene.jpg

![image](https://example.com/scene.jpg)

**TEXT SOURCE:** scene.txt:

A bearded man sits in a car holding his chin, and a passing 
armored vehicle is reflected in the window.
```

### ❌ Invalid Files

These will fail validation:

```markdown
# Missing TEXT SOURCE
**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

This is some text but no TEXT SOURCE line.
```
**Error**: No TEXT SOURCE section found. Files must contain '**TEXT SOURCE:**' line

```markdown
# Empty TEXT SOURCE
**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

**TEXT SOURCE:** test.txt:

```
**Error**: Empty text content after TEXT SOURCE. Text must be provided after the TEXT SOURCE line

```markdown
# Only whitespace after TEXT SOURCE
**IMAGE SOURCE:** test.jpg

![image](https://example.com/test.jpg)

**TEXT SOURCE:** test.txt:
   
   
```
**Error**: Empty text content after TEXT SOURCE. Text must be provided after the TEXT SOURCE line

## When Validation Runs

Pre-flight validation runs automatically:
- **After** input files are discovered
- **Before** API authentication
- **Before** any API calls are made

## Benefits

1. **Fail-fast**: Errors caught immediately, not after partial processing
2. **Cost savings**: No API credits wasted on invalid inputs
3. **Time savings**: All issues reported at once, not one-by-one during processing
4. **Clear feedback**: Error messages show exactly which files need fixing

## Error Messages

When validation fails, you'll see detailed error messages:

```
Pre-flight validation failed for 2 file(s):
  - prompts/invalid.md: No TEXT SOURCE section found. Files must contain '**TEXT SOURCE:**' line
  - prompts/empty.md: Empty text content after TEXT SOURCE. Text must be provided after the TEXT SOURCE line
```

## Implementation Details

- **Location**: `src/processing/validator.py` - `GenericValidator.validate_markdown_files()`
- **Integration**: Called in `src/orchestrator.py` - `discover_inputs_and_profiles()`
- **Exception**: Raises `ValidationError` on failure (fail-fast behavior)
- **Logging**: Logs detailed debug info for each file validated

## Testing

Test the validation with:

```bash
python test_validation_text_source.py
```

This tests:
- Valid markdown files with TEXT SOURCE sections
- Malformed markdown (missing TEXT SOURCE)
- Empty TEXT SOURCE sections
- Proper error messages

## TEXT SOURCE Format

The validator searches for the `**TEXT SOURCE:**` marker and extracts all text content that follows it:

1. Finds the line containing `**TEXT SOURCE:**`
2. Extracts all subsequent lines (skipping initial empty lines)
3. Strips whitespace and validates content is not empty

Example extraction:
```markdown
**TEXT SOURCE:** frame_0001.txt:

This is the prompt text that gets extracted.
```

Result: `"This is the prompt text that gets extracted."`

## Future Enhancements

Potential improvements:
- Validate image URL format and accessibility
- Validate prompt length constraints
- Custom validation rules per profile
- Warning vs error levels (non-blocking warnings)
- Check for required IMAGE SOURCE section
