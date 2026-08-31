# Portfolio Redesign Brief

**Status:** Approved for implementation

**Recorded:** August 31, 2026

## Goal

Present Igor as a **Senior Backend & Data Engineer** who owns production systems end to end and applies mature backend
engineering discipline to emerging AI applications. The site must let a recruiter understand the role, credibility, and
relevance quickly, then let a senior engineer inspect the underlying decisions and evidence.

The intended market includes both startups and larger enterprises. The site must communicate reliability, maintainability,
and operational ownership without tailoring the entire identity to big pharma or claiming regulated-industry experience.

## Success Criteria

- Within 30 seconds, a recruiter can identify the target role, production scope, three strongest examples, and hiring actions.
- A technical reviewer can find constraints, individual responsibility, architecture, tradeoffs, validation, outcomes, and
  limitations for every featured case.
- Production work is credible but anonymized. Exact and approximate metrics are distinguishable.
- AI-assisted engineering is presented transparently as a controlled workflow with human review and accountability.
- English and Russian interface navigation works consistently without suggesting that every article has been translated.
- The design feels deliberate and technically literate without resembling a template, fake terminal, or decorative dashboard.

## Non-Goals

- Positioning Igor as Staff, Principal, engineering manager, or experienced technical team lead.
- Claiming production-proven AI specialization, pharma specialization, or formal regulatory expertise.
- Giving every historical project equal prominence.
- Rewriting or translating the complete blog during the redesign.
- Building a single-page application or introducing a frontend framework solely for visual effects.
- Using inflated marketing language where the evidence supports only a narrower claim.

## Locked Direction

1. **Primary identity:** Senior Backend & Data Engineer.
2. **AI positioning:** A prominent developing specialization grounded in backend, security, and systems thinking.
3. **Audience order:** Recruiters first, with progressive technical depth for senior engineers.
4. **Market:** Company-size agnostic, from startups to enterprises.
5. **Role:** Hands-on senior individual contributor with end-to-end ownership.
6. **Leadership:** More than ten years of prior nontechnical people management is supporting context, not a claim of
   engineering-team leadership.
7. **AI workflow:** Transparent and accountable AI-assisted engineering. Agents generate most code and tests; Igor sets
   direction, weighs tradeoffs, reviews every line, demands explanations, and owns the result.
8. **Private evidence:** Anonymized professional systems may be used after disclosure review.
9. **Visual direction:** Editorial Industrial, implemented initially with Tailwind CSS through the CDN script in `<head>`.
10. **Featured proof:** Two anonymized production cases followed by Dux.
11. **Information architecture:** Focused homepage with dedicated case-study pages.
12. **Voice:** Strong technical-human voice, with more opinionated framing reserved mainly for articles.
13. **Language:** Bilingual shared interface, with English as the canonical technical-content language.
14. **Conversion:** Evidence first. Featured case studies are primary; resume and contact are secondary actions.
15. **Selected concept:** Signal Ledger, as defined by the three final HTML references and visual implementation guide.

## Information Architecture

### Global navigation

- **Work:** Homepage featured-work section or case-study index.
- **Blog:** Existing blog index.
- **About:** Compact professional biography and operating principles.
- **Resume:** Direct document action, visible without dominating the page.
- **Contact:** Persistent but visually secondary.
- **EN/RU:** Clear language control for translated interface pages.

Keep the navigation shallow. GitHub and LinkedIn belong in the header utility area or footer, not as competing primary
destinations.

### Homepage sequence

1. **Hero:** Name, Senior Backend & Data Engineer label, concise outcome-oriented positioning, primary `View selected work`
   action, secondary resume action.
2. **Credibility strip:** A few defensible signals such as production ownership, data volume, database footprint, and
   orchestration scope. Avoid animated counters.
3. **Featured work:** Three persistent, text-led cards in this order:
   - Production Data Platform
   - Internal Platform Ownership
   - Dux, a Constrained NL2SQL Agent
4. **Working with coding agents:** A compact explanation of planning, implementation, review, and verification.
5. **Engineering focus:** Backend systems, data platforms, reliability, and guarded AI applications expressed through
   capabilities and outcomes rather than a logo wall.
6. **Featured articles:** Up to three published posts selected in Django admin, followed by recent posts when fewer than
   three have been selected.
7. **About me:** Stable professional focus and concise prior management context, without a fixed experience counter or
   current-employer status in the headline copy.
8. **Contact:** Low-friction invitation after evidence has been established.

The homepage must remain understandable if a visitor never opens a case study. Each card therefore includes the problem,
scope, role, and outcome, not just a title or image.

