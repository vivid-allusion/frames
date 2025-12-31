# Python Progress Bar Implementation Manifesto

## Core Philosophy

Progress bars are not optional polish—they are critical user feedback mechanisms for long-running processes. A well-implemented progress bar provides:

- **Precise state awareness**: What's happening right now
- **Time intelligence**: How long until completion
- **Resource visibility**: What resources are being consumed
- **Error detection**: When something is going wrong
- **Visual appeal**: Professional, modern aesthetics

Mediocre progress bars are worse than none. If you're going to show progress, make it comprehensive, accurate, and visually striking.

## Package Selection Strategy

### Use Rich When:

- You need multiple concurrent progress bars
- You want integrated console output alongside progress
- The task has nested/hierarchical subtasks
- You need custom columns (speed, ETA, custom metrics)
- You want table-based layouts or complex terminal UIs with Live, Group, Panel
- You're building a production-grade CLI tool
- You need transient progress that disappears after completion
- You want to integrate progress with file operations automatically
- You need precise control over refresh rates and performance
- You want to extend default columns with get_default_columns()

### Use alive-progress When:

- You have a single primary task to track
- You want maximum visual flair with minimal code
- The process is linear and straightforward
- You want animated spinners and bars that "feel alive"
- Quick scripts where setup time matters
- You need dual-line mode for longer status messages
- You want the unique pause/resume capability for interactive debugging
- You need automatic unit scaling (3.0+)
- You want reactive spinners that speed up/slow down with actual throughput
- You want to use themes for instant beautiful styling

### Use Both When:

- Complex workflows with both high-level and detailed progress
- You want alive-progress for main task, Rich for sub-operations
- Different stages of processing need different visual treatments

## Unique Killer Features

### Rich: The Professional's Choice

1. **Live Display Composition** - Combine progress bars with tables, panels, and any renderable
2. **Custom Columns System** - Create domain-specific columns that update in real-time
3. **get_default_columns()** - Extend defaults without rewriting everything
4. **Transient Mode** - Progress bars that vanish when done for clean terminal output
5. **File Operations Integration** - progress.open() and wrap_file() for automatic file progress
6. **TaskProgressColumn with show_speed** - Shows processing rate in percentage column
7. **Multi-threading Friendly** - Built-in support for concurrent operations

### alive-progress: The Most Animated Progress Bar Ever

1. **Pause/Resume Mechanism** - UNPRECEDENTED: Return to Python prompt mid-process, fix items, resume
2. **Reactive Spinners** - Spinners that speed up/slow down based on actual processing speed
3. **Dual-Line Mode** - Put lengthy text BELOW the bar instead of cramping it
4. **Automatic Unit Scaling** - Smart B→KB→MB→GB conversion (3.0+)
5. **Check Tool** - Design and preview custom animations before using them
6. **Zero/Negative Increments** - Support for rollback scenarios (bar goes backwards!)
7. **Enriched Print** - Automatic position tracking in print statements
8. **Skipped Items Tracking** - Improves ETA accuracy when skipping items
9. **Unknown Mode Animations** - Beautiful animations when total is unknown
10. **Theme System** - One parameter for complete beautiful styling

## Rich Implementation Standards

### Mandatory Features

1. **Use Progress with Multiple Columns**
   
   ```python
   from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn, MofNCompleteColumn, TransferSpeedColumn, TaskProgressColumn
   
   # Option 1: Full custom columns
   progress = Progress(
       SpinnerColumn(),
       TextColumn("[bold blue]{task.description}"),
       BarColumn(complete_style="green", finished_style="bold green"),
       TaskProgressColumn(),  # Shows percentage
       MofNCompleteColumn(),
       TextColumn("•"),
       TimeElapsedColumn(),
       TextColumn("•"),
       TimeRemainingColumn(elapsed_when_finished=True, compact=False),
       TextColumn("•"),
       TransferSpeedColumn(),  # If applicable
       transient=False,  # Set True to clear on completion
       expand=False,  # Set True to use full terminal width
       refresh_per_second=10,
       speed_estimate_period=30.0,
   )
   
   # Option 2: Extend defaults with get_default_columns()
   progress = Progress(
       SpinnerColumn(),
       *Progress.get_default_columns(),
       TimeElapsedColumn(),
       TransferSpeedColumn(),
   )
   ```

