# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.1/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.3] - 2026-04-27

### Changed

- Synchronised the project with the latest cruft template.
- Updated dependencies.

### Fixed

- Corrected README copy and contributing rule links.
- Ended exception messages with full stops.
- Resolved Ruff docstring and assert rule violations.
- Resolved a test warning by tidying the asynchronous mock in `test_git_error`.
- Resolved type-checking issues in the plist helpers and defaults export.

### Removed

- AppImage GitHub Actions workflow.

## [0.4.2]

### Added

- Attestation.

## [0.4.1]

### Fixed

- Disabled colours in launchd job.

## [0.4.0]

### Added

- Configuration file support.

### Changed

- Rewrote algorithm for filtering out domains and keys.

[unreleased]: https://github.com/Tatsh/macprefs/compare/v0.4.3...HEAD
[0.4.3]: https://github.com/Tatsh/macprefs/compare/v0.4.2...v0.4.3
[0.4.2]: https://github.com/Tatsh/macprefs/compare/v0.4.1...v0.4.2
[0.4.1]: https://github.com/Tatsh/macprefs/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/Tatsh/macprefs/compare/v0.3.4...v0.4.0
