# Architecture Proposal for the AFA Activity Viability Manager

This document proposes a deliberately simple architecture for a first AI Dev Tools Zoomcamp project. The goal is to deliver a working MVP for monitoring extracurricular activity viability with clear separation from future enhancements.

## Project direction

- Python
- Django
- SQLite
- Django templates for the UI
- pytest for automated tests
- uv for dependency management
- no cloud services
- no paid APIs
- no Docker for the first version
- keep the solution intentionally small and operationally focused

The architecture below is designed for a single-team, small-scale project that can be built and tested reliably without introducing unnecessary complexity.

---

## 1. Application structure

For the MVP, the Django project should stay intentionally small and use only two apps.

Recommended structure:

- project_root/
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
    - activities/
    - accounts/
  - static/
  - tests/
  - fixtures/

This keeps the project easy to reason about:

- accounts handles user identity and role-based access.
- activities owns the activity data, school-year logic, dashboard overview, historical snapshots, search/filtering, and archiving behavior.

### MVP structure

The MVP should focus on:

- login and role checks
- activity management
- status calculation
- dashboard overview for the current school year
- registration history and snapshots
- search and filtering
- archiving
- school-year scoping

No separate dashboard, history, imports_exports, or common app should be created yet. Those responsibilities remain part of the activities app during the MVP.

### Post-MVP structure

Import/export is a future capability and should remain outside the initial Django app structure. It can be added later as a dedicated module or service layer when the core MVP is working and validated.

---

## 2. Main Django apps/modules

### 2.1 accounts

Purpose:
- user login and authentication
- role-based access control
- user profiles and account state

Responsibilities:
- manage admin/editor/viewer roles
- provide login, logout, and access checks
- expose user metadata for audit logging

This app should stay minimal. A custom profile or a small user model extension is enough if needed; it does not need a large identity framework.

### 2.2 activities

Purpose:
- hold the activity/group data
- calculate viability status
- manage school-year scoping
- provide dashboard overview
- store historical snapshots and change history
- support search, filtering, and archive state

Responsibilities:
- create, edit, archive, and list activities
- manage school-year associations
- maintain minimum and maximum counts
- calculate current status based on registration count
- support permanent group codes
- provide dashboard summary metrics for the current school year
- maintain historical registration snapshots and user-visible change history
- allow search and filtering by key values such as activity name, schedule, provider, space, age group, school year, and status

This is the core domain app for the project and will absorb the dashboard, history, search, and archival behavior during the MVP.

Import/export remains a future capability and is not part of the MVP app structure.

---

## 3. Data model

The data model should stay aggregate and simple. The system does not track child-level or family-level records.

### Core entities

#### User
- Django user account
- role: admin/editor or viewer
- active/inactive state
- audit trail association for changes made

#### SchoolYear
- name or identifier such as 2026-2027
- start/end period if useful
- active flag
- current school-year selection for dashboards

#### Activity
- unique permanent group code
- activity name
- schedule and day information
- provider
- age or class group
- space
- price
- minimum participants
- maximum participants
- current registration count
- status
- active or archived
- school year
- notes

Notes:
- The group code should never change once created.
- The activity identity should remain stable even if names or schedule details change.
- The application must treat activities as business entities, not as child records.

#### ActivitySnapshot
- activity reference
- registration count at a point in time
- derived status at that point in time
- timestamp
- user who caused the change
- optional note or reason

#### ActivityChangeLog or AuditEntry
- activity reference
- previous and new values
- changed field names
- timestamp
- user
- human-readable description

### Design principles for the model

- keep only aggregate counts, not child data
- separate operational configuration from historical tracking
- use a permanent group code as the stable identifier for activity identity
- avoid storing raw import rows as first-class business data unless later needed for audit

### MVP vs post-MVP data model

MVP data model should include:
- users
- school years
- activities
- snapshots
- change log entries

Post-MVP may add:
- more detailed audit metadata
- richer reporting tables
- import batch records
- export job summaries
- more advanced filtering metadata

---

## 4. Authentication and roles

The application should use Django’s built-in authentication system with a small role layer.

### Roles

#### Admin / Editor
- create and edit activities
- archive and restore activities
- update registrations
- manage school-year context
- view historical data
- access import/export features
- manage users and roles where included in scope

#### Viewer
- read-only access to dashboard and activity data
- view history and charts
- search and filter
- cannot edit activity status or counts
- cannot export content in the MVP

### Recommended approach

- leverage Django permissions and groups for clear access control
- keep a simple role model instead of a complex permission matrix
- enforce access in views and templates via permission checks and helper functions

### MVP access pattern

- admin/editor pages protected with permission checks
- viewer pages read-only
- data entry endpoints require editor-level permission
- historical and dashboard views available to both roles, with editor-only write controls hidden or disabled

### Post-MVP additions

- more granular role controls
- user lifecycle management inside the app
- password reset and account administration flows

---

## 5. Activity status calculation

The status logic is a core domain rule and should be centralized so that the same logic is used everywhere.

### Status rules

- At Risk: registrations are below minimum
- Confirmed: registrations are at or above minimum and below maximum
- Full: registrations equal maximum
- Waiting List: registrations exceed maximum

### Calculation approach

A single service or helper function should compute the status from the current data.

This avoids duplicated logic in views, templates, and import flows.

### Important rules

- status is derived; it is not manually entered by users
- the system recalculates status whenever relevant data changes
- calculation should be triggered on:
  - registration count update
  - minimum or maximum change
  - school-year or archive-state changes where needed
- the status should be displayed consistently in dashboard, detail views, and history entries

### MVP implementation choice

