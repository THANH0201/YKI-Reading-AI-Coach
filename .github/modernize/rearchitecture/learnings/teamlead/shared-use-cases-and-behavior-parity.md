# Shared Use Cases and Behavior Parity

For a multi-transport brownfield rewrite, treat existing observable behavior as the acceptance baseline and make REST/MCP thin adapters over shared application use cases.

## What Happened

For YKI Reading AI Coach task `t1`, the user fixed a target architecture with Streamlit, FastAPI, and MCP Streamable HTTP while requiring existing user behavior to remain intact. The governance baseline makes host boundaries explicit and requires parity evidence before removing old paths. It also distinguishes deliberately disabled identity/billing seams from real capabilities.

## Takeaway

When planning multiple transports, define shared application use cases as the sole business entrypoints, version transport contracts separately, and test adapter behavior against the same behavior contract. Preserve user data and consent independently of transport migration. Mark extensions as disabled rather than stubbing them as working features.

## History

- 2026-11-08 (`YKI Reading AI Coach/t1`): initial
