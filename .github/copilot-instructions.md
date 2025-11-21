# eeeMeter AI Coding Guidelines

## Project Overview
**eeeMeter** is a Python utility for fetching energy meter data from Shelly EM (Energy Meter) devices via their HTTP RPC API.

## Architecture & Data Flow
- **Primary Component**: `shellyrequest.py` - fetches energy meter status from Shelly devices using HTTP GET requests
- **Integration Point**: Shelly EM RPC API endpoint (`/rpc/em.GetStatus?id=0`)
- **Data Flow**: IP-configured Shelly device → HTTP request → JSON response → stdout

## Key Patterns & Conventions

### Device Configuration
- Shelly device IPs are hardcoded as string variables (e.g., `shelly1_ip`)
- Multiple IP references (commented or active) represent different physical locations
- Example: `#Gundelauer Str.` comments indicate installation location

### HTTP Requests to Shelly Devices
- Use `requests.get()` with the pattern: `http://{ip}/rpc/em.GetStatus?id=0`
- Always include `Content-Type: application/json` header
- Chain `.json()` to parse JSON responses directly
- Device channels/meters referenced via `id` query parameter

### Error Handling
- Bare `except:` clauses catch all Shelly API failures
- Friendly error messages printed to stdout (not logging)
- No network timeout configuration—add timeouts for robustness

## Common Workflows

### Adding a New Shelly Device
1. Define a new IP variable (e.g., `shelly2_ip = '192.168.x.x'`)
2. Create a new GET request following the existing pattern
3. Update error handling if capturing multiple devices

### Debugging API Issues
- Verify device IP is reachable: `curl http://{ip}/status` or similar
- Check RPC endpoint availability: `curl http://{ip}/rpc/em.GetStatus?id=0`
- Inspect raw JSON responses before parsing

## Technical Stack
- **Python**: 3.x (shebang: `#!/usr/bin/env python3`)
- **Dependencies**: `requests` library for HTTP
- **Execution**: Direct script invocation or import as module

## Important Notes
- Bug in line 9: f-string syntax missing (`{shelly1_ip}` should be `f'http://{shelly1_ip}/...'`)
- Bare except blocks should specify exception types for maintainability
- No configuration file or environment variable support yet—hardcoded IPs only
