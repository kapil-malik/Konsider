# Data Refresh Worker Application

This directory is the deployment root for scheduled and manually triggered data refresh jobs. It
will compose source connectors, normalization and validation services, and storage adapters.

No worker runtime is implemented in the architecture-alignment change. See
`docs/components/data-refresh-worker.md` and `docs/roadmap.md`.
