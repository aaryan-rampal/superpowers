---
name: frontend-design-cosmos-explorer
description: Use when creating or editing Avalonia AXAML frontend views in Cosmos Explorer plugins or core app windows, especially when consistency with shared styles, docking patterns, typed bindings, and theme resources matters.
---

# Frontend Design Skill (Cosmos Explorer AXAML)

Use this when creating or editing Avalonia `.axaml` UI in Cosmos Explorer (core app and plugins).

## Intent

Keep UI consistent with existing Cosmos patterns while allowing documented exceptions when plugin-specific constraints require them.

Rule levels:
- **MUST**: required for consistency and safety.
- **SHOULD**: preferred; deviate only with a short rationale.

## Workflow

1. Check whether a shared view already exists in `CosmosPluginShared` before adding plugin-specific UI.
2. Start from existing layout and style patterns used in similar views.
3. Implement with typed bindings and theme resources.
4. Run quick verification (compile bindings plus light/dark sanity pass).
5. If deviating from conventions, document why in PR or notes.

## MUST Rules

- Use `x:DataType` on root views for compile-time binding safety.
- Include `Design.DataContext` for designer support.
- Prefer `DynamicResource` theme keys (no inline colors or brushes).
- Reuse shared style classes where applicable:
  - `content_layout`
  - `content_expander`
  - `top_panel_button`
  - `vertical_seperator` (repo spelling)
  - `viewable_disable`
- Preserve docking and shell conventions when touching main app docking views.
- Use command bindings instead of code-behind click logic where practical.
- Prefer existing converters and patterns (`BoolConverters`, enum display patterns) over ad-hoc logic.

## SHOULD Rules

- Follow common toolbar/content split (`RowDefinitions="60,*"`) when building tool-style views.
- Use existing icon composition pattern (Material icon plus label in horizontal button content).
- Use ancestor bindings in templates when child controls need parent VM context.
- Use lifecycle trigger patterns (`AttachedToLogicalTreeTrigger` and existing behavior style) where already established in that feature area.
- Keep new styling semantic and class-based; avoid one-off visual tweaks.

## Peculiar Repo Conventions (Important)

- `vertical_seperator` is intentionally spelled this way in existing styles.
- Toolbar buttons are typically class-driven (`top_panel_button`) with icon+text structure.
- Content wrappers commonly use `content_layout` plus bordered/padded body.
- Expanders usually use `content_expander` rather than default Expander visuals.
- Theme behavior depends on resource dictionaries from `Themes.axaml` and shared styles in `DefaultStyle.axaml`.

## Don't

- Do not hardcode brushes or colors in controls.
- Do not duplicate shared plugin UI that already exists in `CosmosPluginShared`.
- Do not introduce new icon sizing/style patterns if repo classes already cover the use case.
- Do not skip typed bindings on new views.
- Do not mix inconsistent layout patterns in the same feature without reason.

## Verification Checklist

- Build passes with typed bindings intact.
- View looks acceptable in both light and dark themes.
- New and changed controls use existing classes/resources where expected.
- Shared-view reuse was considered.
- Any convention deviation is documented with rationale.
