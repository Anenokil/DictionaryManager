# Commit convention

Based on [Conventional Commits](https://www.conventionalcommits.org/).

Format: `type(scope): description`

The scope is optional.

## Types

| Type | Use for |
|---|---|
| feat | new functionality |
| fix | bug fixes |
| perf | performance improvements |
| ui | visual-only changes to the GUI (custom type) |
| refactor | internal changes without behavior change |
| build | dependencies and build system (Pipfile, PyInstaller spec) |
| ci | CI configuration (GitHub Actions workflows) |
| docs | documentation only (README, docstrings, comments) |
| test | tests |
| chore | everything else (configs, tooling) |

Use `ui` only when the appearance changes and nothing else does (styles,
displayed text, layout). If a visual change comes with new functionality
or fixes incorrect behavior, use `feat` or `fix` instead.

Correcting typos and grammatical errors in displayed text is a `fix`, not `ui`.
Rewording text that was correct (for clarity or style) is still `ui`.

## Scopes

A scope names the area of the project the change belongs to. It can be:

- **a module or class**: `DctBundle`, `ChoiceDialog`, `gui_v2`.
- **a feature area**: `search`, `menus`, `topics`.
- **a technical domain**: `i18n`, `deps`.

class names as in code, everything else lowercase.

Examples:

```
feat(search): add Reset Settings button
feat(topics): add "At a Glance" help topic
fix(menus): disable menu options when no items selected
ui(PracticeConfigPage): display tags in alphabetical order
build(deps): split Pipfile dependencies into per-GUI categories
chore: ignore compiled Qt translation files (*.qm)
```

Rules of thumb:

- Pick the name a reader would most easily recognize. If a change touches
  several classes that belong to one feature, use the feature name.
- **Omit the scope** when the change is cross-cutting (touches many unrelated
  areas) or concerns the repository as a whole.
- Reuse existing scopes instead of inventing near-duplicates
  (`search`, not `searching` or `search-ui`).

## Breaking changes

Mark with `!` after the type/scope and explain in a `BREAKING CHANGE:` footer
when old data files stop working without migration, or functionality is removed.

Internal signature changes with all call sites updated are NOT breaking.

If a data format changes but a migration opens old files correctly, the change
is NOT breaking. Dropping support for an old format version (removing its
migration) IS breaking.

## Rules

- Imperative mood; start with a lowercase letter, except for names of UI
  elements, code identifiers, and proper names
  (`Reset Settings`, `DctBundle`, `"At a Glance"`, `Pipfile`).
- No trailing period.
