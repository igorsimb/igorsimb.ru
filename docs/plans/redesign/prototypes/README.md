# Visual Implementation Guide

**Status:** Final design reference. Implement this direction only.

## Reference Pages

- [Homepage](homepage.html)
- [Blog index](blog-index.html)
- [Blog article](blog-article.html)

The HTML files are visual references, not production templates. Replace placeholder links with Django URLs and translated
strings. The narrow dark strip above each sticky header labels the prototype and must not appear on the production site.

## Design Tokens

- Canvas: warm paper `#f2efe8`.
- Primary text: deep ink `#17201d`.
- Secondary text: muted green-grey `#66706b`.
- Signal color: restrained orange `#db5b2b`.
- Rules: `#cfcac0`, normally one pixel.
- Secondary surface: `#e9e5dc`; dark sections use `#17201d`.
- Grid texture: 32px square grid using ink at roughly 4.5% opacity.
- Sans stack: Arial, Helvetica, sans-serif. Monospace stack: Consolas, Courier New, monospace.

Use the orange for orientation, active states, and small emphasis. Do not turn it into a large decorative background except
for the final homepage contact band already shown in the reference.

## Shared Layout

- Main page grid: maximum width 1440px.
- Standard section content: maximum width 1360px.
- Horizontal page padding: 20px on small screens and 40px on desktop when the max-width grid does not provide a margin.
- Navigation remains sticky, conventional, and visually quiet. Blog pages use the section wordmark
  **IGOR SIMBIRTSEV / BLOG**. Do not append `ARTICLE` or the article title.
- Keep thin rules and square corners. Avoid shadows except the deliberate offset hover shadow on homepage case cards.
- Motion is limited to hover feedback and must respect `prefers-reduced-motion`.
- The real mobile header needs an accessible navigation control. The prototypes hide desktop navigation below `md` but do
  not specify the final mobile-menu interaction.

## Homepage Rules

- Desktop hero grid: 84px vertical label rail, flexible content column, 380px operating-scale panel.
- Keep the complete hero statement and both actions visible at a 1440x800 viewport.
- The scale panel says **Database footprint**, with ClickHouse named only in supporting technical content.
- All three case-study cards use the same `#e9e5dc` surface. Their hierarchy comes from copy and metadata, not different
  colors.
- The coding-agent workflow remains a dark section with the scan labels **I plan**, **We brainstorm**, **AI implements**,
  **We review**, and **I verify**.
- Homepage articles come from Django data. Do not hard-code the three visible posts from the prototype.

## Blog Index Rules

- Use one article ledger. Featured posts are pinned and marked with a small orange signal; other posts follow by publication
  date.
- Do not repeat featured posts in another archive, add an explanatory sorting label, or add a promotional section above the
  footer.
- Each row exposes date, title, summary, optional tags, and a clear link target.
- Search and filtering are out of scope until the archive is large enough to need them.

## Article Rules

- Header metadata appears once: date, optional tags, and an optional related-project link.
- The TL;DR block is visually distinct but remains inside the article header.
- Body width is 880px. Anchor its left edge to the left edge of the shared 1440px page grid; do not center the reading column
  independently.
- The empty space to the right is intentional. It protects readable line length and gives the page an editorial,
  asymmetrical composition. Do not fill it with decorative panels or widen prose to occupy it.
- Align the header's **← All articles** link to the body’s left edge. In the ending navigation, the back link starts on that
  same edge and the next-article title ends on the body’s right edge.
- Code and wide diagrams scroll inside bounded containers. The page itself must never scroll horizontally.
- Do not add a table of contents until rendered Markdown headings have stable IDs.
- End with compact article navigation and then the single shared site footer.

## Responsive and Accessibility Requirements

- Preserve the desktop alignment system while collapsing rails and columns into one reading path on small screens.
- Keep headings, tags, code, and diagrams inside the viewport. Mobile side padding is 20px.
- Maintain visible focus, semantic landmarks, logical heading order, descriptive link text, and sufficient contrast.
- The design must remain usable without JavaScript except for the explicitly interactive mobile navigation and language
  control.
