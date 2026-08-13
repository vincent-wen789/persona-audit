# Case Study — Persona Audit in Practice (anonymized)

> Anonymized post-mortems of two real audits, to show how the methodology lands in practice and what the output actually looks like. Product = a retail-facing market "readout" tool (a deterministic engine that ships one user-facing text push per day). Paths and product codenames have been anonymized.
>
> **Evidence limit:** these are retrospective summaries. The original reader transcripts, exact prompts, model/runtime metadata, and isolation details were not preserved, so the counts below cannot be independently reproduced. New runs should archive that provenance as required by `../references/engine-mode.md`.

## Background

The product pushes users a daily "market-state readout." The author (also the primary user) knows their own logic too well, and worried new users wouldn't get it — would miss things or be confused. After each of two major version ships, they ran a persona-audit.

## Round 1: stock readout tool, after shipping a new output layer

- Sample: 6-8 pieces, covering ordinary days / earnings days / a scan comparison table (three axes: render branch × edge-case data × surface reach)
- Retrospective notes record 4 reader angles run in parallel → **5 convergence candidates**
- Output: the roadmap for the next two versions
- Primary user's subjective take: "high quality, very real" (note: the primary user = the author themselves; this is a single-person self-assessment, weak evidence grade, take with a grain of salt)

## Round 2: crypto readout tool

- Sample covered ordinary days + full-glow demo mode + major/edge assets (including a meme token with a 1000× "1000" prefix) + a scan comparison table + the push surface that reaches users directly
- **26-item consensus matrix (= candidate list)**, two of them critical:
  - **1000× price mismatch**: an edge asset (the "1000"-prefix meme coin) showed a price off by a factor of 1000 — multiple personas spotted "this price is wrong" at a glance (honest caveat: an order-of-magnitude howler like this could also be caught by a range assertion or a human eyeballing it; it doesn't strictly require this method)
  - **Cross-persona semantic mismatch**: several personas all misread one field as the same wrong meaning. ⚠️ caveat: the personas share the same base model, so "consistent misreading" could be a structural howler — or it could just be "this is how the model reads this passage." Treat it as a **candidate to verify early**, not a proven conclusion
- Same day, **13 fixes shipped** (26 candidates → 13 adopted, roughly half; the other half were low-vote noise or not worth changing. **The ~50% adoption rate itself shows the matrix is a candidate generator that needs a human to filter — not a verified defect list**)

## Post-mortem: why it works

1. **Cognitive gradient**: the novice hits jargon and panic points, the veteran hits terminology and false precision, the mirror hits use cases, the target user of the new feature interrogates the new layer line by line — four kinds of blind spot covered in one pass.
2. **Convergence = attention, not priority**: a semantic mismatch seen across angles deserves an earlier look than a one-angle preference, but ABCD triage and owner judgment still decide what to change.
3. **Cold-read discipline**: reader angles may only read the sample, never the code, which makes first-contact misreadings easier to surface than another author-framed review.
4. **Asset confirmation**: the veteran persona also lists a "do not cut" set, so the next version doesn't casually "optimize away" a design users actually love.

## In one line

Use four fixed reader angles to cold-read the output; cross-angle convergence creates candidates worth verifying earlier. Isolated contexts may report N/4 as a convergence label, while a single-pass simulation should name angles without vote counts. The output is **candidates to verify**, not proven defects, and this retrospective is not a controlled benchmark.
