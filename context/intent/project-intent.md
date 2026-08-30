# Project Intent: HA Flow Map

## What

HA Flow Map is a Home Assistant add-on that helps people understand the relationships among their automations, scripts, scenes, events, and smart-home items through a Flow Map sidebar experience.

## Why

Home Assistant setups become difficult to safely change when a person cannot see what triggers, reads, or controls an item. The project makes these dependencies visible so operators can investigate behavior and assess the impact of changes.

## Current State

The project is an active, read-only integration distributed as a HACS custom repository. It gathers supported Home Assistant configuration relationships, presents searchable dependency maps, and provides impact information. It intentionally does not claim relationships that cannot be reliably determined from supported configuration sources.

## Current Features

- Relationship discovery
- Interactive dependency exploration
- Change-impact summaries
- Index refresh and availability feedback

## Status

- **Created**: 2026-08-30 (Phase: Intent)
- **Status**: Active
- **Note**: Generated from existing codebase analysis
