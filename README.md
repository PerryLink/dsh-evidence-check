# dsh-evidence-check — Court exhibit list completeness and internal consistency check

`dsh-evidence-check` reads one exhibit list — the case header plus one row per exhibit — and checks that list's own completeness and internal consistency: that each exhibit carries a name and the fact it is offered to prove (`claim`, `exhibitName`), that its `source` is recorded, that its `form` comes from the vocabulary you configure, that `obtainedAt` parses and does not fall after `submittedAt`, that no `exhibitNo` is repeated, that the header declares `caseNo` and `party`, and that no template placeholder survives in the fact column. It does not decide whether evidence is authentic, lawfully obtained or relevant, whether it proves the fact, or whether it should be admitted or excluded: that is the court's judgement after cross-examination.

## What it answers

| You ask | What it answers |
|---|---|
| We filed inside the period the court set. Will this tool confirm that? | No. `EV-004` only checks that the two date columns the list itself carries can be parsed and that `obtainedAt` is not later than `submittedAt`; it computes no evidence period, because that period is set by the court's notice or agreed by the parties, with extensions and suspensions of its own. A day-by-day reading of the list is therefore not a finding about timeliness. |
| The exhibit name is filled in but the fact column is blank. | `EV-001` covers `claim` and `exhibitName` together and asks only that at least one of the two be filled; it reports a row where both cells are empty, and does not judge whether the exhibit is enough to prove the fact. |
| Two rows carry the same exhibit number. | `EV-005` compares the `exhibitNo` values inside the list, ignoring whitespace, and reports the later row with the row it duplicates. It only establishes that the number is not unique — whether that is a double registration or a mis-copied number is left to you. A blank number cell is not part of that comparison. |
| The source of this exhibit is obvious, yet the rule fires. | Because the source cell is not filled. `EV-002` requires a `source` on every exhibit the list gives that column to; it checks that the cell has content, not that the source is lawful or that the way it was obtained was proper. |
| Our list has no case number or filing party in its header. | `EV-006` reads the header and reports whichever of `caseNo` and `party` the material does not declare. It checks the declaration, not whether what is declared is correct, and a missing declaration is reported once for the header rather than row by row. |
| Which rule reports `skipped`, and why? | `EV-003` does by default: its `values` ship empty, which means the form vocabulary is unconfigured, and the plugin will not hard-code a list of kinds of evidence because civil, administrative and criminal procedure do not enumerate the same ones. Fill `values` with your procedure's own kinds and the rule runs; it then checks only that each `form` cell is one of them, not which kind a piece of evidence really is. |

## Standards it follows

| Document | Number | Cited by rules |
|---|---|---|
| 《最高人民法院关于民事诉讼证据的若干规定》 | 法释〔2019〕19号（现行版本与条号本次未核实） | EV-001, EV-002, EV-004, EV-005, EV-006, EV-007 |
| 《最高人民法院关于民事诉讼证据的若干规定》 | 法释〔2019〕19号（自 2020 年 5 月 1 日起施行） | EV-003 |

**Boundary:** this plugin checks an **证据清单** for what a list can be held to mechanically — that every
exhibit names itself and the fact it is offered to prove, that its source is recorded, that its form comes
from your vocabulary, that acquisition precedes submission, that exhibit numbers are unique, that the list
names its case and the party filing it, and that no placeholder survives. It does **not** decide whether
evidence is authentic, lawfully obtained or relevant, whether it proves the fact, or whether it should be
admitted or excluded. **That is the court's judgement after cross-examination, and it is the heart of the
case.**

> ### ⚠️ Read this before trusting a citation in the report
>
> **Every `excerpt` in this plugin's rule pack says, in so many words, that the clause text was not
> obtained.** The regime lives in 《中华人民共和国民事诉讼法》, 《最高人民法院关于民事诉讼证据的若干规定》
> and 《中华人民共和国行政诉讼法》. The verification pass could not retrieve verbatim clause text, so rather
> than paraphrase a quotation the pack states the gap in the `excerpt` field itself and puts the honest
> reasoning in `note`. Every rule is therefore `warn` or `info`, and a test asserts that no rule claims a
> quotation it does not have. **When the texts are in hand, two things must be done: replace each `excerpt`
> with the real clause, and raise `kind` to `direct`.**
>
> Two notes on what the findings mean. **The form vocabulary ships empty** — civil, administrative and
> criminal procedure list different kinds of evidence, so `EV-003` reports itself in `skipped` rather than
> imposing one list; classifying a piece of evidence is a legal judgement in any case. And `EV-004` checks
> only that **acquisition precedes submission**; it makes **no** finding about the evidence period, because
> that period is set by the court or agreed by the parties, allows for extensions, and a list rarely records
> enough to compute it.

## Compatibility

