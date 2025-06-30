# config

This folder contains configuration modules for the application, such as database, broker, and logger settings.

## Purpose

- Centralizes all configuration logic and environment variable management.
- Provides reusable configuration objects for other modules.

## How to add a new configuration component

1. Create a new Python file (e.g., `my_service.py`).
2. Define your configuration class or function, following the pattern in `settings.py` or other files.
3. Import and use your configuration in the relevant part of the application.

**Example:**

- To add configuration for a new cache service, create `cache.py` and define your settings class or function.
