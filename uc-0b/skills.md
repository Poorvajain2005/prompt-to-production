# UC-0B Summary That Changes Meaning — Skills

## Skills

### 1. Policy Loader

- **name**: `load_policy`
- **description**: Loads policy text from a file path.
- **input**: File path (str or Path)
- **output**: Raw policy text (str)
- **error_handling**: Raises FileNotFoundError if file missing; returns empty string for unreadable files.

### 2. Extract Critical Elements

- **name**: `extract_critical_elements`
- **description**: Extracts numbers, deadlines, and key obligations from policy text using regex.
- **input**: Policy text (str)
- **output**: Dict with keys: `numbers`, `deadlines`, `obligations`, `scope`
- **error_handling**: Empty input returns empty lists/dict.

### 3. Generate Summary

- **name**: `generate_summary`
- **description**: Builds a 2–5 sentence summary from policy text using section extraction.
- **input**: Policy text (str)
- **output**: Summary string
- **error_handling**: Empty input returns "Unable to summarise: empty policy."

### 4. Validate Summary

- **name**: `validate_summary`
- **description**: Checks if summary preserves policy meaning; flags omissions.
- **input**: Policy text (str), summary (str), critical_elements (dict)
- **output**: Dict with `valid`, `risky`, `omitted_critical` (list of omitted items)
- **error_handling**: Empty summary or policy returns `valid: false`, `risky: true`.

---

## Prompts (for AI-assisted refinement)

**Validation prompt**:
> Does this summary accurately reflect the policy? Check: scope, numeric limits, mandatory procedures. List any critical omissions.

---

## Validation Rules

| Rule | Check |
|------|-------|
| Summary length | 2–5 sentences |
| No fabrication | Summary contains only information from source |
| Critical numbers | At least one key numeric limit mentioned (e.g., days, amounts) |
| Risky flag | Set if any critical element is omitted |

---

## Critical Elements (examples)

- Numeric limits: 18 days, 12 days, 30 days, Rs 500, Rs 800, Rs 3500
- Mandatory procedures: "must submit", "requires approval", "within X days"
- Scope: "permanent employees", "Grade C and above"

---

## Example Inputs/Outputs

**Input**: Policy HR Leave (excerpt)
```
2.1 Each permanent employee is entitled to 18 days of paid annual leave...
2.3 Employees must submit a leave application at least 14 calendar days in advance...
```

**Output** (summary, valid, not risky):
```json
{
  "policy_name": "policy_hr_leave.txt",
  "summary": "Governs leave for permanent and contractual CMC employees. Annual leave: 18 days/year. Sick leave: 12 days/year. Applications must be submitted 14 days in advance. Maternity: 26 weeks for first two births.",
  "valid": true,
  "risky": false,
  "omitted_critical": []
}
```

**Output** (risky example — omits 14-day requirement):
```json
{
  "policy_name": "policy_hr_leave.txt",
  "summary": "Employees get annual and sick leave.",
  "valid": false,
  "risky": true,
  "omitted_critical": ["18 days annual leave", "14 days advance application", "12 days sick leave"]
}
```
