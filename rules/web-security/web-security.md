# Web Security Rules

For browser-facing and HTTP-server code. General security rules live in `universal-coding-security.md`.

## Output

- MUST sanitize user input before rendering
- MUST NOT use `innerHTML` or equivalent (`set:html`, `dangerouslySetInnerHTML`) with user-supplied content

## Content Security

- Be aware of CSP headers — framework-specific header configuration stays in framework rules
- MUST NOT disable or weaken existing security headers without justification
- Client-side scripts MUST NOT fetch or eval external code from untrusted sources