The operating-scale panel uses the general label **Database footprint** rather than tying the headline metric to one database
product. Supporting copy and case studies may still name ClickHouse where the technology is relevant.

### Blog index

Use the same header, paper grid, type hierarchy, signal color, rules, and interaction style as the homepage. Keep the index
to one article ledger: featured posts are pinned and marked, followed by the remaining posts in reverse publication order.
Do not duplicate featured posts in a second archive list. Each row contains publication date, title, short description,
optional tags, and a clear link target. Filtering and search are unnecessary until the archive is large enough to need them.

### Blog articles

Article pages keep the shared navigation and identify the section with the **IGOR SIMBIRTSEV / BLOG** section wordmark. Use a
restrained article header with publication date, optional tags, title, and short description. Keep body copy in a narrow
reading column, while headings, code, lists, figures, and captions retain the Signal Ledger rules and signal color.

Do not repeat the header metadata in a separate body rail. Code and diagrams may scroll inside their own bounded containers;
the page itself must never scroll horizontally. Do not add a table of contents until Markdown headings have stable link
targets. The reading column aligns with the left edge of the shared page grid instead of floating in the center. End with
simple article navigation on the same reading-column axis and one site footer.

### Case-study pages

Use the same narrative structure for all three cases:

1. Executive summary and business outcome
2. Metadata: role, system type, status, scale, and technology
3. Context and problem
4. Constraints and failure modes
5. Individual responsibility and collaborators
6. Architecture and data flow
7. Important decisions, alternatives, and concessions
8. Reliability, security, testing, and operations
9. Outcome with measurement qualifiers
10. Limitations, lessons, and next improvements
11. Public source or related writing where available

Call these **Engineering Case Studies** publicly. "Architectural war stories" may guide drafting, but should not become the
site taxonomy.

## Featured Evidence

### Production Data Platform

Lead with ingestion, ClickHouse, Airflow, operational reliability, and the business need served. Establish what Igor
personally designed, changed, operated, and supported. Use safe aggregate scale only. Do not expose company identity,
customer information, supplier identities, schemas, endpoints, credentials, or sensitive business rules.

### Internal Platform Ownership

Show the breadth and constraints of owning a business-critical internal platform. The present sole-developer context may be
stated inside the case because it explains the decisions, but it should not become the site's general identity. Focus on
prioritization, stakeholder communication, automation, maintenance, incident response, and tradeoffs under limited
capacity. Do not turn sole ownership into an unsupported claim that a larger team was led.

### Dux

Use Dux as inspectable evidence for guarded AI application design. Emphasize deterministic authority boundaries,
allowlisting, exact-query validation, short-lived one-time capabilities, backend-owned result rows, conservative routing,
and extensive tests. State limitations directly, including the lack of external production evidence and opportunities for
stronger database-level read-only enforcement.

Older work can appear in a compact archive, GitHub link, or resume. It must not compete with these three cases on the
homepage.

## Content and Voice Rules

- Start with the real outcome, then progressively reveal technical detail.
- Use concrete verbs and precise nouns. Prefer "reduced greeting requests from about 1,300 to about 72 tokens" over
  "eliminated systemic waste at scale."
- Label estimates with `approximately`, `about`, or a range. Do not present inferred business impact as measured impact.
- State role and team context explicitly for every case.
- Include rejected alternatives and limitations when they materially explain engineering judgment.
- Keep primary pages direct, candid, and professionally restrained. Dry humor is acceptable when it does not obscure meaning.
- Articles may be faster, sharper, and more opinionated for a technically experienced, skeptical audience. Strong positions
  still require evidence. Do not imitate another creator's vocabulary or manufacture controversy.
- Describe AI use once, in the About or working-principles material. Frame it around review gates, comprehension, and
  accountability rather than the percentage of code generated.
- Keep homepage copy durable. Avoid fixed experience counters, current-assignment labels, and employer circumstances that
  can make the design stale after a job change.

The coding-agent workflow uses short statements that identify responsibility before the explanation: **I plan**, **We
brainstorm**, **AI implements**, **We review**, and **I verify**. The review step states that a separate reviewer agent checks
the implementation before Igor reviews it himself.

## Visual System

The interface uses the final Signal Ledger system documented in [`prototypes/README.md`](prototypes/README.md):

- Warm paper canvas, deep ink text, muted green-grey secondary text, and one restrained orange signal color.
- Strong typographic hierarchy with readable body copy and compact monospaced metadata labels.
- Thin rules, measured grid lines, and modular case-study blocks that encode real relationships.
- Architecture diagrams share the same line weights, labels, spacing, and signal color as the page UI.
- Case cards use one consistent surface and expose titles and metadata persistently. Images and hover effects are supporting
  elements only.
