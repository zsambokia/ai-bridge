---
diagram: 99 Full Architecture
architecture_status: CANONICAL
constitution_book_entries: Articles III, IV, VIII
source: Mermaid
derived_drawio: Full Architecture.drawio
constitution: Article V — Architecture Documentation Governance
last_reviewed: 2026-08-14
architecture_version: 1.1.0
related_adrs: ADR-034, ADR-038 (open)
owner: Architecture
---

# Diagram 99 — Full Architecture

## Canonical logical architecture

```mermaid
flowchart TB
    PO[Product Owner] --> FC[Factory Chat]

    subgraph CL[Conversation Layer]
        FC --> CONV[Conversation]
        CONV --> CSE[Conversation State Engine]
        CONV --> CA[Context Assembly<br/>stateless]
        CA --> U[Understanding<br/>stateless; immutable result]
        U --> E[Evaluation<br/>stateless; immutable result]
        E --> CSE
        CSE --> MR[Mission Resolution]
    end

    subgraph KR[Knowledge and Repository]
        REP[Repository]
        AKB[Architecture Knowledge Base]
        SEM[Semantic Layer]
        CP[Context Package<br/>immutable; versioned; reproducible]
        REP --> CA
        AKB --> CA
        SEM --> CA
        CA --> CP
    end

    CP -. immutable processing input .-> U

    subgraph FIP[FactoryIP foundation — semantic boundary communication]
        L0[L0 Effective Scope / isolation] --> L1[L1 Evidence references]
        L1 --> L2[L2 Provenance / causality]
        L2 --> L3[L3 Artifact / Knowledge Candidate]
        L3 --> L4[L4 Factory Packet transport]
        FFS[FFS: name/service resolution] -. control plane only .-> L4
        Z[Zoning: transport permission] -. permits boundary traffic .-> L4
    end

    subgraph RB[Runtime Boundary]
        MISSION[Mission]
        MSM[Mission State Machine]
        OWI[Operational Work Item<br/>immutable]
        MISSION --> MSM --> OWI
    end

    MR --> MISSION
    ADAPTERS[API / MCP / Scheduler / Webhook / Automation] --> MISSION

    subgraph OF[Operational Foundation]
        ADM[Admission]
        CR[Capability Resolution]
        CAPREG[Capability Registry]
        ENGREG[Engine Definition Registry]
        SCH[Scheduler]
        QUEUE[Queue]
        LEASE[Lease Manager]
        RETRY[Retry]
        REC[Recovery]
        HEALTH[Health Monitor]
        TEL[Telemetry]
        CFG[Configuration]
        ADM --> CR --> CAPREG --> ENGREG --> SCH --> QUEUE --> LEASE
        CFG -. policy .-> ADM
        QUEUE -. governed by .-> RETRY
        QUEUE -. governed by .-> REC
        QUEUE -. observed by .-> HEALTH
        QUEUE -. observed by .-> TEL
    end

    OWI --> ADM

    subgraph OE[Operational Engines — stateless capability definitions]
        PLAN[Planning Engine]
        WF[Workflow Engine]
        KNOW[Knowledge Engine]
        REPO[Repository Engine]
        REFL[Reflection Engine]
        DOC[Documentation Engine]
        DEP[Deployment Engine]
        LEARN[Learning Engine]
    end

    ENGREG --> PLAN
    ENGREG --> WF
    ENGREG --> KNOW
    ENGREG --> REPO
    ENGREG --> REFL
    ENGREG --> DOC
    ENGREG --> DEP
    ENGREG --> LEARN

    subgraph KERNEL[AI Kernel]
        ER[Execution Request]
        EXEC[Execution<br/>Kernel-owned]
        PIN[Provider Integration]
        PRES[Provider Resolver]
        PROV[Provider<br/>stateless capability provider]
        PEXE[Provider Executor<br/>stateful runtime instance]
        ER --> EXEC --> PIN --> PRES --> PROV --> PEXE
    end

    PLAN --> ER
    WF --> ER
    KNOW --> ER
    REPO --> ER
    REFL --> ER
    DOC --> ER
    DEP --> ER
    LEARN --> ER
    CP -. immutable context reference .-> EXEC

    subgraph HIST[Historical / Transitional implementation vocabulary]
        ERUN[ExecutionRun]
        EJOB[ExecutionJob]
        PGW[Provider Gateway]
    end
    ERUN -. historical only .-> EXEC
    EJOB -. disposition by ADR .-> ER
    PGW -. implementation adapter only .-> PIN

    classDef canonical fill:#d5f5e3,stroke:#1e8449,color:#000;
    classDef transitional fill:#fcf3cf,stroke:#b7950b,color:#000;
    classDef historical fill:#f2f3f4,stroke:#7f8c8d,color:#000;
    class PO,FC,CONV,CSE,CA,U,E,MR,REP,AKB,SEM,CP,L0,L1,L2,L3,L4,FFS,Z,MISSION,MSM,OWI,ADM,CR,CAPREG,ENGREG,SCH,QUEUE,LEASE,RETRY,REC,HEALTH,TEL,CFG,PLAN,WF,KNOW,REPO,REFL,DOC,DEP,LEARN,ER,EXEC,PIN,PRES,PROV,PEXE canonical;
    class ERUN,EJOB,PGW historical;
```

## Reading rules

- `Mission` is the common Runtime intake. Conversation is mandatory only for
  human interaction; non-human adapters converge directly on Mission intake.
- Factory Chat is a UI/interaction boundary. Conversation remains a durable
  domain object; stateless Context Assembly, Understanding and Evaluation only
  produce immutable processing inputs/results. CSE is the Conversation state
  authority and is the only depicted Conversation route to Mission Resolution.
- FactoryIP is the L0–L4 semantic communication foundation. L0 eligibility
  precedes semantic retrieval; FFS is control-plane resolution, zoning is
  transport permission, and Factory Packet transport is distinct from delivery,
  interaction and payload semantics.
- The Runtime consumes completed immutable Context Packages and does not
  directly query AKB or the Repository.
- Operational Foundation resolves a required capability through the Capability
  Registry and Engine Definition Registry. Engines are stateless definitions;
  an engine requests Kernel-owned Execution rather than owning it.
- Provider routing is `Execution → Provider Integration → Provider Resolver →
  Provider → Provider Executor`.
- `ExecutionRun`, `ExecutionJob`, and `Provider Gateway` are historical or
  transitional implementation terms. Their disposition remains ADR-governed
  and they are not canonical target objects.

## Derived visual artifact

[`Full Architecture.drawio`](Full%20Architecture.drawio) is a derived, editable
visualization of this Mermaid model. It may add educational layout and labels,
but it must not alter the components, ownership, or relationships above.
