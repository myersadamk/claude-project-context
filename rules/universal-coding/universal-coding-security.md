# Security Rules

## Secrets

- MUST NOT commit secrets, API keys, or credentials
- Use `.env` files, never tracked in source control
- `.env` MUST be in `.gitignore`
- MUST NOT log secrets, tokens, or credentials

## Dependencies

- MUST NOT add dependencies without justification
- Audit new dependencies: check maintenance status, download count, known vulnerabilities
- Run the ecosystem's audit tool periodically (`npm audit`, `pip-audit`, `dotnet list package --vulnerable`)
- Prefer existing dependencies over adding new ones

## Input

- Validate at system boundaries (user input, files, external APIs)
- MUST NOT build shell commands or queries by concatenating untrusted input; pass arguments as a list or use parameters
- MUST NOT deserialise untrusted data with formats that can construct arbitrary types (`pickle`, `BinaryFormatter`, unsafe YAML loaders)
- MUST resolve file paths built from untrusted input and check they stay inside the intended directory

## Full Security Audits

Use the `vibesec` skill for changes that add:
- Server-side rendering or API routes
- Authentication or session handling
- Form handling or file uploads
- External service integrations

The `vibesec` skill covers OWASP top 10, dependency analysis, and
framework-specific attack vectors.

If the vibesec skill is not available, manually review OWASP top 10
considerations for the change.