- Personal photography is secondary and intentional. It must not dominate the professional narrative.
- Motion is limited to orientation and feedback. Respect `prefers-reduced-motion`.
- Dark styling may be used selectively, but a cyberpunk, terminal, neon, or fake-observability aesthetic is prohibited.

Tailwind CSS should initially be loaded from its CDN script so the first implementation does not add build tooling. Keep
design tokens and repeated utility groups organized so migration to a compiled Tailwind setup remains straightforward if
the site later needs production optimization or stricter asset policies.

The thin dark labels at the very top of the HTML references identify prototype pages. They are not part of the production
design and must not be implemented.

## Templates and Data Flow

Retain server-rendered Django templates and the existing locale middleware. The first implementation should introduce
small native `{% include %}` partials where markup is genuinely repeated:

- global header, navigation, language control, and footer;
- featured-case card and case metadata;
- article card;
- form-status messages.

Keep the hero, credibility section, architecture diagrams, and other one-off sections in their page templates.

The request flow remains simple: Django resolves locale for translated core routes, renders structured portfolio content,
and links to dedicated case-study templates. The existing blog continues to serve stored Markdown as rendered HTML. No
client-side application state is required.

The homepage article cards come from published `Post` records. Admin-managed featured state and priority determine the first
choices; recent published posts fill empty positions. Optional summaries and tags control card presentation. When a summary
is absent, use a short plain-text excerpt derived from rendered HTML.

Case-study content must have a single authoritative representation. During implementation, choose either structured Django
records or clearly structured templates based on how often content will change. Do not maintain duplicate facts in cards and
detail pages without a shared source.

## Language Behavior

- English is the default and canonical professional language.
- Shared navigation and interface text have English and Russian translations.
- Core translated pages preserve the visitor's selected locale.
- An article remains English-only until an actual Russian version exists.
- If a translation is unavailable, do not show a misleading locale link to a blank page or 404. Keep the English article
  available and label its language clearly.
- When translated article versions are introduced, link them explicitly as equivalents and provide correct canonical and
  alternate-language metadata.
- Missing translation strings must fall back visibly and safely to English, never to an empty label.

## Failure States and Edge Cases

- **Confidential case content:** Omit or generalize unsafe details. A weaker truthful statement is preferable to an impressive
  disclosure risk.
- **Unverifiable metric:** Mark it approximate, explain the measurement basis internally, or remove it.
- **Missing article translation:** Serve the English article with an honest language label.
- **Missing resume:** Hide the action rather than linking to an absent or obsolete file.
- **External project unavailable:** Preserve the case narrative and label repository or demo status accurately.
- **Contact delivery failure:** Preserve entered form data, show an actionable error, and provide a direct email alternative.
- **No JavaScript:** Navigation, case content, language links, resume, and contact information remain usable.
- **Small screens:** Metadata and architecture blocks reflow without horizontal page scrolling; diagrams may use a clearly
  bounded internal overflow region only when unavoidable.
- **Long technical content:** Maintain readable line length, visible section hierarchy, and anchored navigation where useful.

## Validation Requirements

- Test all primary pages in English and Russian, including locale persistence and untranslated-article behavior.
- Verify keyboard navigation, visible focus, heading order, landmarks, link names, contrast, and meaningful image alternatives.
- Confirm featured-case summaries and detail pages do not contradict each other.
- Review every private case against a disclosure checklist before publication.
- Proofread all English and Russian interface copy independently.
- Verify responsive layouts at phone, tablet, laptop, and wide desktop sizes.
- Check contact success and failure paths, missing-resume handling, 404 behavior, metadata, sitemap entries, and canonical URLs.
- Run Django's focused tests and system checks, then perform a production-like page and asset smoke test.

## Content Boundaries During Implementation

- The homepage, blog index, and article detail references contain the approved initial interface copy and hierarchy.
- The aggregate metrics shown there are the current approved public values: more than 10 million ingested rows per day,
  approximately 3.6 TB of database data, and approximately 15 Airflow DAGs.
- Dedicated pages for the two private case studies still require disclosure-safe source material. Do not invent details or
  ship dead `#` links. Hide unavailable case-study actions until a real route exists.
- Reuse the existing English and Russian resume assets, selecting one canonical copy of each during implementation.
- Preserve the existing contact destination unless Igor explicitly changes it.
- Do not invent architecture screenshots or diagrams. Implement only publishable material already supplied.

Any future change to the primary identity, audience order, proof portfolio, language strategy, or visual tokens should be
recorded here explicitly rather than introduced silently during implementation.
