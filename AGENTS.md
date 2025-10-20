# Repository Guidelines

This repository automates applying to Airbus roles on Workday via Selenium. Use these guidelines to extend the agent safely and keep the automation reliable.

## Project Structure & Module Organization
- `main.py` coordinates Selenium sessions, delegates to page objects, and records outcomes in `succ_links.txt` and `missed_links.txt`.
- `app/config.py`, `app/driver.py`, `app/pages.py`, and `app/ux.py` hold configuration dataclasses, Chrome driver setup, page flows, and interaction helpers respectively; keep new logic within these modules to preserve single responsibilities.
- `link_getter.py` (expected in the repository root) should expose `get_links()` returning iterable job URLs; stub or mock it when developing locally.
- `old/` contains legacy scripts kept for reference only—do not modify without a migration plan.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` sets up an isolated environment.
- `python -m pip install selenium` installs the runtime dependency; add extra packages to `requirements.txt` if adoption grows.
- `python main.py` launches the automation using the profile defined in `SeleniumConfig`.

## Coding Style & Naming Conventions
- Use 4-space indentation, `snake_case` for functions, and `PascalCase` for classes to match existing modules.
- Keep configuration values in frozen dataclasses (`app/config.py`); pass them into helpers instead of relying on new globals.
- Store XPaths and CSS locators in `path.py` (same directory as `main.py`) to keep selectors centralized; name constants in all caps.
- Run `python -m black app main.py` before committing once a formatter is adopted; avoid mixing trailing commas or ad-hoc formatting.

## Testing Guidelines
- Add `pytest` tests under `tests/`, mirroring the module tree (e.g., `tests/test_pages.py`) and naming functions `test_*`.
- Mock Selenium drivers to keep tests deterministic and require `python -m pytest` to pass before opening a pull request.

## Commit & Pull Request Guidelines
- Follow the existing log pattern: concise, imperative subject (`Refactor Selenium automation scripts`) with optional context after a colon.
- Each PR should summarise the change, list manual test runs, and link relevant issues or job IDs; attach console snippets when automation output changes.
- Rebase over `main` before review and keep diffs focused—split behavioural and housekeeping changes into separate commits.

## Security & Configuration Tips
- Never commit personal credentials or Workday identifiers; rely on the profile directory referenced in `SeleniumConfig`.
- Validate new locators against both logged-in and guest flows, and document required browser settings in the PR description.
