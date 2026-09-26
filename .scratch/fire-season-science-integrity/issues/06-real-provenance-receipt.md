# Record verifiable source provenance

Status: ready-for-agent

## Goal

Replace placeholder checksums and fixture identifiers with verified file hashes and honest provenance for each decoded provider object.

## Acceptance criteria

- Each granule used has a provider ID, observed interval, byte size, SHA-256, and public catalog/archive link.
- Unknown download timestamps are recorded as unknown, not fabricated.
- Release payload hashes match the manifest.

## Comments

- Implemented using content hashes; source retrieval time is explicitly unknown because the archive does not preserve it.