2. **Always Show:**
   
   - Task description (what's happening)
   - Visual bar (completion percentage)
   - Numeric progress (X of Y items)
   - Time elapsed
   - Time remaining
   - Spinner for active tasks
   - Processing rate when applicable (items/sec, MB/s, etc.)

3. **Custom Columns for Domain-Specific Metrics**
   
   - For ML training: loss, accuracy, learning rate
   - For data processing: rows/sec, error count
   - For file operations: current file name, size
   - For network operations: bandwidth, retry count

4. **Use Live Context for Rich Output**
   
   ```python
   from rich.live import Live
   from rich.table import Table
   
   with Live(generate_table(), refresh_per_second=4) as live:
       # Update table in real-time alongside progress
   ```

5. **Console Integration**
   
   - Use `progress.console.print()` for messages that should persist
   - Never use regular `print()` inside progress contexts
   - Color-code messages: green for success, yellow for warnings, red for errors
   - Use `progress.console.log()` for timestamped entries

### Visual Requirements

- **Colors**: Use semantic colors consistently
  
  - Blue/Cyan for active processes
  - Green for completed tasks
  - Yellow/Orange for warnings or slow progress
  - Red for errors or failed tasks
  - Magenta/Purple for special operations

- **Bar Styles**: 
  
  - `complete_style="bold green"` for finished sections
  - `finished_style="bold green"` for fully completed bars
  - Pulse effect for indeterminate operations

- **Spinners**: Always use spinners for active tasks
  
  - `dots`, `dots12`, `arc`, `clock`, `moon`, `bouncingBar` are visually appealing
  - Match spinner to task nature (e.g., `clock` for time-based operations)

### Advanced Patterns

1. **Nested Progress Tracking**
   
   ```python
   with progress:
       main_task = progress.add_task("[cyan]Main Process", total=100)
       for batch in batches:
           batch_task = progress.add_task(f"[yellow]Batch {batch}", total=len(items))
           # Process items
           progress.update(batch_task, advance=1)
       progress.update(main_task, advance=1)
   
   # Nested with track() - inner bar is transient
   from rich.progress import track
   for outer in track(range(10)):
       for inner in track("ABCDEF", transient=True):
           process(outer, inner)
   ```

2. **Dynamic Task Updates with Custom Fields**
   
   ```python
   # Add custom fields accessible via task.fields
   progress.update(
       task_id,
       description=f"[cyan]Processing: {item.name}",
       advance=1,
       current_file=item.name,  # Custom field
       phase="extraction"  # Another custom field
   )
   
   # Reference in custom columns:
   # TextColumn("{task.fields[current_file]}")
   ```

3. **Live Display with Group and Panel**
   
   ```python
   from rich.live import Live
   from rich.console import Group
   from rich.panel import Panel
   from rich.table import Table
   
   # Combine progress with live-updating table
   progress1 = Progress(...)
   progress2 = Progress(...)
   table = Table()
   
   with Live(Group(
       Panel(progress1, title="Main Tasks"),
       Panel(progress2, title="Subtasks"),
       table
   ), refresh_per_second=4) as live:
       # Update any component
       live.update(Group(...))  # Refresh display
   ```

4. **Transient Progress (Disappears on Completion)**
   
   ```python
   # For clean terminal output
   with Progress(transient=True) as progress:
       task = progress.add_task("Temporary task", total=100)
       # Progress bar vanishes when context exits
   ```

5. **File Operations with Progress**
   
   ```python
   # Automatic progress for file reading
   import rich.progress
   with rich.progress.open("large_file.json", "rb") as file:
       data = json.load(file)
   
   # Or wrap existing file object
   with open("file.dat", "rb") as f:
       with progress.wrap_file(f, total=file_size) as file:
           data = file.read()
   ```

6. **Control Progress Without Context Manager**
   
   ```python
   progress = Progress()
   progress.start()
   try:
       task = progress.add_task("Processing", total=100)
       # ... work ...
       progress.advance(task)
   finally:
       progress.stop()
   ```

7. **Error Handling in Progress**
   
   ```python
   try:
       # processing
   except Exception as e:
       progress.console.print(f"[red]Error: {e}")
       progress.update(task_id, description=f"[red]Failed: {task.description}")
   ```

8. **Hidden/Visible Tasks**
   
   ```python
   # Start with hidden task, reveal when needed
   task = progress.add_task("Secret task", total=100, visible=False)
   # Later...
   progress.update(task, visible=True)
   ```

## alive-progress Implementation Standards

### Mandatory Features

1. **Bar Style Selection**
   
   - Use high-contrast bars: `classic`, `smooth`, `blocks`, `bubbles`, `solid`, `halloween`, `filling`, `circles`, `squares`, `charging`
   - Avoid low-visibility bars in default terminals
   - Test bar visibility in your actual terminal environment
   - Use `show_bars()` from `alive_progress.styles` to preview all available bar styles

2. **Spinner Configuration**
   
   - Always use a spinner for visual interest
   - Recommended: `dots_waves`, `dots_recur`, `pulsating`, `radioactive`, `fireworks`, `fish_bouncing`, `dots`, `waves`, `moon`, `arc`
   - Match spinner energy to task duration (calm for long tasks, energetic for short)
   - Use `show_spinners()` from `alive_progress.styles` to preview all available spinner styles
   - Use `show_themes()` to see complete theme combinations

3. **Dual-Line Mode for Longer Messages**
   
   ```python
   from alive_progress import alive_bar
   
   # CRITICAL FEATURE: dual_line puts text BELOW the bar
   with alive_bar(total, dual_line=True, title='Processing Data', bar='smooth', spinner='dots_waves') as bar:
       for item in items:
           bar.text = f'→ Currently processing: {item.name}\nPhase: {item.phase}'
           # Text appears BELOW the progress bar, not cramped into it
           process(item)
           bar()
   ```

4. **Title and Text Updates**
   
   ```python
   with alive_bar(total, title='Processing Data', bar='smooth', spinner='dots_waves') as bar:
       bar.text = f'Current: {item_name}'  # Update frequently
       # Or update both progress and text
       bar(text=f'Processing {item_name}')
       # Or just increment
       bar()
   ```

5. **Units Support with Automatic Scaling**
   
   ```python
   # Enable unit support with automatic scaling (NEW in 3.0+)
   with alive_bar(total, title='Downloading', unit='B', unit_scale=True) as bar:
       bar()  # Stats automatically show as KB/s, MB/s, GB/s
   
   # Custom units
   with alive_bar(total, title='Processing', unit='items', unit_scale=False) as bar:
       bar()  # Shows "items/s"
   
   # Precision control
   with alive_bar(total, unit='B', unit_scale=True, precision=2) as bar:
       bar()  # Shows 2 decimal places
   ```

6. **Global Configuration with config_handler**
   
   ```python
   from alive_progress import alive_bar, config_handler
   
   # Set global defaults - applies to all subsequent alive_bars
   config_handler.set_global(
       length=50,              # Bar length
       spinner='dots_waves',   # Default spinner
       bar='smooth',           # Default bar style
       theme='smooth',         # Or use a complete theme
       unknown='stars',        # Animation for unknown mode
       force_tty=True,         # Force in non-TTY environments (PyCharm, etc)
       calibrate=1000000,      # FPS calibration (higher = faster updates)
       dual_line=False,        # Enable dual-line mode globally
       enrich_print=True,      # Enrich print statements with position
       enrich_offset=0,        # Custom offset for enriched messages
       max_cols=80,            # Max columns for Jupyter
       file=sys.stderr,        # Use stderr instead of stdout
   )
   
   # Local options override global
   with alive_bar(total, bar='bubbles') as bar:  # Uses bubbles, not smooth
       pass
   ```

7. **Stats Display**
   
   - Stats are always visible by default
   - Show rate (items/sec) automatically
   - Show ETA with intelligent rounding for long tasks
   - Manual mode shows %/s if no total provided

### Visual Requirements

- **Title**: Clear, action-oriented (e.g., "Processing Images" not "Images")
- **Text Updates**: Update `.text` attribute to show current item/state
- **Stats**: Always visible, never disable
- **Length**: Use `length=50` or more for visual impact on modern terminals

### Advanced Patterns

1. **Manual Mode for Percentage Control**
   
   ```python
   # Send exact percentages
   with alive_bar(total, manual=True) as bar:
       for item in items:
           percentage = calculate_progress()
           bar(percentage)  # Send 0.0 to 1.0
           bar.text = f'Processing {item}'
   
   # Manual mode with total (gets count widget)
   with alive_bar(100, manual=True) as bar:
       bar(0.45)  # 45% complete
   ```

2. **PAUSE Mechanism - Unprecedented Feature**
   
   ```python
   # UNIQUE TO ALIVE-PROGRESS: Pause and return to prompt
   def process_with_pause(transactions):
       with alive_bar(len(transactions)) as bar:
           for transaction in transactions:
               if transaction.is_faulty():
                   # PAUSE BAR AND YIELD OBJECT
                   with bar.pause(): 
                       yield transaction  # Return to prompt with this object
               bar()
   
   # Usage in interactive session:
   gen = process_with_pause(transactions)
   transaction = next(gen, None)  # Bar pauses, you get the object
   # ... manually fix the transaction ...
   next(gen, None)  # Bar resumes seamlessly!
   ```

3. **alive_it Iterator Adapter**
   
   ```python
   from alive_progress import alive_it
   
   # Automatically calls bar() for you
   for item in alive_it(items, title='Processing'):
       process(item)
       # No need to call bar() manually!
   
   # With customization
   bar = alive_it(items, bar='bubbles', spinner='dots_waves')
   for item in bar:
       bar.text = f'Current: {item}'
       process(item)
   ```

4. **Check Tool for Designing Custom Animations**
   
   ```python
   from alive_progress.styles import check_bars, check_spinners
   
   # Check your custom spinner before using it
   check_spinners('my_spinner', ['⠋','⠙','⠹','⠸','⠼','⠴','⠦','⠧','⠇','⠏'])
   
   # Check custom bar
   check_bars('my_bar', ['▱','▰'])
   
   # See it alive with different verbosity levels
   check_spinners('my_spinner', frames, verbosity=2)
   ```

5. **Zero and Negative Increments**
   
   ```python
   # NEW: Support for rollback scenarios
   with alive_bar(total) as bar:
       for item in items:
           result = try_process(item)
           if result.success:
               bar(1)  # Advance by 1
           elif result.rollback_needed:
               bar(-1)  # Go backwards!
           else:
               bar(0)  # No progress this iteration
   ```

6. **Resuming Computations with Skipped Items**
   
   ```python
   # Track skipped items for accurate ETA
   with alive_bar(total, calibrate=100000) as bar:
       for item in items:
           if should_skip(item):
               bar.skip()  # Mark as skipped, improves ETA accuracy
           else:
               process(item)
               bar()
   ```

7. **Unknown Total Mode**
   
   ```python
   # When you don't know how many items
   with alive_bar(unknown='stars') as bar:  # Or 'horizontal', 'vertical', etc
       while condition:
           process_item()
           bar()  # Still shows count and throughput
   ```

8. **Print/Logging Enrichment**
   
   ```python
   # Prints are automatically enriched with position
   with alive_bar(total, enrich_print=True, enrich_offset=0) as bar:
       for i, item in enumerate(items):
           if i % 100 == 0:
               print(f'Checkpoint: {i}')  # Automatically shows "on 100: Checkpoint: 100"
           bar()
   ```

9. **Exploring Available Styles**
   
   ```python
   from alive_progress.styles import showtime, show_bars, show_spinners, show_themes
   
   # See everything (interactive, press Ctrl+C to continue)
   showtime()
   
   # Filter by pattern
   showtime(pattern='dot')  # Only shows styles matching 'dot'
   
   # Individual showcases
   show_bars()      # All bar styles
   show_spinners()  # All spinner styles  
   show_themes()    # All complete themes
   ```

## Hybrid Rich + alive-progress Patterns

For maximum impact, combine packages strategically:

```python
from rich.console import Console
from alive_progress import alive_bar

console = Console()

# Use alive-progress for main visual appeal
with alive_bar(len(files), bar='smooth', spinner='dots_waves', title='Processing Files') as bar:
    for file in files:
        bar.text = f'Current: {file.name}'

        # Use Rich for detailed sub-operation logging
        console.print(f"[cyan]Starting {file.name}...")
        result = process_file(file)

        if result.success:
            console.print(f"[green]✓ Completed {file.name}")
        else:
            console.print(f"[red]✗ Failed {file.name}: {result.error}")

        bar()
```

## Performance Considerations

1. **Update Frequency**
   
   - Update progress every 0.1-1% for large totals
   - Don't update more than 60 times per second (terminal refresh limit)
   - Batch progress updates when processing very fast operations

2. **Computation in Progress Contexts**
   
   - Keep progress update logic fast (<1ms)
   - Don't compute complex stats on every update
   - Cache expensive calculations

3. **Memory Management**
   
   - Remove completed tasks from Rich Progress objects
   - Don't accumulate log messages indefinitely

## Error Handling

Always handle interruptions gracefully:

```python
try:
    with progress:
        # work
except KeyboardInterrupt:
    progress.console.print("[yellow]Operation cancelled by user")
    # cleanup
except Exception as e:
    progress.console.print(f"[red]Fatal error: {e}")
    raise
```

## Accessibility and Compatibility

- Test in multiple terminal emulators (iTerm2, Terminal.app, VS Code terminal)
- Ensure progress bars don't break with narrow terminal widths
- Provide fallback for environments without color support (rare but possible)
- Never assume terminal height/width—use Rich's auto-detection

## The "Epic" Standard Checklist

A progress bar meets the epic standard when it has ALL of:

**Core Requirements:**

- ✅ Visual bar with color-coded completion state
- ✅ Animated spinner for active tasks (or reactive spinner that speeds up/slows down with throughput)
- ✅ Current item/operation clearly displayed
- ✅ Numeric progress (X of Y) or percentage
- ✅ Time elapsed
- ✅ Time remaining/ETA with intelligent rounding
- ✅ Processing rate (items/sec, MB/s, etc.) with automatic unit scaling
- ✅ Proper error handling and display
- ✅ Persistent logging for important events (using console.print or enriched print)
- ✅ Color coding for status (success/warning/error)
- ✅ Updates frequently enough to feel responsive (<0.5s between updates)
- ✅ Graceful handling of keyboard interrupts

**Advanced Features (Use When Appropriate):**

- ✅ Dual-line mode for lengthy status messages (alive-progress)
- ✅ Live display integration with panels/groups (Rich)
- ✅ Multiple concurrent progress bars for complex workflows
- ✅ Custom columns for domain-specific metrics
- ✅ Transient mode for clean terminal output (Rich)
- ✅ Pause/resume capability for interactive debugging (alive-progress)
- ✅ File operation integration with automatic progress (Rich)
- ✅ Unit support with automatic scaling (alive-progress 3.0+)
- ✅ Global configuration for consistent styling
- ✅ Hidden/visible task control
- ✅ Custom fields accessible in all columns (Rich)
- ✅ get_default_columns() for extending defaults (Rich)

Anything less than the core requirements is a missed opportunity.

## Anti-Patterns to Avoid

❌ Silent long-running operations
❌ Progress bars that don't actually progress smoothly
❌ Missing ETAs on operations >30 seconds
❌ Using print() inside progress contexts (breaks formatting)
❌ Overly verbose progress descriptions
❌ Invisible or low-contrast bars
❌ Progress bars that lie about completion time
❌ No indication of what specific item is being processed
❌ Progress bars for operations <2 seconds (just do the work)
❌ Cluttered displays with too many simultaneous progress bars (>5)

## Code Templates

### Rich: Epic Progress Template

```python
from rich.progress import (
    Progress,
    SpinnerColumn,
    BarColumn,
    TextColumn,
    TaskProgressColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
    MofNCompleteColumn,
    TransferSpeedColumn,
)
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.console import Group

console = Console()

def process_with_epic_progress(items):
    """Template for epic Rich progress implementation."""

    # Option 1: Simple progress with extended defaults
    progress = Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),  # Includes description, bar, percentage, time remaining
        TimeElapsedColumn(),
        TransferSpeedColumn(),  # Add if processing bytes
        console=console,
        transient=False,  # Set True to vanish on completion
        expand=False,  # Set True for full terminal width
    )

    # Option 2: Fully custom with all widgets
    progress_detailed = Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(complete_style="green", finished_style="bold green"),
        TaskProgressColumn(show_speed=True),
        MofNCompleteColumn(),
        TextColumn("•"),
        TimeElapsedColumn(),
        TextColumn("•"),
        TimeRemainingColumn(elapsed_when_finished=True),
        console=console,
    )

    with progress:
        task = progress.add_task("[cyan]Processing items", total=len(items))

        for i, item in enumerate(items, 1):
            try:
                # Update with custom fields
                progress.update(
                    task,
                    description=f"[cyan]Processing: {item.name}",
                    current_item=item.name,  # Custom field
                    phase="extraction"  # Another custom field
                )

                # Do work
                result = process_item(item)

                # Log success
                console.print(f"[green]✓[/green] {item.name}")

                # Advance progress
                progress.advance(task)

            except Exception as e:
                console.print(f"[red]✗ {item.name}: {e}[/red]")
                progress.advance(task)  # Still advance even on error

### Rich: Multi-Progress with Live Display
def complex_progress_with_live(main_tasks, sub_tasks):
    """Multiple progress bars with live display."""
    from rich.live import Live
    from rich.console import Group
    from rich.panel import Panel

    main_progress = Progress(...)
    sub_progress = Progress(transient=True, ...)

    progress_group = Group(
        Panel(main_progress, title="[bold cyan]Main Tasks"),
        Panel(sub_progress, title="[bold yellow]Subtasks"),
    )

    with Live(progress_group, refresh_per_second=4) as live:
        main_task = main_progress.add_task("Overall", total=len(main_tasks))

        for task in main_tasks:
            sub_task = sub_progress.add_task(f"Processing {task}", total=100)
            # Work...
            sub_progress.advance(sub_task)

        main_progress.advance(main_task)

### alive-progress: Maximum Visual Impact
from alive_progress import alive_bar, config_handler, alive_it

# Set global style
config_handler.set_global(
    length=60,
    bar='smooth',
    spinner='dots_waves',
    theme='smooth',  # Or any theme from show_themes()
    enrich_print=True,
    dual_line=False,  # Enable for long messages
)

def process_with_alive(items):
    """alive-progress with all features."""
    with alive_bar(
        len(items),
        title='Processing Items',
        dual_line=True,  # Put text below bar
        bar='smooth',
        spinner='dots_waves',
        unit='items',
        unit_scale=False,
    ) as bar:
        for item in items:
            bar.text = f'→ Current: {item.name}\nPhase: {item.phase}'
            process_item(item)
            bar()  # or bar(text='new text')

# With alive_it (automatic bar calls)
def process_with_alive_it(items):
    """Using alive_it iterator adapter."""
    items_bar = alive_it(items, title='Processing', bar='circles', spinner='radioactive')

    for item in items_bar:
        items_bar.text = f'Processing: {item.name}'
        process(item)
        # bar() called automatically!

# With pause for interactive debugging
def process_with_pause(transactions):
    """Unique pause/resume capability."""
    with alive_bar(len(transactions), dual_line=True) as bar:
        for transaction in transactions:
            if transaction.is_faulty():
                # Pause and yield to user for fixing
                with bar.pause():
                    yield transaction
            else:
                process_transaction(transaction)
            bar()

# Usage in interactive session:
# gen = process_with_pause(transactions)
# faulty = next(gen, None)  # Bar pauses
# fix_transaction(faulty)
# next(gen, None)  # Bar resumes!

# Manual mode with percentage control
def process_with_manual_control(complex_operation):
    """When you only have percentage information."""
    with alive_bar(manual=True, dual_line=True) as bar:
        for phase in phases:
            bar.text = f'Current phase: {phase.name}\nStatus: {phase.status}'
            percentage = complex_operation.get_percentage()
            bar(percentage)  # Send 0.0 to 1.0
```

## Implementation Workflow

1. **Start**: Choose package based on complexity
2. **Configure**: Set up all visual elements (bar style, spinner, columns)
3. **Integrate**: Add progress updates at appropriate intervals
4. **Enhance**: Add custom metrics and domain-specific columns
5. **Polish**: Add color coding and error handling
6. **Test**: Verify in your actual terminal with realistic data volumes
7. **Iterate**: Adjust update frequency and visual elements based on performance

Remember: A progress bar is a promise to the user that something is happening. Honor that promise with accurate, informative, and visually engaging feedback.
