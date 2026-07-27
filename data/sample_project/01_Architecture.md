# Project AetherFleet Architecture Specification

## System Overview
AetherFleet is an autonomous drone fleet management platform built with Python 3.11 and FastAPI.

## Database Selection
We selected PostgreSQL 16 as our relational data store for ACID compliance on flight mission locks.
For real-time spatial caching of drone telemetry coordinates, we use Redis 7.

## Telemetry Ingestion SLA
The TelemetryIngest service processes up to 10,000 packets per second with under 15ms p99 latency.
