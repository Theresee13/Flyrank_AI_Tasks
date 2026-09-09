# Contributing and Verification Notes

This repository is organized as a portfolio of small, independently runnable projects. Changes should stay close to the project they improve and should preserve the documented API contracts.

## Before making a change

1. Read the README in the target project.
2. Check its dependency file and `.env.example`.
3. Keep credentials, local databases, generated reports, and build output out of version control.

## Validation

Use the project’s existing test command when one is provided. For documentation-only changes, check Markdown links and confirm that commands match the current folder names. When a change requires a live service or external account, record the real result in the project README rather than inventing output.

## Pull requests and commits

Keep commits focused and describe the user-visible or operational result. Include the command used for verification and call out any local services or credentials that were required.
