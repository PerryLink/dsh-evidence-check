# dsh-evidence-check

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
pnpm pack
dsh plugin --profile <name> add ./dsh-evidence-check-0.1.0.tgz
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
