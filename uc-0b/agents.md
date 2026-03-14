# UC-0B Summary That Changes Meaning — Agent Definition

## Role

A **Policy Summary Agent** that loads policy text files, generates short summaries, and validates that each summary preserves the original policy meaning. The agent highlights any summaries that are risky (i.e., that could change interpretation or omit critical obligations). It operates within the boundary of the provided policy documents only — no external APIs.

## Intent

A correct output is:

- **Summary** for each policy: concise (2–5 sentences) capturing core obligations and scope
- **Meaning preservation check**: Whether the summary accurately reflects the policy (pass/fail)
- **Risky summaries flagged**: Any summary that omits critical terms, numbers, deadlines, or obligations is marked as risky
- **Structured output**: JSON or formatted text with policy name, summary, validation result, and risk flags

## Context

The agent may use:

- Policy text files from `data/policy-documents/` (or user-specified path)
- Rule-based extraction: section titles, numbers, deadlines, mandatory terms
- Only standard library: `pathlib`, `re`, `json` — no external summarisation APIs

Exclusions:

- No external LLM or summarisation API calls
- Summaries are produced by rule-based extraction (key sections, numbers, obligations)

## Task Flow

1. **Load** — Read policy files from the policy-documents directory
2. **Extract** — Identify key sections, numbers, deadlines, and obligations
3. **Summarise** — Build a short summary from extracted content
4. **Validate** — Check that critical terms/numbers are present in the summary
5. **Flag** — Mark summaries that omit critical content as risky
6. **Output** — Print results and optionally write to file

## Reasoning Approach

- **Critical elements**: Policy numbers, effective dates, numeric limits (e.g., 18 days leave, 30 days claim), mandatory procedures
- **Validation**: Summary must mention at least: scope, key entitlement/obligation, and any numeric limit
- **Risky**: Summary is risky if it omits a critical numeric limit or changes a mandatory requirement to optional (or vice versa)
- **Transparency**: Explain what was omitted if a summary is flagged as risky

## Enforcement Rules

- Summary must be 2–5 sentences
- Summary must not introduce information not in the source policy
- If policy cannot be parsed (empty, binary), output error and skip
- Every output must include: `policy_name`, `summary`, `valid`, `risky`, `omitted_critical` (if risky)
