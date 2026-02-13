# Security Rules

## Secrets

- MUST NOT commit secrets, API keys, or credentials
- Use `.env` files, never tracked in source control
- `.env` MUST be in `.gitignore`

## Dependencies

- MUST NOT add dependencies without justification
- Audit new dependencies: check maintenance status, download count, known vulnerabilities
- Run `npm audit` periodically
- Prefer existing dependencies over adding new ones

## Input & Output

- MUST sanitize user input before rendering
- MUST NOT use `innerHTML` or equivalent (`set:html`, `dangerouslySetInnerHTML`) with user-supplied content
- Validate at system boundaries (user input, external APIs)

## Content Security

- Be aware of CSP headers — framework-specific header configuration stays in framework rules
- MUST NOT disable or weaken existing security headers without justification
- Client-side scripts MUST NOT fetch or eval external code from untrusted sources

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
