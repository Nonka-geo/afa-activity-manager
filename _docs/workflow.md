# Issue Workflow for AFA Activity Manager

This document defines the required development workflow for each GitHub issue in this repository. The goal is to keep the MVP small, reliable, and issue-scoped while preserving the required project rules around privacy, centralized status calculation, and historical tracking.

## 1. Roles and responsibilities

### PM
The PM role is responsible for issue readiness and scope control.

PM responsibilities:
- read the GitHub issue and the relevant project docs
- confirm the issue is aligned with the project purpose and MVP scope
- check that the Goal, Acceptance criteria, Out of scope, and Constraints are clear
- refine or clarify the issue if required before work begins
- confirm the issue does not expand into post-MVP work
- do not implement code

PM output:
- a clear issue with explicit scope and acceptance standards
- a decision to proceed, refine, or defer

### Engineer
The Engineer role is responsible for implementing the selected issue only.

Engineer responsibilities:
- read the issue and relevant project docs before making changes
- implement only the selected issue
- keep changes minimal and directly tied to the issue
- update or add tests covering the behavior being changed
- run the relevant tests before handing the work off
- do not expand scope into adjacent features
- do not mix this issue with unrelated cleanup or post-MVP development

Engineer output:
- code changes tied to one issue
- updated tests
- evidence from the relevant test run

### QA
The QA role is responsible for independent verification.

QA responsibilities:
- independently review the implementation against the issue acceptance criteria
- run relevant tests and validation commands
- check permissions, business rules, and regressions
- verify the implementation matches the issue statement and project constraints
- return PASS or FAIL
- if FAIL, provide concrete defect descriptions and evidence
- do not fix the implementation

QA output:
- PASS or FAIL result
- defects and evidence if FAIL

---

## 2. Required loop: PM → Engineer → QA

Every issue follows the same loop:

1. PM reviews the issue and project context.
2. Engineer implements only the selected issue.
3. QA independently checks the result against the issue acceptance criteria.
4. If QA passes, the issue may be considered complete.
5. If QA fails, the issue is returned to the Engineer for correction and then QA re-checks it.

The loop is:

PM → Engineer → QA

If QA = FAIL:
QA → Engineer → QA

If QA = PASS:
issue can be considered complete.

---

## 3. Required evidence before PASS

An issue may not be marked complete without fresh evidence.

Before PASS, the implementation must show all of the following:
- the issue was read and understood
- the relevant implementation work was completed
- the relevant tests were run and the output reviewed
- the acceptance criteria were checked against the actual behavior
- permission or access rules were verified when relevant
- business rules such as deterministic status calculation and historical snapshot behavior were checked
- the code remains within the issue scope and does not include unrelated work

Minimum evidence required for PASS:
- a clear test run output showing the relevant test set passes
- a QA checklist linked to the issue acceptance criteria
- a final QA result of PASS

No issue should be closed based on confidence alone; it must have run verification.

---

## 4. Rules for test execution

Tests are mandatory for all issue work that affects product behavior.

Required rules:
- run the smallest relevant test set for the issue
- prefer focused tests over broad suites when the issue is narrow
- include new or updated tests when the issue changes behavior
- run tests after implementation before handoff to QA
- if the issue affects access control, validate both allowed and blocked paths
- if the issue affects status calculation, validate determinism and boundary cases
- if the issue affects registration updates, validate historical snapshot behavior

Examples of relevant tests:
- status rules for At Risk, Confirmed, Full, and Waiting List
- auth and role checks for Admin/Editor vs Viewer
- CRUD flows for activity create/edit/archive
- registration updates and snapshot creation
- dashboard summaries and school-year filtering

Test execution should be real behavior validation, not mock-only validation.

---

## 5. When an issue may be closed

An issue may be closed only when all of the following are true:
- the PM confirms the issue scope and requirements are still valid
- the Engineer completed the implementation for that issue only
- the relevant tests were run and passed
- QA completed an independent check and returned PASS
- no unresolved defects remain that directly contradict the issue acceptance criteria
- the change does not broaden scope beyond the GitHub issue and project rules

If any required evidence is missing, the issue must remain open.

---

## 6. How QA should document findings

QA findings must be concrete and actionable.

When QA returns FAIL, it should include:
- the issue title and scope checked
- the exact acceptance criteria that failed
- the observed defect or mismatch
- supporting evidence such as command output, test name, or behavior observed
- the suggested next step for the Engineer

Preferred format:
- PASS or FAIL
- failed criteria list
- defect summary
- evidence
- follow-up request

Example:
- FAIL
- Acceptance criteria not met: activity status recalculation after registration update
- Defect: status remained unchanged after update because the central status rule was bypassed
- Evidence: targeted pytest failed or observed UI state differed from expected result

QA must not fix the implementation, but must clearly state what needs to be corrected.

---

## 7. How to avoid scope creep

Issues must stay narrow and focused.

Rules to prevent scope creep:
- work on one GitHub issue at a time
- do not combine adjacent feature work into one implementation
- do not add post-MVP capabilities unless the issue explicitly calls for them
- do not refactor unrelated code while fixing the issue
- do not introduce new abstractions or general-purpose infrastructure without clear need
- do not implement dashboard, import/export, or other future capabilities unless the issue explicitly includes them

If a proposed change is outside the issue scope, it must be deferred and documented, not included in the fix.

---

## 8. Required project-specific guardrails

These constraints apply to every issue and every workflow step:
- read the relevant GitHub issue before changing code
- read the matching project docs when needed
- keep the work aligned with the MVP and the current issue
- do not implement post-MVP features without explicit approval
- do not store child or family personal data
- do not bypass the centralized status calculation logic
- do not allow historical snapshots to be lost or ignored
- keep status calculation deterministic and centralized
- keep permission checks explicit and simple
- preserve school-year scoping and archive behavior

---

## 9. Workflow summary

This workflow should be followed for every issue:

PM:
- reads issue and relevant docs
- confirms scope and acceptance criteria
- clarifies if needed

Engineer:
- implements only the issue
- keeps changes small and relevant
- adds or updates tests
- runs relevant tests

QA:
- independently validates behavior against the issue
- runs relevant tests
- checks permissions, business rules, and regressions
- returns PASS or FAIL

If FAIL:
QA → Engineer → QA

If PASS:
issue may be considered complete.

This is the required project discipline for staying issue-scoped, test-backed, and safe for a first MVP implementation.
