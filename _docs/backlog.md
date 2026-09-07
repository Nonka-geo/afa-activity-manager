# MVP Backlog

This backlog is intentionally small and ordered by dependency. It focuses only on the MVP workflow required to deliver a working AFA activity viability manager using the simple Django + SQLite + Django templates architecture described in the project plan and technical architecture.

The following items omit post-MVP import/export features and keep all work aligned with the first working version.

---

## 1. Project bootstrap

### Goal
Set up the Django project foundation and development environment so the application can run locally with the required toolchain.

### Acceptance criteria
- A Django project is initialized with the required configuration.
- The project uses Python, Django, SQLite, pytest, and uv as specified.
- The app can run locally in a development environment.
- The project structure includes the required accounts and activities apps.
- A basic project configuration and settings are in place.
- A minimal smoke test confirms the application starts without configuration errors.

### Out of scope
- Import/export workflows
- Production deployment configuration
- Docker setup
- External services or paid integrations

### Constraints
- Keep the setup minimal and focused on local development.
- No cloud dependencies.
- No Docker in the MVP.
- No application logic beyond project initialization.

---

## 2. Authentication and roles

### Goal
Provide secure user login and clear read/write permissions for different user types.

### Acceptance criteria
- Users can log in and log out using Django authentication.
- There are at least two roles: Admin/Editor and Viewer.
- Viewer users can access read-only pages.
- Admin/Editor users can access management and update flows.
- Unauthorized users are redirected or blocked appropriately.
- Role checks are enforced in views and templates.

### Out of scope
- Self-service password reset
- User administration screens beyond basic role-based access
- Social login or external identity providers
- Advanced permission hierarchies

### Constraints
- Use Django’s built-in authentication system.
- Keep access control simple and explicit.
- No child or family data is involved in the auth layer.

---

## 3. School year model

### Goal
Support the concept of school-year scoped activity management so the dashboard and activity list operate on the correct current cohort.

### Acceptance criteria
- A SchoolYear model exists with a unique identifier such as 2026-2027.
- Activities belong to exactly one school year.
- A current or active school year can be selected or inferred.
- Dashboard and activity listings can be filtered by school year.
- Historical data remains associated with the relevant school year.

### Out of scope
- Copying activities between years
- Multi-year dashboards with complex comparisons
- Advanced school-year lifecycle management

### Constraints
- Keep the model minimal and sufficient for use in the MVP.
- Use SQLite for local persistence.
- Do not add unrelated reporting features.

---

## 4. Activity model

### Goal
Define the core activity data model and business identity required to manage extracurricular groups.

### Acceptance criteria
- An Activity model exists with required fields such as name, schedule, provider, age group, space, price, min participants, max participants, registration count, school year, archive state, and notes.
- Each activity has a permanent group code that does not change.
- Activities can be marked active or archived.
- Activity structure supports multiple groups with similar names but different properties.
- Activity data is stored without storing individual child records.

### Out of scope
- Import of source files
- Payment or billing data
- Family-level or child-level personal data
- Advanced activity metadata beyond the MVP need

### Constraints
- Aggregate counts only; no individual participant data.
- Model must support automatic viability calculation.
- Data model must remain simple enough for a first project.

---

## 5. Automatic viability status

### Goal
Automatically calculate the viability status of every activity from registration totals and thresholds.

### Acceptance criteria
- Activity status is derived automatically from minimum and maximum values.
- Status values are: At Risk, Confirmed, Full, and Waiting List.
- Status recalculates whenever registration count or threshold values change.
- The same status logic is used in the dashboard, detail views, and history records.
- Users cannot manually override the status value.

### Out of scope
- AI-based viability decisions
- Manual status override options
- Additional viability rules beyond the defined MVP logic

### Constraints
- The status rule must be centralized and testable.
- Use explicit business rules rather than ad hoc logic.
- Keep the implementation deterministic and easy to reason about.

---

## 6. Activity CRUD

### Goal
Allow authorized users to create, view, edit, and manage activities without adding unnecessary complexity.

### Acceptance criteria
- Admin/Editor users can create new activities.
- Admin/Editor users can edit activity details.
- Admin/Editor users can archive activities.
- Archived activities remain accessible in an archived view.
- Viewer users can view activities but cannot modify them.
- Activity records can be found through a basic list page and a detail page.

### Out of scope
- Bulk editing of many activities at once
- Advanced workflow automation
- Soft-delete plus restore complexity beyond archive state

### Constraints
- Keep CRUD operations focused on core operational needs.
- Use Django templates for the UI.
- Preserve integrity of the permanent group code and school-year associations.

---

## 7. Registration updates

