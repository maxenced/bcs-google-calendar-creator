# BCS Calendar creator

## Getting started

Install [mise-en-place](https://mise.jdx.dev/) then run:
```bash
make install
```

Update tools:
```bash
make update
```

Update tooling configuration from [Copier](https://copier.readthedocs.io/en/stable/) template:
```bash
make update-tooling
```

## Usage

### Prerequisites

Before running the script, you need to:

1. **Set up Google Calendar API credentials:**
    - Go to the [Google Cloud Console](https://console.cloud.google.com/)
    - Create a new project or select an existing one
    - Enable the Google Calendar API
    - Create credentials (OAuth 2.0 Client ID) for a desktop application
    - Download the credentials file and save it as `credentials.json` in the project root directory

2. **Run from the project root directory:** The script expects to find `credentials.json` and the configuration files in the current working directory.

### Running the script

Run the script using Poetry from the project root directory:

```bash
poetry run bcs_calendar_creator
```

### Command line options

- `--debug`: Enable debug mode for verbose logging
- `--no-override`: Prevent overriding existing data. If set, overlapping events won't be deleted (default: false, meaning existing events will be overridden)
- `--target <category_key>`: Filter to only process one specific category instead of all categories
- `--prune <category_key>`: Prune all future events in one category (⚠️ **Note**: This feature is currently under development)

Examples:
```bash
# Run with debug logging
poetry run bcs_calendar_creator --debug

# Process only the "ateliers_level3" category
poetry run bcs_calendar_creator --target ateliers_level3

# Run without overriding existing events
poetry run bcs_calendar_creator --no-override

# Prune all future events from a specific category (under development)
poetry run bcs_calendar_creator --prune ateliers_level3

# Combine options
poetry run bcs_calendar_creator --debug --target cours_n1_mardi --no-override
```

### Configuration format

The script uses [`configuration.yaml`](src/bcs_calendar_creator/configuration.yaml) to define calendar events. The configuration file has the following structure:

```yaml
categories:
    category_name:
        calendar: "google_calendar_id@group.calendar.google.com"
        default:
            title: "Default event title"
            location: "Default location"
            duration: 60  # Duration in minutes
            start_time: "20h00"  # Format: HHhMM
            description: |
                Multi-line description
                with details about the event
        items:
            - start_day: "16/09/2025"  # Format: DD/MM/YYYY
            - start_day: "23/09/2025"
            title: "Override title for this specific event"
```

#### Categories

Each item in the `categories` dictionary is called a **category**. A category represents a group of related events (e.g., a weekly class, monthly workshops, etc.).

Each category must have:
    - `calendar`: The Google Calendar ID where events will be created
    - `items`: A list of events to create, each with at least a `start_day`

Each category can optionally have:
    - `default`: Default values that will be applied to all items in this category

#### Event properties

Each event (in `items` or `default`) can have:
    - `title`: Event title (string)
    - `location`: Event location (string)
    - `duration`: Event duration in minutes (integer)
    - `start_time`: Start time in "HHhMM" format (string)
    - `start_day`: Event date in "DD/MM/YYYY" format (string, required for items)
    - `description`: Event description, supports multi-line text (string)

Properties defined in individual items override the corresponding properties from `default`.

### Authentication

On first run, the script will:
    1. Open your web browser for Google OAuth authentication
    2. Create a `token.json` file to store your authentication tokens
    3. Use the stored tokens for subsequent runs

The `token.json` file will be automatically refreshed when needed.
