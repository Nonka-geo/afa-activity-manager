# AFA Extracurricular Activity Viability Manager

## 1. Project Overview

The AFA Extracurricular Activity Viability Manager is a web application for AFA members responsible for managing extracurricular activities.

Its main purpose is to provide a simple way to monitor registration numbers and automatically determine whether each activity is viable based on its minimum and maximum participant thresholds.

The tool should also preserve registration history so AFA members can see how registrations evolve over time.

This project is initially being developed as part of the AI Dev Tools Zoomcamp 2026 and should remain small enough to implement as a first project while solving a real AFA operational problem.

---

## 2. Problem

AFA manages multiple extracurricular activities and groups.

Each activity may have different:

- schedules
- age/class groups
- providers
- spaces
- prices
- minimum participant requirements
- maximum capacity
- registration counts

During registration periods, AFA members need to quickly understand:

- which activities have enough registrations to run;
- which activities are at risk;
- which activities are full;
- which activities have registrations beyond capacity;
- how registration numbers have changed over time.

The information should be accessible to several AFA members without requiring access to individual children's registration data.

---

## 3. Users and Roles

The application will have individual user accounts.

### Admin / Editor

Admin/editor users have full activity-management permissions.

They can:

- create activities;
- edit activities;
- archive activities;
- view archived activities;
- update registration counts;
- import activity data from Excel/CSV;
- export activity data to Excel/CSV;
- view historical registration data;
- manage school years;
- copy activities from one school year to another;
- create and deactivate user accounts;
- assign user roles.

### Viewer

Viewer users have read-only access.

They can:

- view the dashboard;
- view activities;
- search and filter activities;
- view historical registration information and charts;
- view archived activities.

Viewers cannot modify or export data.

---

## 4. Activity Model

An activity/group should contain at least:

- unique group code;
- activity name;
- one or more days/schedules;
- provider;
- age/class group;
- space;
- price;
- minimum participants;
- maximum participants;
- current registration count;
- automatically calculated status;
- school year;
- internal notes;
- active/archived state.

### Group Code

The system generates a unique group code automatically.

The group code is permanent.

Changing the activity name, schedule, age group, or other activity details must not change the existing group code.

The same activity name may have multiple groups with different schedules, age groups, spaces, or capacities.

---

## 5. Activity Status Rules

Activity status is calculated automatically.

Users cannot manually override it.

### At Risk

```text
registrations < minimum participants
```

### Confirmed

```text
minimum participants <= registrations < maximum participants
```

### Full

```text
registrations == maximum participants
```

### Waiting List

```text
registrations > maximum participants
```

The status must be recalculated whenever relevant activity data changes.

---

## 6. Registration Data

The application tracks only the total registration count for each activity/group.

It does NOT store individual children's registrations.

Registration counts can be updated:

1. manually by an admin/editor;
2. through an Excel/CSV import.

---

## 7. Excel / CSV Import

Admins/editors can upload an Excel or CSV file containing activity data.

During import:

- new activities that do not exist are created;
- existing activities are updated;
- registration counts can be updated;
- relevant activity details can be updated.

The system should report the result of the import, including:

- activities created;
- activities updated;
- rows that could not be processed.

Matching/import rules will be defined during technical design.

---

## 8. Export

Admins/editors can export activity data to Excel or CSV.

Viewers cannot export data.

Historical data does not need to be included in the first export implementation unless explicitly added in a later iteration.

---

## 9. Historical Snapshots

The application keeps historical registration information.

A new snapshot is created whenever activity data affecting registration monitoring changes.

At minimum, a snapshot should preserve:

- activity/group identifier;
- registration count;
- calculated status;
- timestamp;
- user who made the change.

This allows AFA members to see how registration numbers evolved over time.

---

## 10. Activity History

Changes should identify the user who made them.

For example:

```text
06 Sep 2026 18:20
Maria changed registrations from 7 to 9.
```

Historical information must remain available even when an activity is archived.

---

## 11. Dashboard

The main dashboard should provide an immediate overview of the current school year.

### Summary Metrics

Show:

- total active activities;
- confirmed activities;
- at-risk activities;
- full activities;
- waiting-list activities.

### Activity Overview

Display activities with key information such as:

- activity name/group;
- schedule;
- registrations;
- minimum;
- maximum;
- status.

