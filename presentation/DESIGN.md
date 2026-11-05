# DESIGN — 9Router Wolfi evidence deck

## Surface and intent

Read / speaker-led presentation in Vietnamese. Preserve the existing ivory, teal and ochre identity and embedded Be Vietnam Pro font. Revise evidence and narrative rather than rebrand. The audience should distinguish packaging success, observed size, compatibility coverage and security findings.

## Flow

20 slides: Alpine→Wolfi thesis; version boundaries; filesystem layers; deletion; COPY order; two cache types; multi-stage; base choice; minimum runtime; pinned inputs; completed Grype scan; smoke coverage; optional isolated security review; pipeline; initial evidence table; layer breakdown; old Grype findings; removal of separate Next COPY; completed new run; next experiment.

Keep the original first fifteen slide positions where possible; slides 11 and 14 now acknowledge scan execution on 0.4.41. Slide 15 is initial evidence, explicitly not the latest build. Slides 18–19 explain the newer run. Source main 0.5.112 remains separate.

## Tokens

- Stage: 1920×1080, uniform scale, centered letterboxing.
- Canvas #f8f6f1; viewport #e8e5dd; ink #252827.
- Teal #326878; dark teal #264f5b; ochre #805a27 for added conclusions, existing accent #a37332 retained.
- Table header field #e5ebe7; separators #c8cbc2; secondary text #555e58.
- Embedded Be Vietnam Pro, existing Deck family; no remote fonts or network dependencies.
- Titles 90px, tracking -3px; body 32px; lead 43px; tables 29px; notes 24px; footer 19px.
- Slide inset 110px; evidence body top 315px and bottom 135px. Table cells 15px vertical / 24px horizontal. Rhythm 24/28/42px.
- Tables and short process rails, no decorative metric cards. Labels and text carry meaning independently of color. Severity uses explicit text, not red/green safety inference.

## Responsive and interaction

Fixed 16:9 canvas at desktop and phone, never reflow slide contents. Phone is a fit-to-width preview and requires landscape/zoom for dense tables. Controls remain outside stage. Prev/next, keyboard arrows, Page keys, Home/End, wheel and swipe supported. Hash selects slide. E toggles editing, Ctrl/Cmd+S downloads a new HTML copy; edits are not written back to disk automatically. No autosave guarantee.

## Accessibility

Semantic tables with column/row headers. Inactive slides inert and aria-hidden. Buttons have names and disabled edge states; visible teal focus, minimum control size 40px. Selection is themed. Reduced motion removes transitions/entrances. Existing diagrams remain SVG with labels. Important caveats are visible, not only in hidden notes. Mobile preserves geometry rather than promising reading comfort.

## Loading, empty, errors

Offline deck has no runtime fetch/loading state. Embedded font is awaited by verification. Unknown/unmeasured data says chưa đo/chưa benchmark, not zero. Missing upstream local size stays explicitly unavailable; no fabricated chart values. Artifact/report failures must be reported and source labels retained. No external renderer or active scan is invoked by this deck. No Impeccable engine, hooks, launcher or detector was run; manual-context fallback was used.

## Verification actually performed

Chromium rendered all 20 slides at 1280×720; DOM bounds and evidence body overflow checks found no issues after adjustment. No JS errors, no HTTP dependencies. Stage ratio verified at 1920×1080 and 390×844. Home/Right/End/clamp, prev/next and edit toggle exercised. Final rendered slides 15, 18 and 19 visually reviewed via vision; slide 17 and phone viewport visually reviewed before final minor content update. Full-deck visual signoff is not claimed. Save/download, swipe/wheel, screen-reader output, PNG/PDF export and browser compatibility were not fully tested.

## Handoff

Entry: /mnt/c/Users/taint73/Documents/Projects/DockerFile-Contest/presentation/9router-proposal.html
Validation: validation-updated.json. Screenshots: screenshots-updated/.
Evidence: evidence/, including original ZIPs, parsed Grype reports and API snapshots. Previous deck/notes/source snapshot preserved in archive-before-evidence-update/.
