# background_tasks

This folder contains background task modules for asynchronous and long-running operations.

## Purpose

- Handles tasks that should run outside the main request/response cycle (e.g., document extraction, embedding generation).
- Improves API responsiveness by offloading heavy operations.

## How to add a new background task

1. Create a new Python file for your task (e.g., `my_task.py`).
2. Implement your task logic, following the structure of existing tasks.
3. Register and trigger your task from the appropriate service or API endpoint.

**Example:**

- To add a new background task for data cleanup, create `data_cleanup.py` and define your async task function.
