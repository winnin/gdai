# Changelog

All notable changes to this project will be documented in this file.

The format follows the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.

## [Unreleased]

### Added

- Support for multiple tenants.
- Integration with PGVector and RabbitMQ via Docker Compose.
- RESTful API for document upload and semantic search.
- Asynchronous processing with Dramatiq.
- Initial documentation with MkDocs.

### Fixed

- Fixed handling of large files in the document extractor.

### Changed

- Updated CI workflow to run pre-commit before tests.

## [0.1.0] - 2024-06-10

### Added

- First stable release of GDAI.
- Document upload and indexing.
- Basic semantic search.
