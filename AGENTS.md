# AGENTS.md

This repository is the AFA Extracurricular Activity Viability Manager, a small Django project for monitoring extracurricular activity viability for AFA members.

This file is the persistent operating guide for coding agents working in this repository. Follow it before making changes.

## 1. Project purpose

The project helps AFA members understand whether extracurricular activities are viable based on registration counts and minimum/maximum participant thresholds.

The application is meant to:
- track activity registrations at an aggregate level,
- calculate whether each activity is At Risk, Confirmed, Full, or Waiting List,
- show the current school-year status at a glance,
- retain activity registration history over time,
- allow authorized users to review and update activity data safely.

This project is intentionally small and suitable for a first AI Dev Tools Zoomcamp effort.

## 2. MVP scope

The MVP is intentionally limited to the core operational workflow.

In scope for the MVP:
- project bootstrap
- authentication and roles
- school year model
- activity model
- automatic viability status
- activity CRUD
- registration updates
- historical snapshots
- dashboard
- search/filtering
- archiving
- tests

The MVP should remain small enough to be implemented and validated reliably with Django, SQLite, Django templates, pytest, and uv.

## 3. Explicit out-of-scope features

The following features are explicitly out of scope for the MVP and must not be implemented unless a human explicitly requests them:
- CSV import
- Excel import
- CSV export
- Excel export
- automated syncing with Google Sheets or other external systems
- direct integration with third-party systems or paid APIs
- payment or billing workflows
- family or child personal data storage
- attendance tracking
- AI-based viability decisions
- production deployment setup
- Docker-based workflows
- any new feature not listed in the current issue being worked

If an issue mentions a post-MVP feature, treat it as future work and do not implement it during MVP work.

## 4. Technical stack

The project uses:
- Python
- Django
- SQLite
- Django templates for user interface rendering
- pytest for automated tests
- uv for dependency management

Additional constraints:
- keep the architecture simple
- no cloud services
- no paid APIs
- no Docker in the MVP
- no production-only complexity during the early build

## 5. Repository structure

The project is expected to follow a simple structure with a small Django setup.

Planned structure:
- manage.py
- config/
  - settings.py
  - urls.py
  - wsgi.py
  - asgi.py
- apps/
  - accounts/
  - activities/
- templates/
  - base.html
  - accounts/
  - activities/
- static/
- tests/
- fixtures/
- _docs/
  - plan.md
  - architecture.md
  - backlog.md
- AGENTS.md

Notes:
- Do not create extra Django apps for dashboard, history, imports_exports, or common logic unless a human explicitly requests it.
- Keep the core behavior inside the MVP app boundaries and avoid unnecessary abstraction.

## 6. Core domain rules

Agents must preserve these domain rules in all implementation work:
- The system tracks aggregate registration counts only.
- It does not store child-level or family-level personal data.
- The activity group code is permanent and should not change.
- Activity records are identified by a stable business identity, not by mutable metadata.
- The status of an activity is derived from business rules, not manually entered.
- Historical snapshots must be preserved even when an activity is archived.
- School-year scopes must be respected in dashboard and activity logic.

## 7. User roles and permissions

The project uses simple role-based access:

### Admin / Editor
- create and edit activities
- archive and restore activities
- update registration counts
- view historical information
- manage school-year context
- perform role-appropriate admin actions in scope of the issue

### Viewer
- read-only access to activity and dashboard information
- search and filter activity data
- view history and archive information
- cannot modify activity data or registration counts

Rules:
- Keep permission checks explicit and simple.
- Do not implement extended permission systems beyond the issue scope.
- If an issue is about access control, validate both allowed and blocked paths.

## 8. Activity viability rules

The activity viability rules are deterministic and must remain centralized.

Status rules:
- At Risk: registrations < minimum participants
- Confirmed: minimum participants <= registrations < maximum participants
- Full: registrations == maximum participants
- Waiting List: registrations > maximum participants

Important rules:
- Status calculation must remain deterministic.
- Status calculation must be centralized in one shared place rather than duplicated across views or templates.
- Users cannot manually override the calculated status.
- The status must be recalculated whenever relevant values change, especially registration counts, minimum, or maximum values.

## 9. Historical snapshot rules

Historical snapshots are a required MVP feature.

Rules:
- A snapshot must be created when registrations or other relevant activity state changes.
- Each snapshot should preserve at minimum:
  - activity reference
  - registration count
  - calculated status
  - timestamp
  - acting user
- Historical snapshots must remain accessible even after archiving.
- The snapshot logic must not be bypassed during registration updates.
- Historical tracking must be preserved as a first-class product rule, not an optional add-on.

## 10. Privacy constraints

Privacy and data handling are mandatory constraints.

Rules:
- Do not store child or family personal data.
- Do not store names, contact information, family details, or any personally identifying data unrelated to aggregate activity viability.
- Use synthetic or anonymized demo data only in development.
- Never commit real personal data or secrets.
- Keep the project data model aggregate-only.
- If a feature would require personal or familial data, it is out of scope and should not be implemented.

## 11. Testing expectations

The MVP must be tested with pytest.

Minimum expectations:
- write or update tests for the issue being implemented
- run the relevant tests before considering the issue complete
- cover the core business behavior impacted by the change
- validate access control rules when role-based behavior is involved
- validate determinism for status calculation
- validate historical snapshot behavior when update workflows change

Rules:
- Prefer real behavior tests over mock-heavy tests.
- Do not claim an issue is complete without running the relevant test set.
- If a test does not exist for the changed behavior, create one as part of the issue work.

## 12. Development workflow

Follow this workflow for safe, issue-scoped development:
1. Read the relevant GitHub issue before implementing.
2. Read the relevant project documents in _docs/ as needed.
3. Keep the work limited to the issue scope.
4. Make the smallest possible change that solves the issue.
5. Run relevant tests before completing the issue.
6. Do not add unrelated refactors or features while working on the issue.
7. Keep the implementation simple, readable, and aligned with the MVP architecture.

## 13. GitHub issue workflow

The GitHub issue is the source of truth for work.

Rules:
- Read the matching issue before implementing any code.
- Do not start work without a clear issue context.
- Keep the implementation aligned to the issue’s Goal, Acceptance criteria, Out of scope, and Constraints.
- Do not implement post-MVP features unless explicitly requested by the issue or by a human.
- If the issue is unclear, ask for clarification before changing code.
- Update or reference the issue if the implementation requires scope clarification.

## 14. Rules for keeping changes small and issue-scoped

Agents must keep every code change narrow and maintainable.

Rules:
- One issue should normally correspond to one focused change set.
- Do not broaden scope to adjacent features during the same issue.
- Do not implement future capabilities while solving the current issue.
- Do not add large abstractions or generic infrastructure that are not required by the issue.
- Keep domain logic simple and deterministic.
- Keep UI changes minimal and consistent with Django template-based development.
- Prefer direct, readable code over clever or over-engineered solutions.
- If a change crosses a major project boundary, stop and reassess scope before continuing.

## Final operating rule

Do not implement post-MVP features unless a human explicitly asks for them.
Do not store personal child or family data.
Do not bypass the centralized status calculation logic.
Do not allow historical snapshots to be lost or ignored.
Read the issue, work only within scope, and verify the relevant tests before considering the task complete.