Activities requiring attention should be easy to identify.

### Registration History

Users should be able to view a chart showing registration changes over time for an activity.

---

## 12. Search and Filtering

Users should be able to search/filter activities by relevant fields including:

- activity name;
- day/schedule;
- provider;
- space;
- age/class group;
- status;
- school year.

---

## 13. Archiving

Activities should not normally be permanently deleted.

Admins/editors can archive an activity.

Archived activities:

- disappear from the normal active activity view;
- remain available under an Archived Activities view;
- retain their historical snapshots and change history.

---

## 14. School Years

Activities belong to a school year, for example:

```text
2026-2027
```

Admins can create a new school year.

When creating a new school year, they can optionally copy activities from the previous year.

When copied:

- activity configuration is copied;
- registration counts are reset to zero;
- new group codes are generated for the new activity groups;
- previous-year historical data remains associated with the previous year.

Admins may also start a new school year without copying previous activities.

---

## 15. User Management

Each user has an individual account.

Admins can:

- create users;
- deactivate users;
- assign roles;
- change users between Admin/Editor and Viewer roles;
- manage/reset user passwords.

Self-service password reset is not required for the initial version.

---

## 16. Internal Notes

Admins/editors may add internal notes to an activity.

Notes are visible within the AFA application.

Internal notes should not be included in standard activity exports.

---

## 17. MVP Scope

The first implementation should remain deliberately small.

The MVP should prioritize the core viability-monitoring workflow.

### Required MVP Features

1. Individual user login.
2. Admin/editor and viewer permissions.
3. Create and edit activities.
4. Automatically generated permanent group code.
5. Minimum and maximum participant values.
6. Manual registration count updates.
7. Automatic status calculation.
8. Activity list.
9. Dashboard summary metrics.
10. Search/filter activities.
11. Archive and view archived activities.
12. Historical snapshots when registration data changes.
13. Basic registration-history chart.
14. School-year association.

The MVP should use synthetic/demo data during development.

---

## 18. Post-MVP Features

The following requirements are useful but can be implemented after the basic application works:

### Import / Export

- Excel import;
- CSV import;
- update existing activities through import;
- create missing activities through import;
- Excel export;
- CSV export.

### School-Year Management

- create school years through the UI;
- copy activities from the previous school year;
- optionally start an empty school year.

### User Administration

- create/deactivate users through the application;
- assign roles through the application;
- admin-managed password resets.

### Enhanced History

- richer audit/change descriptions;
- additional charts;
- comparison of registration trends.

These features are part of the product direction but should not block completion of the first working version.

---

## 19. Out of Scope

The following are explicitly outside the initial project scope:

- storing children's names;
- storing family personal data;
- payment management;
- bank information;
- direct PlayOff integration;
- direct Dinantia integration;
- WhatsApp integration;
- automated emails;
- Google Sheets synchronization;
- provider billing;
- attendance tracking;
- automatic registration of children;
- AI-based viability decisions;
- production AFA personal data.

---

## 20. Privacy and Demo Data

The project repository may be public on GitHub.

Therefore:

- no real children's data may be committed;
- no family personal information may be committed;
- no credentials or secrets may be committed;
- development/demo datasets must be synthetic or properly anonymized.

The application only needs aggregate registration counts for its core functionality.

---

## 21. Core Workflow

```text
AFA member logs in
        |
        v
Views current school-year dashboard
        |
        v
Views activities and their registration status
        |
        v
Admin/editor updates registration count
        |
        v
System saves historical snapshot
        |
        v
System recalculates status
        |
        v
Dashboard and history are updated
```

---

## 22. Success Criteria

The first version is successful when an AFA member can:

1. log in;
2. see all current extracurricular activity groups;
3. see current registrations versus minimum/maximum capacity;
4. immediately identify At Risk, Confirmed, Full, and Waiting List activities;
5. update registration counts;
6. see previous registration counts;
7. see registration evolution on a chart;
8. search/filter activities;
9. archive activities without losing their history.

The application should solve these tasks without storing any individual child or family registration data.

---

## 23. Development Principle

This project should be developed incrementally.

The specification defines the intended product behavior. Implementation should be divided into small backlog items with explicit acceptance criteria.

Features outside the MVP should not be implemented until the core workflow is working and tested.
