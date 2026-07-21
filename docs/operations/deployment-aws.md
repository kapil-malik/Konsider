# AWS deployment design

Status: selected initial design; no AWS infrastructure is implemented

## Baseline topology

```text
EventBridge Scheduler -> Lambda worker -> private S3 raw/release bucket
                                              |
                                              v
                                      active.json + releases

Browser -> CloudFront -> S3 static React application
   |
   +-> API Gateway -> FastAPI Lambda -> S3 active release/catalog
```

S3 plus CloudFront is the baseline UI host. Amplify Hosting is an optional convenience alternative,
not the architectural requirement. FastAPI needs an appropriate ASGI-to-Lambda adapter when this
design is implemented.

## Component mapping

| Local concern | Initial AWS component |
| --- | --- |
| Scheduled refresh | EventBridge Scheduler invoking a worker Lambda |
| Raw third-party bytes | Private, encrypted, versioned S3 prefix |
| Releases, catalogs, manifests, active pointer | Encrypted, versioned S3 objects |
| Static React build | S3 origin behind CloudFront |
| FastAPI | API Gateway plus Lambda |
| Logs and metrics | CloudWatch |
| Secrets, if future sources require them | Secrets Manager |

The worker uploads a complete candidate under a new immutable prefix, validates it, and replaces the
small active-pointer object only after publication succeeds. The API Lambda loads and validates the
active release on cold start and reuses it for warm invocations. Pointer changes therefore reach new
cold starts automatically; deliberate rollback may also require invalidating or recycling warm
instances depending on the implemented cache policy.

## Security and operations

- Give the worker write access to raw, release, and pointer prefixes. Give the API read-only access
  to release, catalog, manifest, and pointer objects. The UI bucket must never expose raw artifacts.
- Enable S3 versioning, default encryption, TLS-only bucket policies, blocked public access, and
  lifecycle rules that preserve required audit data.
- Keep credentials out of source registrations and browser variables. Use Secrets Manager only when
  a registered source actually requires a secret.
- Use structured CloudWatch logs for worker runs, publication results, API initialization failures,
  release IDs, and request IDs without logging private filesystem paths or source credentials.
- Restrict API Gateway CORS to deployed UI origins. CloudFront should use secure origin access for
  the UI bucket.
- Roll back by validating a prior compatible immutable release and changing only the versioned
  active pointer. Never edit release objects.

## Cost and scale assumptions

The initial design assumes small releases, periodic rather than continuous refresh, low request
volume, and an API snapshot that fits comfortably in Lambda memory. S3, Lambda, API Gateway, and
CloudFront keep idle cost low and match the immutable workload.

## Escalation criteria

- Move the worker from Lambda to ECS Fargate when downloads or parsing exceed Lambda duration,
  memory, temporary-storage, networking, or package-size limits.
- Move the API from Lambda to App Runner or ECS when measured cold starts, streaming, long-lived
  requests, persistent caches, or release sizes make a container service preferable.
- Move loaded metrics from S3 to DynamoDB or SQL only when release size or query patterns no longer
  suit complete snapshot loading. Preserve immutable release identity and lineage.
- Introduce DynamoDB for profiles, sessions, quotas, conversations, or run state only after those
  mutable features exist.
- Introduce vector retrieval only after evidence volume and measured lexical/metadata search quality
  justify it. Embeddings remain derived and rebuildable.

Infrastructure-as-code, deployment pipelines, alarms, budgets, domains, certificates, and runbooks
remain intentionally deferred until AWS implementation begins.
