# Bank in a Box — Product & Technical Spec

Single source of truth for every agent. If code and spec disagree, the spec wins until an ADR changes it.

## 1. Goal
A small, complete bank: create an account, deposit, withdraw, view history. Backend in **Dropwizard**, frontend in **React**, shipped as **one container image plus a database** via `docker compose up`.

The app is deliberately simple. The point is that it is built end to end by a team of agents from issues, then secured and released with GitHub's platform.

## 2. Stack (initial decisions; ADR-001 may refine versions only)
| Concern | Choice |
|---|---|
| Language / runtime | Java 21 |
| Framework | Dropwizard (latest stable) — Jersey, Jackson, Jetty, Hibernate Validator |
| Data access | JDBI 3 (`dropwizard-jdbi3`), plain SQL |
| Database | PostgreSQL 16 |
| Migrations | Flyway, run at startup |
| Build | Maven, single module, shaded JAR |
| Tests | JUnit 5, AssertJ, Mockito, Dropwizard testing, Testcontainers |
| Frontend | React 18, Vite, Tailwind, Axios, @tanstack/react-query, Vitest + Testing Library |
| Packaging | Multi-stage Dockerfile; Dropwizard serves the built React app |

## 3. Repository layout (target)
```
.
├── pom.xml
├── src/main/java/com/example/bank/
│   ├── BankApplication.java        # Application, bundles, wiring
│   ├── BankConfiguration.java      # YAML config (db, cors, env overrides)
│   ├── api/                        # Request/response DTOs (records)
│   ├── core/                       # Account, Transaction, Money, TransactionType
│   ├── db/                         # JDBI DAOs, SQL objects
│   ├── resources/                  # AccountResource, TransactionResource, HealthResource
│   ├── service/                    # AccountService, LedgerService (transaction boundaries)
│   └── errors/                     # ApiError, exception mappers
├── src/main/resources/
│   ├── config.yml
│   └── db/migration/V1__init.sql
├── src/test/java/...
├── frontend/                       # Vite app (see §7)
├── Dockerfile
├── docker-compose.yml
└── specs/ docs/ .github/
```

## 4. Domain model
- `Account { id: UUID, name, email, balance (Money), createdAt }`
- `Transaction { id: UUID, accountId, type: DEPOSIT|WITHDRAWAL|TRANSFER_IN|TRANSFER_OUT, amount (Money), note, createdAt }`
- **Money** is a value type holding `long cents`. Never `double`/`float` anywhere in Java or SQL.
- API represents amounts as JSON numbers with at most 2 decimal places, parsed via `BigDecimal`, converted to cents at the edge. Reject 3+ decimals with `VALIDATION_ERROR`.

## 5. API
All responses are JSON. Base path `/api`.

| Method | Path | Body / Query | Success | Description |
|---|---|---|---|---|
| POST | `/api/accounts` | `name`, `email`, `initial_deposit?` | 201 | Create account |
| GET | `/api/accounts/{id}` | — | 200 | Account + balance |
| GET | `/api/accounts/{id}/transactions` | `?page=1&limit=20` | 200 | Paginated history, newest first |
| POST | `/api/accounts/{id}/deposit` | `amount`, `note?` | 201 | Deposit |
| POST | `/api/accounts/{id}/withdraw` | `amount`, `note?` | 201 | Withdraw |
| GET | `/api/health` | — | 200 | App + DB health |
| POST | `/api/accounts/{id}/transfer` | `to_account_id`, `amount`, `note?` | 201 | **Stretch** |

Dropwizard admin port (8081) also exposes `/healthcheck`; the DB health check must be registered there.

### Error contract
Every error: `{"error": "human message", "code": "ERROR_CODE"}`

| Situation | HTTP | code |
|---|---|---|
| Bad/missing field, amount ≤ 0, >2 decimals | 400 | `VALIDATION_ERROR` |
| Account not found | 404 | `ACCOUNT_NOT_FOUND` |
| Duplicate email | 409 | `EMAIL_ALREADY_EXISTS` |
| Withdraw > balance | 422 | `INSUFFICIENT_FUNDS` |
| Unhandled | 500 | `INTERNAL_ERROR` (no stack trace in body) |

## 6. Business rules
1. Amount must be > 0 on every transaction (validated server-side and client-side).
2. Withdrawals are rejected if balance < amount.
3. Email is unique, case-insensitive (unique index on `lower(email)`).
4. Balance changes and the matching transaction row are written in **one database transaction**.
5. Concurrent withdrawals must never overdraw: use a conditional `UPDATE ... WHERE balance >= :amount` or `SELECT ... FOR UPDATE`. An integration test must prove it with parallel requests.
6. An `initial_deposit` greater than 0 creates the account and a DEPOSIT transaction atomically.
7. Balance equals the sum of the account's transactions. A test must assert this invariant.

## 7. Frontend
Pages: **Home** (search by account ID or create), **Account Dashboard**, **Create Account modal**.

Dashboard: large "vault" balance, deposit and withdraw forms side by side, scrollable history with type icons and timestamps. Single column on mobile, two columns on desktop.

UX requirements:
- Optimistic UI with a pending state for deposit/withdraw; roll back on error.
- Invalidate and refetch balance and history after every mutation.
- Client validation before any call; backend `error` shown inline.
- Empty history: "No transactions yet — make your first deposit".
- Components under ~150 lines each.

### Design system — "vault modernism"
| Token | Value |
|---|---|
| Background | `#0F1117` |
| Surface | `#1A1D27` |
| Border | `#2A2D3E` |
| Accent | `#4F8EF7` |
| Success | `#34D399` |
| Danger | `#F87171` |
| Text / muted | `#E8EAF0` / `#8B8FA8` |

Type: Inter (700/800 for balances, 400/500 for UI); JetBrains Mono for account IDs and amounts. Signature element: large tabular-numeric balance with a subtle animated gradient shimmer on load.

## 8. Serving & container
- Dropwizard serves the compiled React app at `/` and the API under `/api`; unknown non-API paths fall back to `index.html`.
- Dev: Vite on 5173 proxies `/api` to 8080. CORS allows `http://localhost:5173` only when `ENV != production`.
- Dockerfile, 3 stages: `node:20-alpine` (frontend build) → `maven:3-eclipse-temurin-21` (package, copy dist into `target/classes/assets` or equivalent) → slim JRE 21 runtime, non-root user, `EXPOSE 8080`.
- `docker-compose.yml`: `app` + `postgres:16-alpine` with a named volume; app healthcheck on `/api/health`; `docker compose down && up` preserves data.
- **Size target:** app image under 250 MB (the original Go spec's 50 MB is not realistic for a JVM; a jlink runtime is an optional stretch).

## 9. Configuration (env overrides)
| Variable | Default | Purpose |
|---|---|---|
| `PORT` | 8080 | Application port |
| `ADMIN_PORT` | 8081 | Dropwizard admin port |
| `DB_URL` | `jdbc:postgresql://localhost:5432/bank` | JDBC URL |
| `DB_USER` / `DB_PASSWORD` | `bank` / `bank` (dev only) | Credentials; never committed for non-dev |
| `ENV` | `development` | `production` disables dev CORS |

## 10. Definition of done (every issue)
- Acceptance criteria in the issue are met and checked off in the PR.
- `mvn verify` (and `npm test` where relevant) pass in CI.
- No new CodeQL, dependency-review, or secret-scanning findings.
- Docs touched if behaviour or config changed.
- PR description links the issue with `Closes #N`.