| Surface | Status |
|---|---|
| Harness | Peer range `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verified to accept both `0.2.0-rc.2` and `0.2.1-alpha.1`. `engines.dsh` is deliberately not declared: it has no reader and cannot reject a host |
| Node | `^22.19.0 || >=24.0.0` |
| Platforms | All (plain ESM; no native code, no network, no model call) |
| Tool mode | Works in `native`, `ptc` and `both`; for a large exhibit list use `ptc` |

## What it does

Registers the `evidence_check` tool. It reads one exhibit list — the case header plus one row per exhibit —
applies a versioned rule pack, and returns a report.

| Rule | Check | Severity | Basis kind |
|---|---|---|---|
| `EV-001` | every exhibit names itself and its fact | warn | principle |
| `EV-002` | every exhibit records its source | warn | principle |
| `EV-003` | the form comes from your vocabulary (off by default) | info | local |
| `EV-004` | acquisition is not later than submission | warn | principle |
| `EV-005` | exhibit numbers are unique | warn | principle |
| `EV-006` | the list names its case and filing party | warn | principle |
| `EV-007` | the fact column holds no unreplaced placeholder | warn | principle |

## Install

```sh
dsh plugin --profile <name> add dsh-evidence-check
dsh --profile <name> --dump-config | grep 'dsh-evidence-check'
```

## Configuration

| Key | Type | Default | Description |
|---|---|---|---|
| `rulesFile` | string | `rules/evidence-check.yaml` | Rule-pack path, relative to the package root |
| `disabledRules` | string[] | `[]` | Rule ids to stop running; each appears in `skipped` |
| `onlyRules` | string[] | `[]` | Run only these rule ids; empty runs every rule |
| `skipNotes` | string | `""` | Note appended to every `skipped` reason |
| `timeoutMs` | number | `120000` | Cooperative tool timeout budget |

Rule-level parameters worth knowing:

- `EV-003` `values` — your procedure's kinds of evidence, e.g.
  `[书证, 物证, 视听资料, 电子数据, 证人证言, 鉴定意见, 勘验笔录]`. Empty means no check.
- `EV-004` `field` / `notBeforeField` — the date pair, acquisition against submission by default.
- `EV-007` `terms` — the placeholders to look for.

## Material format

The tool accepts JSON or YAML:

```yaml
caseNo: （2026）某民初 1234 号
caseName: 买卖合同纠纷
party: 原告某某公司
rows:
  - { 证据编号: 证1, 待证事实: 双方于 2025 年 3 月 10 日签订买卖合同,
      证据名称: 买卖合同原件, 证据形式: 书证, 来源: 原告留存，签订时取得,
      页码: 第 1-3 页, 原件: 原件, 取得日期: 2025-03-10, 提交日期: 2026-03-02 }
```

Column names are matched case-insensitively and ignoring spaces, underscores and hyphens; the list's own
column names are kept, so a finding names the column it read. Dates may be `2026-03-02` or
`2026-03-02 09:30`.

## Rule sources

Rule data lives in `rules/evidence-check.yaml`. The pack's header states the citation gap in full, and each
rule's `note` repeats the part that matters for that rule. The load-time guard that normally enforces "an
excerpt must be a real quotation of at least eight characters" cannot tell a quotation from a description —
so this pack leans on the header, the per-rule notes and a test that asserts every `excerpt` admits the gap.

## Troubleshooting

- **`EV-003` never runs.** Its vocabulary is empty. Kinds of evidence differ between civil, administrative and
  criminal procedure, so the plugin will not impose a list.
- **`EV-004` fires although I filed within the period.** The rule does not know the period; it only compares
  the acquisition and submission cells. If acquisition really postdates submission, one of the two is wrong.
- **`EV-002` fires on an exhibit whose source is obvious.** A blank source cell means the list does not say
  where the exhibit came from, which is exactly what a list has to say.
- **`EV-005` fires twice on one exhibit number.** Numbering a supplementary bundle with the same number is
  common; correct the number rather than relying on the remark.
- **The plugin installs but the tool never appears.** Check that `main` resolves to `lib/index.mjs` and
  that `pnpm run build` produced it; a wrong `main` makes the loader skip the entry silently.
- **`dsh plugin add` refuses the package as incompatible.** The peer range covers `0.1.x` and `0.2.x`; if
  your runtime sits outside it, grant an explicit exemption:
  `dsh plugin --profile <name> allow-version dsh-evidence-check@0.1.0 --dsh-version <runtime> --accept-risk`
- **`check` reports `manifest-peers` as failed.** The static checker compares against a hard-coded peer
  range that predates the 0.2 line. The runtime enforces peer compatibility at install time, so the
  declared range is the correct one; this is a known upstream issue in `dsh-plugin-dev`.

## Development

```sh
pnpm install
pnpm run typecheck   # tsc --noEmit
pnpm test            # vitest, the shared table-plugin suite plus paired fixtures
pnpm run build       # tsdown -> lib/index.mjs + lib/index.d.mts
node ../scripts/sync-shared.mjs dsh-evidence-check   # refresh src/shared from ../_shared
```

The plugin is **data-only**: `src/model.ts` declares the table shape, the shared kit supplies the reader and
the check engine, and the rule pack declares every check.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-evidence-check contributors.
