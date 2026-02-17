# Kimi SDD Review Report

## Summary
- **Confidence level:** 65%
- **Critical gaps:** 12
- **Major issues:** 15
- **Minor issues:** 11

---

## Critical Gaps (Block Implementation)

### 1. Missing Trello Card Files (Cards 03-07, 09-15, 16-20)

**Location:** `/home/pets/temp/jsonl_dashboard/docs/sdd/artifact-nexus-sdd/trello-cards/`

**Issue:** BOARD.md references 22 cards, but only 5 card files exist (01, 02, 08, 21, 22). Cards 03-07, 09-15, and 16-20 are missing entirely.

**Impact:** Cannot execute implementation as specified. Cards 03 (DatabaseManager), 04 (Static Layout), 05-07 (UI Components), 09-11 (Parsers), 12-15 (Scanner/Watcher/Filter), and 16-20 (Cognitive Engine) have no implementation instructions.

**Fix Required:** Generate all missing card files with same level of detail as existing cards.

---

### 2. No Error Handling Strategy for Parser Failures

**Location:** `requirements.md` Section 1.2, `08-codex-parser.md`

**Issue:** The parsers assume well-formed JSONL/JSON files. No handling for:
- Corrupted files (partial writes, truncated JSONL)
- Malformed JSON syntax
- Missing required fields
- Encoding issues (non-UTF8 characters)
- File permission errors

**Impact:** Watcher service will crash or skip sessions silently when encountering bad data.

**Fix Required:** Add try/except blocks with error logging. Define behavior: skip file? mark as "parse_error"? alert user?

---

### 3. Cognitive Router Has No LLM Implementation Details

**Location:** `requirements.md` Section 5, `CARD-17` (missing file)

**Issue:** The CognitiveRouter is central to the product but:
- No prompt templates defined for cross-session queries
- No token counting strategy before API calls
- No context window size handling per model
- litellm configuration not specified
- No rate limiting strategy beyond fallback

**Impact:** Card 17 cannot be implemented without guessing the LLM integration details.

**Fix Required:** Create CARD-17 with prompt templates, token counting logic, and litellm configuration examples.

---

### 4. Session Summary Generation Is Underspecified

**Location:** `requirements.md` Section 2.2, `08-codex-parser.md`

