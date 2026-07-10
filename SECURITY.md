# Security Policy

## Supported Versions

Security fixes are provided for the latest released version of this package.

The supported Nautobot and Python version ranges are documented in `pyproject.toml` and `README.md`.

## Reporting a Vulnerability

Do not open a public GitHub issue for suspected security vulnerabilities.

Report vulnerabilities privately through GitHub's private vulnerability reporting feature if it is enabled for the repository. If private reporting is not available, contact the repository owner privately before publishing details.

Please include:

- affected package version or commit
- Nautobot version
- Python version
- description of the issue
- reproduction steps
- potential impact
- any known mitigations

## Scope

This project is a Nautobot app. It relies on Nautobot and Django for authentication, authorization, request handling, and core platform security controls.

Security reports are in scope when they affect this app's:

- object permission enforcement
- REST API behavior
- job behavior
- assignment or schedule validation
- package distribution integrity

General Nautobot, Django, database, or deployment vulnerabilities should be reported to the relevant upstream project unless this app introduces the vulnerable behavior.
