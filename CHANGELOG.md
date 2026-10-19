# Changelog

All user-relevant changes are documented in this file.

## [2026.10.1] - 2026-10-19

### Changed

- Restricted the Flow Map sidebar panel to Home Assistant administrators.
- Improved panel loading, empty, and error states, including accessible labels
  and disabled controls during rebuilds and data loads.
- Restored the index summary after relationship and focused-flow loads finish.
- Completed the light and dark branding asset set required by Home Assistant
  and HACS, including matching high-density variants.

## [2026.8.0] - 2026-08-25

### Added

- Initial HACS-ready release of HA Flow Map.
- Read-only mapping of explicit relationships in Home Assistant automations,
  scripts and scenes.
- Flow Map panel with graph search, bounded relationship expansion and
  administrator-triggered rebuilds.
- Recursive parsing for conditions, branches, parallel sequences, repeats,
  waits, service calls, events and scene targets.
- GitHub Actions validation for Python and frontend tests, HACS, Hassfest and
  SonarQube.
