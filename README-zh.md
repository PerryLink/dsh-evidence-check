# dsh-evidence-check — 证据清单齐备性与自洽核对

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-evidence-check` 读取一份证据清单——案件表头加每份证据一行——核对这份清单自身的齐备与自洽：每份证据是否写明名称与待证事实（`claim`、`exhibitName`）、是否注明来源（`source`）、证据形式（`form`）是否属于你所配置的取值口径、取得日期（`obtainedAt`）是否可解析且不晚于提交日期（`submittedAt`）、证据编号（`exhibitNo`）是否唯一、表头是否声明案号（`caseNo`）与举证方（`party`）、待证事实栏是否残留模板占位符。它不判断证据是否真实、取得是否合法、是否具有关联性，是否足以证明待证事实，是否应予采信或排除——那是法庭经质证后依法作出的判断。

## 实际输出长什么样

![Terminal demo of dsh-evidence-check: real output over its EV-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-evidence-check/main/docs/assets/dsh-evidence-check-demo.png)

本插件对自己 `EV-001` 测试夹具的**真实输出**，不是示意图。规则库不伪造引文，因此每条发现都会同时写明所引条款，以及该条款原文本次未取得。

## 它回答什么问题

| 你会问 | 它怎么答 |
|---|---|
| 我们在法院指定的期限内提交了，工具能确认这一点吗？ | 不能。`EV-004` 只核对清单自己带着的两栏日期能否解析、`obtainedAt` 是否不晚于 `submittedAt`；它不推算举证期限——该期限由法院指定或当事人协商，另有延长与中止情形。因此逐日核对清单上的日期，并不构成关于是否逾期提交的结论。 |
| 证据名称填了，待证事实栏空着。 | `EV-001` 把 `claim` 与 `exhibitName` 一并核对，只要求两者至少填了一项；两栏都为空才报出该行，它不判断该份证据是否足以证明该事实——那需要经质证后由法庭判断。 |
| 两行填了同一个证据编号。 | `EV-005` 在清单内部比较 `exhibitNo`，比较时忽略空白字符，报出后出现的那一行及其重复的对象。它只确认编号不唯一——究竟属于重复登记还是编号抄错，需你自行确认。编号栏为空的行不参与这项比较。 |
| 这份证据的来源明摆着，为什么还被报出？ | 因为来源栏没有填写。`EV-002` 要求凡清单给了 `source` 这一栏的每份证据都注明来源；它只核对这一栏有没有内容，不判断来源是否合法、取得方式是否正当。 |
| 清单表头没有写案号和举证方。 | `EV-006` 读取表头，报出材料未声明的 `caseNo` 与 `party`；它核对的是有没有声明，不判断声明的值是否正确，且缺声明只在表头报一条，不逐行重复。 |
| 哪一条会报 `skipped`，为什么？ | 出厂状态下是 `EV-003`：它的 `values` 为空，即证据形式取值口径未配置，而本插件不硬编码证据种类清单——民事、行政、刑事程序列举的种类并不一致。把 `values` 填成本程序的口径后本条即开始运行，此后它只核对每个 `form` 的值是否在册，不判断某份证据实际上属于哪一类。 |

## 依据的标准

| 文件 | 文号 | 引用它的规则 |
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

| 项目 | 状态 |
|---|---|
| Harness | 对等版本范围 `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` —— 已实测同时接受 `0.2.0-rc.2` 与 `0.2.1-alpha.1`。**刻意不声明 `engines.dsh`**：它没有任何读取者，也无法拒装任何宿主 |
| Node | `^22.19.0 || >=24.0.0` |
| 平台 | 全平台（纯 ESM；无原生代码、无联网、不调用模型） |
| 工具模式 | `native` / `ptc` / `both` 均可；批量校验整个目录时建议 `ptc`，schema 成本只付一次 |

## What it does

规则表、字段说明与行为细节见 [README.md](README.md#what-it-does)（英文主版本）。本插件只列出材料与所引条款之间的字面差异，并对无法执行的检查在 `skipped` 中逐项说明。

## Install

```sh
dsh plugin --profile <name> add dsh-evidence-check
dsh --profile <name> --dump-config | grep 'dsh-evidence-check'
```

## Configuration

全部可调参数都在 `src/config.ts` 的 Schemastery schema 中，只改 `cordis.yml` 即可生效，无需改代码；逐条阈值在 `rules/` 下的规则库文件里。

| 键 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rulesFile` | string | `rules/evidence-check.yaml` | 规则库文件路径，相对插件包根目录 |
| `disabledRules` | string[] | `[]` | 要停用的规则 id 列表；每条都会出现在 `skipped` 中 |
| `onlyRules` | string[] | `[]` | 只执行这些规则 id；留空表示执行全部规则 |
| `skipNotes` | string | `""` | 附加到每条 `skipped` 说明后的备注 |
| `timeoutMs` | number | `120000` | 工具协作式超时预算（毫秒） |

## Material format

支持 JSON 与 YAML。完整字段示例见 [README.md](README.md#material-format)（英文主版本）。字段在读取层是可选的，由检查引擎校验，因此部分导出的材料会产生"缺项"类差异，而不是让程序崩溃。

## Rule sources

规则数据与代码分离，每条规则都带文件名、文号、按原文自身编号体系的条款号、逐字摘录与来源地址。加载期强制：摘录必须是真实引文且不少于八个字符；依据仅为原则性条款（`kind: derived-from-principle`，严重级上限 `warn`）或本机构配置（`kind: institutional-configuration`，上限 `info`）的检查不得标为 `error`。夸大依据的规则库会在加载期失败，而不会产出一份看起来很有底气的报告。

核验中确认的边界与"刻意没有作出的结论"见 [README.md](README.md#rule-sources)（英文主版本）与随包的 `rules/evidence/` 目录。

## Troubleshooting

- **插件装上了但工具不出现**：确认 `main` 指向 `lib/index.mjs` 且 `pnpm run build` 已生成该文件；`main` 写错会让加载器静默跳过该条目。
- **`dsh plugin add` 报版本不兼容**：peer 范围覆盖 `0.1.x` 与 `0.2.x`；若运行时在其之外，可显式豁免：`dsh plugin --profile <name> allow-version <包名@版本> --dsh-version <runtime> --accept-risk`
- **某条规则没有执行**：查看 `skipped` 数组，其中写明了规则 id 与原因。
- **`check` 报 `manifest-peers` 失败**：静态检查器比对的是一份早于 0.2 世代的硬编码 peer 范围；安装期的 peer 校验以运行时为准。这是 `dsh-plugin-dev` 的已知上游问题。
- **时间看起来偏移**：全部计算都是对输入字符串做墙上时钟运算，不做时区换算。

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-evidence-check
```

第 4 项把 `../_shared` 的共享件同步进 `src/shared/`；每次改动共享件后都要重跑。

## License

[Apache License 2.0](LICENSE) © 2026 dsh-evidence-check contributors.
