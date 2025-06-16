# Contributing to G-DAI

We welcome contributions from the community! Please follow these guidelines to help us maintain a high-quality project.

## Getting Started

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/g-dai.git
   cd g-dai
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   Or use Docker Compose:
   ```bash
   docker-compose up --build
   ```

### Usage
- Run the API:
  ```bash
  python -m src.api.main
  ```
- Ingest documents by placing them in `DOC_FOLDER/raw/` and using the provided scripts or API endpoints.
- Query the API for semantic search and auditable answers.

## How to Contribute
- Fork the repository and create your branch from `main`.
- Write clear, concise commit messages.
- Ensure your code passes linting and tests.
- Submit a pull request with a detailed description of your changes.

## Coding Standards
- Follow PEP8 and use Ruff for linting/formatting.
- Write tests for new features and bug fixes.
- Document your code and public APIs.

## Reporting Issues
- Use GitHub Issues to report bugs or request features.
- Provide as much detail as possible, including steps to reproduce and expected behavior.

## Community
- Be respectful and follow our [Code of Conduct](code_of_conduct.md).