### Goal
Allow authorized users to update activity registration counts and immediately reflect the new viability state.

### Acceptance criteria
- Admin/Editor users can update registration count values for an activity.
- Each update records a change to the activity’s current registrations.
- The status is recalculated as part of the update flow.
- Updates are saved in a way that supports historical tracking.
- Viewer users cannot change registrations.

### Out of scope
- Batch editing through uploaded files
- Individual participant registration records
- Automated registration imports from external sources

### Constraints
- The update flow must be explicit and auditable.
- Registration counts remain aggregate totals, not child-level records.
- Data changes must be easy to test with pytest.

---

## 8. Historical snapshots

### Goal
Capture and retain the registration history of each activity so the team can see how numbers changed over time.

### Acceptance criteria
- A snapshot record is created whenever a relevant registration or viability field changes.
- Each snapshot stores the activity reference, registration count, status, timestamp, and actor.
- Historical snapshots remain available after an activity is archived.
- A basic activity history view can show how registrations evolved over time.
- The snapshot logic is tested with real update flows.

### Out of scope
- Detailed rich audit reporting
- Complex trend analysis across multiple metrics
- Historical comparisons between years beyond the basic timeline

### Constraints
- Keep snapshots simple and minimal.
- Do not store child or family-level data.
- History must be consistent with the same status rules used in live activity views.

---

## 9. Dashboard

### Goal
Provide a simple overview of the current school year so AFA members can identify activity viability at a glance.

### Acceptance criteria
- The dashboard shows total active activities and summary counts by status.
- The dashboard distinguishes At Risk, Confirmed, Full, and Waiting List activity groups.
- Activities with attention needs are easy to identify in the overview.
- The dashboard is scoped to the current school year.
- Dashboard totals reflect currently active activity data.

### Out of scope
- Advanced analytics or charts beyond basic activity summaries
- Cross-school-year comparison views
- Exported dashboard reports

### Constraints
- Keep the dashboard simple, readable, and fast.
- Use existing activity and snapshot models rather than duplicate data structures.
- No external reporting dependencies.

---

## 10. Search and filtering

### Goal
Allow users to quickly locate and filter activities by the most relevant attributes.

### Acceptance criteria
- Users can search by activity name and other common identifying fields.
- Users can filter by schedule, provider, space, age/class group, school year, and status.
- Results update for the active school year without requiring separate logic in multiple places.
- Search and filtering are available to both viewers and editors.
- Empty or invalid filter combinations return sensible results.

### Out of scope
- Full-text search beyond simple query filters
- Advanced faceted analytics
- Complex saved queries or report presets

### Constraints
- Keep filtering logic simple and deterministic.
- Do not add broad admin tools or unrelated data filters.
- UI and queryset logic must remain understandable for a small project.

---

## 11. Archiving

### Goal
Allow activities to be hidden from active views without losing historical information or operational context.

### Acceptance criteria
- Admin/Editor users can archive activities.
- Archived activities are removed from the default active activity list.
- Archived activities remain accessible in an archived view.
- Historical snapshots and change history remain preserved for archived activities.
- Archived activities do not block current-year dashboard operations for active records.

### Out of scope
- Permanent deletion of records
- Complex restore workflows beyond basic archived access
- Separate archival policy management

### Constraints
- Archived records must remain available for reference.
- Archiving must not delete historical data.
- Keep archive behavior simple and deterministic.

---

## 12. Testing and validation

### Goal
Ensure the MVP is reliable, regressions are caught early, and key business rules are verified in real workflows.

### Acceptance criteria
- pytest is configured for the project.
- Unit tests cover activity status rules and core calculations.
- Integration tests cover authentication and authorization rules.
- Tests cover activity create/edit/archive behavior.
- Tests cover registration updates and history creation.
- Dashboard summary tests confirm the expected total and status counts.
- A minimum pass set runs successfully in the local environment.

### Out of scope
- UI automation beyond a small amount of critical path validation
- Performance testing at scale
- Complex cross-browser testing

### Constraints
- Keep tests focused on real project behavior.
- Use SQLite-backed testing where appropriate.
- No mock-heavy tests that validate only mocks instead of real behavior.

---

## MVP completion definition

The MVP is complete when the application supports the core operational workflow for AFA activity viability management:

- users log in with roles;
- activities exist under school years;
- status is calculated automatically;
- registration counts can be updated by authorized users;
- history is retained through snapshots;
- the dashboard reflects the current status of active activities;
- users can search, filter, and archive activities;
- tests validate the important business flow.

This path intentionally excludes import/export and other post-MVP features until the core identity, status, and monitoring workflow is working reliably.
