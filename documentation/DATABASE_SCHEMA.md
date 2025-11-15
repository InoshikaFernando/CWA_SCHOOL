# Database Schema Documentation

**Generated:** 2025-11-16 10:54:37

> **Note:** This document is auto-generated. Run `python Testing/generate_database_documentation.py` to update it.

---

## Table of Contents

- [LogEntry](#logentry) - `django_admin_log`
- [Group](#group) - `auth_group`
- [Permission](#permission) - `auth_permission`
- [ContentType](#contenttype) - `django_content_type`
- [Answer](#answer) - `maths_answer`
- [BasicFactsResult](#basicfactsresult) - `maths_basicfactsresult`
- [ClassRoom](#classroom) - `maths_classroom`
- [CustomUser](#customuser) - `maths_customuser`
- [Enrollment](#enrollment) - `maths_enrollment`
- [Level](#level) - `maths_level`
- [Question](#question) - `maths_question`
- [StudentAnswer](#studentanswer) - `maths_studentanswer`
- [TimeLog](#timelog) - `maths_timelog`
- [Topic](#topic) - `maths_topic`
- [TopicLevelStatistics](#topiclevelstatistics) - `maths_topiclevelstatistics`
- [Session](#session) - `django_session`

---

## LogEntry

**App:** `admin`
**Database Table:** `django_admin_log`

**Description:** LogEntry(id, action_time, user, content_type, object_id, object_repr, action_flag, change_message)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `action_time` | DateTimeField | default=<function now at 0x000001BC483F1760> | action time |
| `user` | ForeignKey -> CustomUser | db_index=True | user → CustomUser |
| `content_type` | ForeignKey -> ContentType | null=True, blank=True, db_index=True | content type → ContentType |
| `object_id` | TextField | null=True, blank=True | object id |
| `object_repr` | CharField | None | object repr |
| `action_flag` | PositiveSmallIntegerField | None | action flag |
| `change_message` | TextField | blank=True | change message |

**Default Ordering:** -action_time

---

## Group

**App:** `auth`
**Database Table:** `auth_group`

**Description:** Groups are a generic way of categorizing users to apply permissions, or
some other label, to those users. A user can belong to any number of
groups.

A user in a group automatically has all the permissions granted to that
group. For example, if the group 'Site editors' has the permission
can_edit_home_page, any user in that group will have that permission.

Beyond permissions, groups are a convenient way to categorize users to
apply some label, or extended functionality, to them. For example, you
could create a group 'Special users', and you could write code that would
do special things to those users -- such as giving them access to a
members-only portion of your site, or sending them members-only email
messages.

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `name` | CharField | unique=True | name |
| `permissions` | ManyToMany -> Permission | blank=True | permissions → Permission |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `CustomUser` | `groups` | ManyToMany -> Group | `user_set` |

### Many-to-Many Relationships

| Field Name | Related Model | Through Table | Related Name |
|------------|---------------|---------------|--------------|
| `permissions` | `Permission` | `auth_group_permissions` | `group` |

---

## Permission

**App:** `auth`
**Database Table:** `auth_permission`

**Description:** The permissions system provides a way to assign permissions to specific
users and groups of users.

The permission system is used by the Django admin site, but may also be
useful in your own code. The Django admin site uses permissions as follows:

    - The "add" permission limits the user's ability to view the "add" form
      and add an object.
    - The "change" permission limits a user's ability to view the change
      list, view the "change" form and change an object.
    - The "delete" permission limits the ability to delete an object.
    - The "view" permission limits the ability to view an object.

Permissions are set globally per type of object, not per specific object
instance. It is possible to say "Mary may change news stories," but it's
not currently possible to say "Mary may change news stories, but only the
ones she created herself" or "Mary may only change news stories that have a
certain status or publication date."

The permissions listed above are automatically created for each model.

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `name` | CharField | None | name |
| `content_type` | ForeignKey -> ContentType | db_index=True | content type → ContentType |
| `codename` | CharField | None | codename |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `Group` | `permissions` | ManyToMany -> Permission | `group_set` |
| `CustomUser` | `user_permissions` | ManyToMany -> Permission | `user_set` |

**Default Ordering:** content_type__app_label, content_type__model, codename

**Unique Together:** (('content_type', 'codename'),)

---

## ContentType

**App:** `contenttypes`
**Database Table:** `django_content_type`

**Description:** ContentType(id, app_label, model)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `app_label` | CharField | None | app label |
| `model` | CharField | None | python model class name |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `LogEntry` | `content_type` | ForeignKey -> ContentType | `logentry_set` |
| `Permission` | `content_type` | ForeignKey -> ContentType | `permission_set` |

**Unique Together:** (('app_label', 'model'),)

---

## Answer

**App:** `maths`
**Database Table:** `maths_answer`

**Description:** Answer(id, question, answer_text, is_correct, order)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `question` | ForeignKey -> Question | db_index=True | question → Question |
| `answer_text` | TextField | None | answer text |
| `is_correct` | BooleanField | default=False | is correct |
| `order` | PositiveIntegerField | default=0 | Order for multiple choice options |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `StudentAnswer` | `selected_answer` | ForeignKey -> Answer | `studentanswer_set` |

**Default Ordering:** question, order, id

---

## BasicFactsResult

**App:** `maths`
**Database Table:** `maths_basicfactsresult`

**Description:** Store Basic Facts quiz attempts in database for persistent tracking

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `student` | ForeignKey -> CustomUser | db_index=True | student → CustomUser |
| `level` | ForeignKey -> Level | db_index=True | level → Level |
| `session_id` | CharField | None | Session identifier for tracking attempts |
| `score` | PositiveIntegerField | None | Number of correct answers |
| `total_points` | PositiveIntegerField | None | Total possible points |
| `time_taken_seconds` | PositiveIntegerField | None | Time taken for this attempt in seconds |
| `points` | DecimalField | None | Calculated points based on score, time, and percentage |
| `completed_at` | DateTimeField | blank=True | completed at |

**Default Ordering:** -completed_at

**Indexes:**
- ['student', 'level']
- ['student', 'level', 'session_id']

---

## ClassRoom

**App:** `maths`
**Database Table:** `maths_classroom`

**Description:** ClassRoom(id, name, teacher, code)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `name` | CharField | None | name |
| `teacher` | ForeignKey -> CustomUser | db_index=True | teacher → CustomUser |
| `code` | CharField | unique=True, default=<function generate_class_code at 0x000001BC495BF060> | code |
| `levels` | ManyToMany -> Level | blank=True | levels → Level |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `Enrollment` | `classroom` | ForeignKey -> ClassRoom | `enrollments` |

### Many-to-Many Relationships

| Field Name | Related Model | Through Table | Related Name |
|------------|---------------|---------------|--------------|
| `levels` | `Level` | `maths_classroom_levels` | `classrooms` |

---

## CustomUser

**App:** `maths`
**Database Table:** `maths_customuser`

**Description:** CustomUser(id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined, is_teacher, date_of_birth, country, region)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `password` | CharField | None | password |
| `last_login` | DateTimeField | null=True, blank=True | last login |
| `is_superuser` | BooleanField | default=False | Designates that this user has all permissions without explicitly assigning them. |
| `username` | CharField | unique=True | Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only. |
| `first_name` | CharField | blank=True | first name |
| `last_name` | CharField | blank=True | last name |
| `email` | EmailField | blank=True | email address |
| `is_staff` | BooleanField | default=False | Designates whether the user can log into this admin site. |
| `is_active` | BooleanField | default=True | Designates whether this user should be treated as active. Unselect this instead of deleting accounts. |
| `date_joined` | DateTimeField | default=<function now at 0x000001BC483F1760> | date joined |
| `is_teacher` | BooleanField | default=False | is teacher |
| `date_of_birth` | DateField | null=True, blank=True | Date of birth |
| `country` | CharField | blank=True | Country |
| `region` | CharField | blank=True | Region/State/Province |
| `groups` | ManyToMany -> Group | blank=True | The groups this user belongs to. A user will get all permissions granted to each of their groups. → Group |
| `user_permissions` | ManyToMany -> Permission | blank=True | Specific permissions for this user. → Permission |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `LogEntry` | `user` | ForeignKey -> CustomUser | `logentry_set` |
| `ClassRoom` | `teacher` | ForeignKey -> CustomUser | `classes` |
| `Enrollment` | `student` | ForeignKey -> CustomUser | `enrollments` |
| `StudentAnswer` | `student` | ForeignKey -> CustomUser | `student_answers` |
| `BasicFactsResult` | `student` | ForeignKey -> CustomUser | `basic_facts_results` |
| `TimeLog` | `student` | ForeignKey -> CustomUser | `time_log` |

### Many-to-Many Relationships

| Field Name | Related Model | Through Table | Related Name |
|------------|---------------|---------------|--------------|
| `groups` | `Group` | `maths_customuser_groups` | `user` |
| `user_permissions` | `Permission` | `maths_customuser_user_permissions` | `user` |

---

## Enrollment

**App:** `maths`
**Database Table:** `maths_enrollment`

**Description:** Enrollment(id, student, classroom, date_enrolled)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `student` | ForeignKey -> CustomUser | db_index=True | student → CustomUser |
| `classroom` | ForeignKey -> ClassRoom | db_index=True | classroom → ClassRoom |
| `date_enrolled` | DateTimeField | blank=True | date enrolled |

**Unique Together:** (('student', 'classroom'),)

---

## Level

**App:** `maths`
**Database Table:** `maths_level`

**Description:** Level(id, level_number, title)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `level_number` | PositiveIntegerField | unique=True | level number |
| `title` | CharField | blank=True | title |
| `topics` | ManyToMany -> Topic | blank=True | topics → Topic |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `ClassRoom` | `levels` | ManyToMany -> Level | `classrooms` |
| `Question` | `level` | ForeignKey -> Level | `questions` |
| `BasicFactsResult` | `level` | ForeignKey -> Level | `basic_facts_results` |
| `TopicLevelStatistics` | `level` | ForeignKey -> Level | `topic_statistics` |

### Many-to-Many Relationships

| Field Name | Related Model | Through Table | Related Name |
|------------|---------------|---------------|--------------|
| `topics` | `Topic` | `maths_level_topics` | `levels` |

**Default Ordering:** level_number

---

## Question

**App:** `maths`
**Database Table:** `maths_question`

**Description:** Question(id, level, topic, question_text, question_type, difficulty, points, explanation, image, created_at, updated_at)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `level` | ForeignKey -> Level | db_index=True | level → Level |
| `topic` | ForeignKey -> Topic | null=True, blank=True, db_index=True | Topic this question belongs to (e.g., BODMAS/PEMDAS, Measurements, Fractions) → Topic |
| `question_text` | TextField | None | question text |
| `question_type` | CharField | default=multiple_choice | question type |
| `difficulty` | PositiveIntegerField | default=1 | 1=Easy, 2=Medium, 3=Hard |
| `points` | PositiveIntegerField | default=1 | points |
| `explanation` | TextField | blank=True | Explanation for the correct answer |
| `image` | ImageField | null=True, blank=True | Upload an image for this question |
| `created_at` | DateTimeField | blank=True | created at |
| `updated_at` | DateTimeField | blank=True | updated at |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `Answer` | `question` | ForeignKey -> Question | `answers` |
| `StudentAnswer` | `question` | ForeignKey -> Question | `student_answers` |

**Default Ordering:** level, difficulty, created_at

---

## StudentAnswer

**App:** `maths`
**Database Table:** `maths_studentanswer`

**Description:** StudentAnswer(id, student, question, selected_answer, text_answer, is_correct, points_earned, answered_at, session_id, time_taken_seconds)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `student` | ForeignKey -> CustomUser | db_index=True | student → CustomUser |
| `question` | ForeignKey -> Question | db_index=True | question → Question |
| `selected_answer` | ForeignKey -> Answer | null=True, blank=True, db_index=True | selected answer → Answer |
| `text_answer` | TextField | blank=True | For short answer questions |
| `is_correct` | BooleanField | default=False | is correct |
| `points_earned` | PositiveIntegerField | default=0 | points earned |
| `answered_at` | DateTimeField | blank=True | answered at |
| `session_id` | CharField | blank=True, default= | Session identifier for tracking attempts |
| `time_taken_seconds` | PositiveIntegerField | default=0 | Time taken for this attempt in seconds |

**Default Ordering:** -answered_at

**Unique Together:** (('student', 'question'),)

---

## TimeLog

**App:** `maths`
**Database Table:** `maths_timelog`

**Description:** Track daily and weekly time spent by students on the app

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `student` | ForeignKey -> CustomUser | unique=True, db_index=True | student → CustomUser |
| `daily_total_seconds` | PositiveIntegerField | default=0 | Total seconds spent today |
| `weekly_total_seconds` | PositiveIntegerField | default=0 | Total seconds spent this week |
| `last_reset_date` | DateField | blank=True | Last date when daily time was reset |
| `last_reset_week` | IntegerField | default=0 | ISO week number of last weekly reset |
| `last_activity` | DateTimeField | blank=True | Last time activity was recorded |

**Default Ordering:** -last_activity

---

## Topic

**App:** `maths`
**Database Table:** `maths_topic`

**Description:** Topic(id, name)

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `name` | CharField | None | name |

### Reverse Relationships

These relationships point TO this model:

| From Model | Field Name | Type | Related Name |
|------------|------------|------|--------------|
| `Level` | `topics` | ManyToMany -> Topic | `levels` |
| `Question` | `topic` | ForeignKey -> Topic | `questions` |
| `TopicLevelStatistics` | `topic` | ForeignKey -> Topic | `level_statistics` |

---

## TopicLevelStatistics

**App:** `maths`
**Database Table:** `maths_topiclevelstatistics`

**Description:** Store average and standard deviation (sigma) for each topic-level combination

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `level` | ForeignKey -> Level | db_index=True | level → Level |
| `topic` | ForeignKey -> Topic | db_index=True | topic → Topic |
| `average_points` | DecimalField | default=0 | Average points across all students |
| `sigma` | DecimalField | default=0 | Standard deviation (sigma) |
| `student_count` | PositiveIntegerField | default=0 | Number of students who have completed this topic-level |
| `last_updated` | DateTimeField | blank=True | Last time statistics were calculated |

**Default Ordering:** level__level_number, topic__name

**Unique Together:** (('level', 'topic'),)

**Indexes:**
- ['level', 'topic']

---

## Session

**App:** `sessions`
**Database Table:** `django_session`

**Description:** Django provides full support for anonymous sessions. The session
framework lets you store and retrieve arbitrary data on a
per-site-visitor basis. It stores data on the server side and
abstracts the sending and receiving of cookies. Cookies contain a
session ID -- not the data itself.

The Django sessions framework is entirely cookie-based. It does
not fall back to putting session IDs in URLs. This is an intentional
design decision. Not only does that behavior make URLs ugly, it makes
your site vulnerable to session-ID theft via the "Referer" header.

For complete documentation on using Sessions in your code, consult
the sessions documentation that is shipped with Django (also available
on the Django web site).

### Fields

| Field Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| `session_key` | CharField | unique=True, primary_key=True | session key |
| `session_data` | TextField | None | session data |
| `expire_date` | DateTimeField | db_index=True | expire date |

---

## Relationship Diagram

### Foreign Key Relationships

```
LogEntry --|> CustomUser : user
LogEntry --|> ContentType : content_type
Permission --|> ContentType : content_type
Answer --|> Question : question
BasicFactsResult --|> CustomUser : student
BasicFactsResult --|> Level : level
ClassRoom --|> CustomUser : teacher
Enrollment --|> CustomUser : student
Enrollment --|> ClassRoom : classroom
Question --|> Level : level
Question --|> Topic : topic
StudentAnswer --|> CustomUser : student
StudentAnswer --|> Question : question
StudentAnswer --|> Answer : selected_answer
TimeLog --|> CustomUser : student
TopicLevelStatistics --|> Level : level
TopicLevelStatistics --|> Topic : topic
```

### Many-to-Many Relationships

```
Session }o--o{ Permission : permissions
Session }o--o{ Level : levels
Session }o--o{ Group : groups
Session }o--o{ Permission : user_permissions
Session }o--o{ Topic : topics
```
