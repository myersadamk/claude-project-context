# CPC Roadmap

Future evolution of the cpc architecture, captured during the Java/Spring Boot rules design (2026-03-23).

## 1. Rules → Skills Migration

Decompose flat rule files into on-demand skills across all profiles (not just Java). Each concern becomes invocable and doubles as a reviewer agent. Rules become lean "always-on" fundamentals only. This addresses the context bloat problem: investigative or debugging conversations shouldn't pay the cost of loading coding standards.

## 2. Dispatchable Agents

Define custom agent archetypes (coding, reviewing, designing) that draw from the same best-practice knowledge base. Examples: `failure-mode-review-agent` dispatched during planning, `concurrency-review-agent` dispatched during code review. Agents can be composed during planning to debate and stress-test designs from multiple angles.

## 3. JDK Feature Dictionary

Version-indexed catalog of idioms and patterns. Skills for auditing a codebase against its target JDK version and suggesting modernization (e.g. upgrading deprecated concurrency patterns, adopting newer language features).

## 4. Session Continuity

Team-oriented session handoff and context persistence. Needs ecosystem research to understand how this would work across a team using Claude Code — particularly around shared state, session history, and handoff protocols.

## 5. Context-Aware Loading

Path-based or intent-based rule activation so conversations that aren't about writing code (investigation, debugging, architecture discussion) don't load the full coding standards into the context window.