For the first version, keep the calculation simple and synchronous in the Django application.

The architecture should prioritize a clear, testable status function over a more elaborate event-driven design.

---

## 6. Historical snapshots

Historical tracking is a key product requirement and should be treated as an explicit domain capability rather than an afterthought.

### Snapshot purpose

A snapshot captures the state of an activity at a defined moment in time.

It should preserve:
- activity reference
- registration count
- status
- timestamp
- actor
- optional note or change reason

### When snapshots are created

- whenever registration count changes
- when a status-relevant field changes
- when admin/editor changes a value that affects viability monitoring

### Why this matters

The project is not just a current-state tracker; it is a trend-monitoring tool. Historical snapshots allow AFA members to answer questions like:

- how did registrations change over the last two weeks?
- did an activity decline after a change in capacity or schedule?
- which date was the turning point for a group?

### MVP snapshot design

Keep it small and reliable:
- snapshot per change or per relevant state update
- no complex event sourcing
- no heavy data warehouse patterns
- store only what is required for trend analysis and audit

### Post-MVP expansion

- richer charts and comparison views
- comparisons between school years
- more detailed audit narratives
- aggregated trend reports

---

## 7. Import/export approach

Import and export are valuable but should remain explicitly post-MVP in the first version.

### MVP position

The MVP should not depend on import/export being complete before the core viability workflow works.

Manual registration updates are sufficient for the first project milestone.

### Post-MVP import strategy

- support CSV first for simplicity
- support Excel after CSV works
- validate rows before applying changes
- show created versus updated rows
- report failed rows with reasons
- keep mapping rules explicit and simple

### Import rules

A later import flow may use a small set of deterministic matching rules:
- match on permanent group code when available
- otherwise match on a stable activity identifier or unique business key
- otherwise create a new activity record
- update registration count and other supported fields only when a valid match exists

### Export strategy

- admin/editor only
- limited to current activity data, not full historical detail in the early version
- CSV output first, Excel second if needed
- no export of internal notes in the first export version

### Technical decision

The project should favor straightforward file-based import/export over automation or cloud synchronization. This fits the project constraints and reduces operational complexity.

---

## 8. Testing strategy

Testing should be simple, dependable, and focused on real behavior.

### Tools

- pytest as the main test runner
- Django test integration for request, view, and database validation
- SQLite as the local test database
- small fixtures for activity and user data

### test layers

#### Unit tests
- status calculation rules
- snapshot creation logic
- school-year filtering
- validation rules for minimum and maximum counts

#### Integration tests
- login and role access checks
- create/edit/archive activity flows
- dashboard summary logic
- history rendering and chart data preparation

#### UI tests
- keep minimal for the MVP
- cover a small number of important templates and workflows
- avoid heavy front-end test complexity because the project uses Django templates

### Testing principles

- test real behavior, not mocked assumptions
- verify the status logic from real database states
- cover permission boundary checks
- ensure historical snapshot creation is exercised in real flows

### MVP test priorities

1. Activity status calculation
2. User role access control
3. Registration count updates and history creation
4. Dashboard summary counts
5. Archive behavior and historical retention

### Post-MVP expansion

- import validation tests
- export output tests
- larger dashboard/report tests
- edge-case validation around capacity and waiting list scenarios

---

## 9. Important technical decisions and trade-offs

### 9.1 Keep the model simple

A small number of domain entities is preferred over over-engineering.

This project should solve the operational problem clearly and predictably without adding unnecessary abstractions, event buses, or complex service layers.

### 9.2 Aggregate-only data model

The project intentionally does not store child-level information.

This is the best trade-off for privacy, simplicity, and the project’s public GitHub context.

### 9.3 Status is derived, not manually editable

This ensures consistency and removes “human override” drift.

It also simplifies audit and reduces user error.

### 9.4 Historical snapshots are a first-class feature

This is more valuable than a generic change log alone because trend analysis and monitoring are central to the product.

### 9.5 SQLite is adequate for the first version

SQLite fits the project constraints and supports quick development with no operational overhead.

It is a good fit for a first project, especially when the feature set remains small and local.

### 9.6 Django templates are the right UI choice

A Django template-based UI is simpler and more appropriate for an MVP than a JavaScript-heavy frontend.

It keeps the project focused on business logic, testing, and the operational workflow.

### 9.7 The MVP stays intentionally small

The architecture explicitly separates the MVP from post-MVP features so the team can ship a working version without getting blocked by import/export, advanced reporting, or broader admin capabilities.

This is important for the Zoomcamp context: a reliable MVP is more valuable than a large but incomplete product.

### 9.8 Import/export is intentionally deferred

CSV and Excel import/export are useful future capabilities, but they should not be part of the initial Django app structure or the first implementation pass.

This keeps the first version focused on the real operational workflow: manage activities, monitor viability, and track history.

### 9.9 No external services or paid integrations

This keeps the project local, reliable, and easy to run during the learning phase.

It also reduces the risk of hidden deployment and cost constraints.

---

## MVP summary

The MVP should deliver:

- secure user login for admin/editor and viewer roles
- activity management for the current school year
- automatic status calculation using minimum and maximum counts
- dashboard summary and activity overview
- manual registration updates
- historical registration snapshots
- basic search and filtering
- archive support without deleting history
- SQLite-backed local development setup
- pytest-based automated verification

## Post-MVP summary

The post-MVP roadmap can add:

- CSV and Excel import
- CSV and Excel export
- richer audit and reporting
- improved school-year administration
- broader user management controls
- more advanced charts and comparisons

This keeps the architecture clear and gives the project a realistic path from a small but useful MVP to a richer operational tool.
