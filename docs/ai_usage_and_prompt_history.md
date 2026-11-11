# AI Assistance and Prompt History

## 1. Introduction

While developing this project, I used ChatGPT as a supporting tool to understand the requirements, solve technical problems, improve my implementation, and learn data engineering concepts.

My goal was not just to complete the assignment, but also to understand how an incremental data ingestion pipeline works in a practical environment.

I worked on the project using Python, SQLite, PowerShell, Git, and GitHub. I used AI assistance whenever I needed clarification, implementation guidance, or help troubleshooting an issue.

## 2. How I Used ChatGPT During Development

I used ChatGPT at different stages of the project.

### Stage 1: Understanding the requirements

I started by trying to understand what the project expected and how to approach it.

Some of the questions I discussed were:

- How should I approach this data engineering challenge?
- What is incremental data ingestion, and why is it needed?
- How do watermarks help identify new and updated records?
- How can I make sure running a pipeline multiple times does not create duplicate data?
- What should happen when records arrive late or out of order?
- How should a pipeline handle failed executions?

**My takeaway:** This helped me understand the main requirements and plan the project before starting the implementation.

### Stage 2: Setting up the project

I needed guidance to organize the Python application properly and work with the project from Windows PowerShell.

Some of my prompts included:

- Guide me through creating the project structure step by step.
- Help me set up a Python virtual environment.
- Explain which modules are needed for the ingestion pipeline.
- How should I connect Python with SQLite?
- Explain the purpose of each Python file in simple terms.

**My takeaway:** I learned how to organize the application into separate modules instead of putting all the logic into one Python file.

### Stage 3: Building the ingestion pipeline

During implementation, I asked for help with different parts of the pipeline.

Examples of my prompts:

- Help me read JSON records from a source file.
- How can I validate required fields and data types?
- How should I implement watermark-based incremental processing?
- How can I handle duplicate event IDs?
- Help me implement insert and update operations.
- How should delete events be handled without permanently removing historical information?
- How can I prevent older records from overwriting newer records?

**My takeaway:** These discussions helped me understand the flow from source data reading and validation to loading records into the target database.

### Stage 4: Debugging and fixing errors

I shared errors and terminal outputs whenever something did not work as expected.

Examples of my prompts:

- Explain this Python error and help me fix it.
- I am getting an import error in PowerShell. What should I check?
- Help me understand why this command is failing.
- How can I inspect the SQLite database tables?
- Check whether this file is necessary or unused.
- Explain what this terminal output means before I continue.

**My takeaway:** I learned to investigate errors using terminal output, database queries, and small tests rather than blindly changing code.

### Stage 5: Testing different scenarios

I wanted to check whether the pipeline behaved correctly in different situations.

Examples of my prompts:

- How can I test whether running the same input twice creates duplicates?
- Help me test late-arriving records.
- How can I verify that an older update does not replace newer data?
- Help me test soft-delete functionality.
- How can I simulate a pipeline failure?
- How do I verify that the database changes are rolled back after a failure?
- Help me test malformed JSON input.

**My takeaway:** Testing these situations helped me understand why idempotency, transaction handling, validation, and recovery are important in data engineering.

### Stage 6: Preparing project documentation

After implementation and testing, I worked on documenting the project.

Examples of my prompts:

- Help me prepare a clear README with setup and execution instructions.
- Explain the architecture and data flow.
- Help me document the database tables and columns.
- Explain the design decisions and limitations.
- Help me prepare a reconciliation report with actual test results.

**My takeaway:** I learned that documentation should explain not only what the application does, but also why certain design decisions were made.

### Stage 7: GitHub and final submission

I also needed help managing the repository and preparing it for submission.

Examples of my prompts:

- Guide me through checking the files before committing.
- How can I push my project to GitHub?
- Help me resolve Git remote and push errors.
- How can I confirm that my local branch is synchronized with GitHub?
- Does my repository contain the required project deliverables?
- Help me compare my project against the submission guidelines.

**My takeaway:** I learned how to maintain the project in Git and prepare a public repository for review.

## 3. Where AI Helped Me the Most

ChatGPT was particularly useful in the following areas:

- Understanding incremental ingestion and watermark concepts.
- Planning the Python project structure.
- Getting implementation suggestions for database and pipeline operations.
- Troubleshooting Python and PowerShell errors.
- Identifying useful testing scenarios.
- Understanding transaction rollback and idempotency.
- Improving the README and technical documentation.

I used AI suggestions as guidance and checked the implementation by running the code and reviewing the results.

## 4. What I Personally Worked On

During the project, I worked in my local development environment and performed the following activities:

- Set up the Python project and virtual environment.
- Created and organized the project files.
- Executed the ingestion pipeline using sample JSON data.
- Inspected SQLite tables and records.
- Ran the automated test suite.
- Checked duplicate, update, delete, and late-arriving event scenarios.
- Simulated a pipeline failure and checked whether data changes were rolled back.
- Tested malformed JSON input.
- Managed Git commits and pushed the code to GitHub.
- Reviewed the project documentation and execution results.

I also used the test output and database records to check whether the implementation behaved as expected.

## 5. Testing Results

The following validation was performed during development:

| Test or scenario | Result |
|---|---|
| Automated pytest suite | 18 tests passed |
| Repeated input processing | No duplicate target records |
| Late-arriving events | Processed |
| Older events | Prevented from overwriting newer records |
| Update operations | Verified |
| Delete operations | Verified using soft deletes |
| Simulated pipeline failure | Transaction rollback verified |
| Malformed JSON | Failed run recorded; watermark unchanged |

These results represent the tests performed in my local development environment.

## 6. What I Learned

Working on this project improved my understanding of several practical data engineering concepts:

1. How incremental ingestion works using source timestamps and watermarks.
2. Why idempotency is important when pipelines are rerun.
3. How to handle duplicate and late-arriving events.
4. How validation helps maintain data quality.
5. How quarantine tables can store rejected records for investigation.
6. How database transactions help protect data during pipeline failures.
7. How automated tests help verify application behavior.
8. Why technical documentation and reconciliation are important.

## 7. My Approach to AI-Assisted Development

I used ChatGPT as a learning and development assistant throughout this project.

When I encountered a new concept or technical issue, I asked questions, reviewed the suggested approach, implemented changes, and checked the results in my local environment.

I also recognize that AI-generated suggestions may contain mistakes. Therefore, I used execution results, database inspection, and automated tests to validate the behavior of the application.

I understand that I am responsible for the submitted solution and should be able to explain its architecture, code, design decisions, testing approach, and limitations.

## 8. Disclosure

This document is a summary of the main AI-assisted development discussions. The prompt examples are reconstructed summaries, not a complete verbatim conversation export.

No confidential assessment instructions, private recruitment emails, or assessment attachments are reproduced in this document.