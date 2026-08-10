# Mission Domain Assessment

## Target Architecture

Mission is the unified Runtime intake. Every human interaction begins as a Conversation; API, MCP, scheduler, webhook, and automation converge to the same Mission-intake model. MSM remains the business-state authority.

## Current Repository

`projects/models.py:FactoryMission` is a durable human-facing mission tied one-to-one to `FactoryChatSession`; `projects/factory_missions.py` manages its readiness and phases. `projects/factory_chat.py` is the principal authenticated human boundary. `projects/mcp.py` and `projects/governed_mcp.py` expose integration entry points, but they do not use a shared Mission intake abstraction.

## Gap Analysis

**Partial:** durable Mission and a state lifecycle exist. **Missing:** provider-neutral Mission identity, source type, intake command, and common entry contract. **Legacy/adapter:** Factory Chat session is both Conversation transport and Mission parent, making non-human convergence indirect.

## Migration Strategy

Add a constitutional Mission Intake facade and map Factory Chat into it first. Adapt MCP/API/scheduled sources incrementally. Keep FactoryMission as a compatibility projection until lifecycle authority has one canonical mapping; expected API schema additions, not an immediate breaking change.

## Risks and Dependencies

Technical: dual Mission state can drift. Architectural: MSM versus ORKI lifecycle ownership. Business: existing Factory flows must remain explainable. Depends on AC-02 and identity/scope propagation.

## Readiness

**Ready.** The durable Mission foundation and acceptance tests are present; the migration is principally an adapter and authority-boundary exercise.

## Evidence

`projects/models.py` (`FactoryChatSession`, `FactoryMission`); `projects/factory_missions.py`; `projects/factory_chat.py`; `projects/governed_mcp.py`; `projects/mcp.py`.