**Issue:** Summary format specified as `[ACTION] Brief description | Files: file1.py, file2.js | Status` but:
- No algorithm for extracting "action verb" from prompts
- No handling for prompts without clear verbs
- File extraction regex is naive (won't catch paths with spaces, nested paths)
- No character limit for summary field (database schema has no MAXLENGTH)

**Impact:** Summaries will be inconsistent, potentially very long, breaking UI layout.

**Fix Required:** Define summary generation algorithm with fallbacks. Add character limit (e.g., 200 chars).

---

### 5. Watcher Service Has No State Tracking

**Location:** `requirements.md` Section 1.3, `CARD-13` (missing)

**Issue:** Watcher polls every 30s but:
- No tracking of which files have been processed
- No handling for file modifications (append-only assumed, but what if file changes?)
- No mechanism to detect "new" sessions vs "updated" sessions
- No reprocessing logic for failed parses

**Impact:** Same sessions may be inserted multiple times. Modified sessions won't be updated.

**Fix Required:** Add processed_files tracking (set of filepath + last_modified hash). Define update strategy.

---

### 6. Database Schema Missing Critical Indexes and Constraints

**Location:** `02-database-schema.md`

**Issue:**
- No foreign key between `cognitive_audit.session_ids` and `sessions.id` (session_ids is TEXT storing comma-separated IDs)
- No UNIQUE constraint enforcement beyond filepath
- No handling for duplicate session detection (same file, different parse)
- `start_time` and `end_time` can be NULL but are marked NOT NULL in schema

**Impact:** Data integrity issues. Cannot efficiently query audit log by session. NULL violations possible.

**Fix Required:** Redesign cognitive_audit to use junction table for many-to-many relationship. Add NULL handling.

---

### 7. Multi-Session Chat Context Assembly Not Defined

**Location:** `requirements.md` Section 3.4, `21-multi-session.md`

**Issue:** When user selects 3 sessions and asks a question:
- No specification for how contexts are combined (concatenated? interleaved?)
- No token budget allocation per session
- No handling when combined context exceeds all model limits
- No indication to user which sessions contributed to answer

**Impact:** CognitiveRouter cannot implement multi-session queries without this logic.

**Fix Required:** Define context assembly strategy. Example: "Combine sessions chronologically, allocate tokens proportionally, truncate each session equally."

---

### 8. Fallback Chain Has No Circuit Breaker

**Location:** `requirements.md` Section 5.1

**Issue:** Fallback chain retries on auth/rate-limit/timeout errors but:
- No maximum retry count per session
- No backoff strategy (immediate retry could worsen rate limiting)
- No caching of known-bad models (will retry failed model on every query)
- No user notification when fallback occurs

**Impact:** Infinite loops possible. Rate limits exacerbated. User unaware of degraded mode.

**Fix Required:** Add circuit breaker pattern. Cache failed models for N minutes. Log fallback events visibly.

---

### 9. No Authentication/Authorization for LLM APIs

**Location:** `requirements.md` Section 6.2

**Issue:** "System MUST NOT store API keys (use system credentials)" but:
- No specification for HOW to use system credentials (env vars? keyring? os-specific credential store?)
- No handling for missing credentials
- No credential rotation strategy
- litellm expects API keys in specific format

**Impact:** Cannot implement Card 16/17 without knowing credential source.

**Fix Required:** Specify credential mechanism. Example: "Read from environment variables {PROVIDER}_API_KEY or use `keyring` library."

---

### 10. TUI Layout Has No Responsive Design

**Location:** `ui-flow.md` Section 1

**Issue:** Fixed percentages (20%/45%/35%) but:
- No minimum width handling (what if terminal is 80 chars?)
- No handling for short terminals (less than 24 rows)
- No scrolling strategy for panes with overflow content
- Textual framework supports responsive layouts but not utilized

**Impact:** TUI will break or become unusable on small terminals.

**Fix Required:** Define minimum terminal size. Add responsive breakpoints. Specify scroll behavior.

---

### 11. No Session Deduplication Logic

**Location:** `requirements.md` Section 1, `CARD-12` (missing)

**Issue:** SessionScanner finds files but:
- No logic to detect if session already exists in database
- Filepath is UNIQUE but what if file moves?
- No handling for session file renames (Codex uses rollout-*.jsonl pattern)

**Impact:** Duplicate sessions in database. Orphaned records if files move.

**Fix Required:** Add deduplication by filepath + content hash. Define behavior for moved files.

---

### 12. No Health Check or Diagnostics Command

**Location:** `requirements.md`, `manual-e2e-test.md`

**Issue:** No way for user to verify:
- Watcher is running
- Database is accessible
- LLM credentials are valid
- Parsers are working

**Impact:** Debugging requires reading logs. No `nexus doctor` or `nexus status` command.

**Fix Required:** Add diagnostic CLI commands. Example: `nexus doctor`, `nexus scan --dry-run`.

---

## Major Issues (Should Fix)

### 1. Inconsistent Agent Type Naming

**Location:** `requirements.md` Section 1.2 vs `02-database-schema.md`

**Issue:** requirements.md uses "Codex, Qwen, Kimi, Gemini" (capitalized) but schema uses lowercase CHECK constraint `('codex', 'qwen', 'kimi', 'gemini', 'unknown')`.

**Fix:** Standardize on lowercase throughout.

---

### 2. Session Status Determination Is Ambiguous

**Location:** `08-codex-parser.md`

**Issue:** Status is "success" only on `task_completed` event. But:
- What if session ends without task_completed (user Ctrl-C)?
- What defines "failure" vs "interrupted"?
- No detection for error messages in assistant responses

**Fix:** Define status detection algorithm:
- `success`: task_completed event present
- `failure`: error message in assistant response, no task_completed
- `interrupted`: no task_completed, no error (abrupt end)

---

### 3. Fuzzy Search Threshold Not Configurable

**Location:** `requirements.md` Section 4.2

**Issue:** Threshold hardcoded at 60% but:
- No user configuration option
- No explanation why 60% was chosen
- May produce false positives for short queries

**Fix:** Make threshold configurable in config.yaml. Document tradeoffs.

---

### 4. No Session Content Preview in Inspector

**Location:** `ui-flow.md` Section 2 (Flow 2)

**Issue:** Inspector tabs show Details, Artifacts, Chat but no tab to view actual session content (user prompts + assistant responses).

**Fix:** Add "Transcript" tab to Inspector showing full session conversation.

---

### 5. Context Loader Strategy Is Vague

**Location:** `requirements.md` Section 5.3, `CARD-20` (missing)

**Issue:** "Load full session if tokens < limit, otherwise Heads & Tails" but:
- What is "limit"? Per-model context window?
- How to count tokens before loading?
- "Heads & Tails" (first 2 + last 2) may miss critical middle content

**Fix:** Define token limit per model. Consider smarter summarization for middle content.

---

### 6. No Handling for Very Large Session Files

**Location:** All parser cards

**Issue:** JSONL files can be hundreds of MBs (long coding sessions). Parsers read entire file into memory.

**Fix:** Add streaming parser with memory limits. Skip sessions over N MB with warning.

---

### 7. chains.yaml Schema Not Fully Defined

**Location:** `requirements.md` Section 5.2

**Issue:** Example shows `name`, `provider`, `model`, `timeout` but:
- No list of valid providers
- No timeout format specification (seconds? milliseconds?)
- No optional fields (api_key override, base_url for custom endpoints)
- No validation rules

**Fix:** Provide full YAML schema with all fields, types, and defaults.

---

### 8. No Internationalization Implementation Plan

**Location:** `requirements.md` Section 6.3

**Issue:** "MUST support Russian and English UI" but:
- No i18n framework specified (gettext? custom?)
- No translation file structure
- All UI strings in code are English

**Fix:** Add i18n card to Phase 1. Define translation file format.

---

### 9. Keyboard Shortcut Conflicts Not Addressed

**Location:** `ui-flow.md` Section 4

**Issue:** Shortcuts include `/` (search), `f` (focus filters), `c` (clear) but:
- What happens when search input is focused? Does `/` insert slash or trigger search?
- Textual has its own key bindings that may conflict
- No handling for non-Latin keyboard layouts (Russian ЙЦУКЕН)

**Fix:** Document key binding precedence. Test with Russian keyboard layout.

---

### 10. No Session Export Functionality

**Location:** `requirements.md` Section 7 (Out of Scope)

**Issue:** Session deletion is out of scope (correct), but export is not mentioned. User may want to:
- Export session to markdown
- Copy session summary
- Backup sessions

**Fix:** Consider adding export as low-priority feature, or explicitly mark as out-of-scope.

---

### 11. Database Migration Strategy Missing

**Location:** `02-database-schema.md`

**Issue:** migrate.py only creates tables. No handling for:
- Schema changes (adding columns in future versions)
- Data migration between versions
- Rollback on failed migration

**Fix:** Add version tracking table. Implement migration up/down scripts.

---

### 12. No Logging Configuration

**Location:** All cards

**Issue:** No logging strategy defined:
- Where do logs go? (stdout? file? ~/.nexus/logs/)
- What log levels? (DEBUG for dev, INFO for prod?)
- No log rotation

**Fix:** Add logging configuration to config.yaml. Create log directory.

---

### 13. Test Fixtures Not Provided

**Location:** `08-codex-parser.md` (test section)

**Issue:** Tests reference `codex_fixture_path` but no fixture files provided. No sample JSONL/JSON files for any agent.

**Fix:** Create `tests/fixtures/` with sample session files for all 4 agents.

---

### 14. No Performance Benchmarks

**Location:** `requirements.md` Section 6.1

**Issue:** Performance requirements stated (<2s launch, <500ms filter, <30s router) but:
- No benchmark test defined
- No baseline measurements
- No performance regression detection

**Fix:** Add benchmark tests to test suite. Document expected performance per card.

---

### 15. Card Dependencies Have Gaps

**Location:** `state.json`, `BOARD.md`

**Issue:** CARD-21 (Multi-Session) depends on CARD-06 (Session Card), but CARD-06 file doesn't exist. Similar gaps for other dependencies.

**Fix:** Generate all missing cards before starting implementation.

---

## Minor Issues (Nice to Have)

### 1. Inconsistent Date Format

**Location:** Multiple files

**Issue:** Dates shown as "February 17, 2026" in some places, "2026-02-17" in others, "2026-02-17T23:59:00Z" in state.json.

**Fix:** Standardize on ISO 8601 for machine-readable, locale-specific for human-readable.

---

### 2. Story Point Justification Missing

**Location:** All cards

**Issue:** Cards have story points (2 SP, 3 SP, etc.) but no explanation of estimation criteria.

**Fix:** Add brief justification or reference to complexity assessment.

---

### 3. No ASCII Art for Pipeline

**Location:** `README.md`

**Issue:** Pipeline visualization uses Unicode box-drawing characters that may not render in all terminals.

**Fix:** Provide ASCII fallback.

---

### 4. Config File Location Not Validated

**Location:** `01-project-bootstrap.md`

**Issue:** Config at `~/.nexus/config.yaml` but no check if directory exists before writing.

**Fix:** Add directory creation in bootstrap card (already present, but verify).

---

### 5. No CLI Help Text Examples

**Location:** `01-project-bootstrap.md`

**Issue:** `nexus --help` mentioned but no example output provided.

**Fix:** Add expected --help output to card.

---

### 6. Missing Card 03-07 References in KICKOFF

**Location:** `KICKOFF.md`

**Issue:** Phase 1 table lists cards 01-07 but files only exist for 01-02.

**Fix:** Generate missing files or update table.

---

### 7. No Git Repository Initialization

**Location:** `01-project-bootstrap.md`

**Issue:** Card 01 creates project but doesn't initialize git repo.

**Fix:** Add `git init` and initial commit to Card 01.

---

### 8. Status Bar Not Documented

**Location:** `ui-flow.md`

**Issue:** Status bar mentioned in CARD-21 but not in UI flow diagrams.

**Fix:** Add status bar to UI layout diagram.

---

### 9. No Dark/Light Theme Mention

**Location:** `ui-flow.md`

**Issue:** Textual supports themes but no theme specified.

**Fix:** Specify default theme. Consider user preference in config.

---

### 10. E2E Test Sign-Off Blank

**Location:** `manual-e2e-test.md`

**Issue:** Sign-off table is empty (expected, but worth noting).

**Fix:** Leave as-is for implementation phase.

---

### 11. Typo in File Path

**Location:** `README.md` (raw requirements reference)

**Issue:** References `raw_requiremenst.md` (typo: "requiremenst" vs "requirements").

**Fix:** Correct filename reference.

---

## Recommendations

### Immediate Actions (Before Implementation)

1. **Generate all missing Trello cards (03-07, 09-15, 16-20)** with same detail level as existing cards. This is blocking.

2. **Create sample fixture files** for all 4 agent types in `tests/fixtures/` for parser testing.

3. **Define CognitiveRouter prompt templates** and context assembly strategy for multi-session queries.

4. **Add error handling specification** to all parser cards with explicit failure modes.

5. **Redesign cognitive_audit table** to use proper many-to-many relationship with junction table.

### High Priority (Phase 1-2)

6. **Add diagnostic commands** (`nexus doctor`, `nexus scan --dry-run`) for debugging.

7. **Implement circuit breaker pattern** for fallback chain with backoff strategy.

8. **Define credential management strategy** (env vars vs keyring).

9. **Add responsive TUI design** with minimum terminal size requirements.

10. **Create i18n infrastructure** early to avoid retrofitting later.

### Medium Priority (Phase 3)

11. **Add session transcript tab** to Inspector for viewing full conversation.

12. **Implement streaming parsers** with memory limits for large files.

13. **Add logging configuration** with file rotation.

14. **Create benchmark tests** for performance requirements.

### Documentation Improvements

15. **Add glossary** of terms (Session, Turn, Context, Chain, etc.).

16. **Create troubleshooting guide** for common issues.

17. **Add architecture diagram** showing component interactions.

---

## Conclusion

The SDD package has a solid foundation with clear requirements, well-defined UI flows, and comprehensive E2E test scenarios. However, **12 critical gaps** must be addressed before implementation can proceed safely. The missing Trello cards alone block 77% of the implementation work.

**Recommendation:** Do not start implementation until:
1. All 22 Trello card files exist with complete instructions
2. Cognitive Router design is fully specified (prompts, context assembly, credentials)
3. Error handling strategy is defined for all components
4. Database schema is reviewed for integrity issues

**Estimated effort to fix critical gaps:** 2-3 days of documentation work.

**Risk of proceeding now:** High probability of mid-implementation blockers, rework, and inconsistent implementations across cards.
