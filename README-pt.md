# dsh-evidence-check — Verificação da completude e da coerência interna de uma lista de provas judiciais

[![DSH Market](https://raw.githubusercontent.com/2BingLing/dsh-market/master/assets/readme/badge-listed-en.svg)](https://dsh.market/)

`dsh-evidence-check` lê uma lista de exhibits —o cabeçalho do processo mais uma linha por exhibit— e verifica a completude e a coerência interna dessa lista: se cada exhibit traz nome e o facto que pretende provar (`claim`, `exhibitName`), se o seu `source` está registado, se o seu `form` vem do vocabulário que você configurar, se `obtainedAt` é analisável e não é posterior a `submittedAt`, se não há `exhibitNo` repetido, se o cabeçalho declara `caseNo` e `party` e se não resta nenhum marcador de modelo na coluna do facto. Não decide se a prova é autêntica, se foi obtida licitamente ou se é pertinente, nem se prova o facto, nem se deve ser admitida ou excluída: isso é o juízo do tribunal depois do contraditório.

## Como é a saída

![Terminal demo of dsh-evidence-check: real output over its EV-001 fixture](https://raw.githubusercontent.com/PerryLink/dsh-evidence-check/main/docs/assets/dsh-evidence-check-demo.png)

Saída real deste plugin sobre o seu próprio fixture de teste `EV-001` — não é uma simulação. O pacote de regras não inventa citações, por isso cada achado nomeia a cláusula aplicada e avisa que o seu texto não foi obtido.

## O que ele responde

| Você pergunta | O que ele responde |
|---|---|
| Entregámos dentro do prazo fixado pelo tribunal. Esta ferramenta confirma isso? | Não. `EV-004` verifica apenas que as duas colunas de data que a própria lista traz são analisáveis e que `obtainedAt` não é posterior a `submittedAt`; não calcula qualquer prazo probatório, porque esse prazo é fixado pelo tribunal ou acordado pelas partes, com prorrogações e suspensões próprias. Uma leitura dia a dia da lista não constitui, por isso, uma conclusão sobre a tempestividade. |
| O nome do exhibit está preenchido, mas a coluna do facto está vazia. | `EV-001` abrange `claim` e `exhibitName` em conjunto e pede apenas que pelo menos um dos dois esteja preenchido; reporta a linha em que ambas as células estão vazias e não julga se o exhibit basta para provar o facto. |
| Duas linhas trazem o mesmo número de exhibit. | `EV-005` compara os valores de `exhibitNo` dentro da lista, ignorando espaços, e reporta a linha posterior juntamente com aquela que duplica. Apenas estabelece que o número não é único: se é um registo duplicado ou um número mal copiado, cabe a você decidir. Uma célula de número vazia não entra nessa comparação. |
| A origem deste exhibit é óbvia e, mesmo assim, a regra dispara. | Porque a célula de origem não está preenchida. `EV-002` exige um `source` em cada exhibit a que a lista dê essa coluna; verifica que a célula tem conteúdo, não que a fonte seja lícita ou que o modo de obtenção tenha sido regular. |
| A nossa lista não traz número de processo nem parte que a apresenta no cabeçalho. | `EV-006` lê o cabeçalho e reporta qual de `caseNo` e `party` o material não declara. Verifica a declaração, não se o declarado está correto, e uma declaração em falta é reportada uma só vez para o cabeçalho, não linha a linha. |
| Que regra reporta `skipped` e por quê? | `EV-003` fá-lo de origem: os seus `values` vêm vazios, ou seja, o vocabulário de formas não está configurado, e o plugin não codifica uma lista de classes de prova porque os processos civil, administrativo e penal não enumeram as mesmas. Preencha `values` com as classes do seu processo e a regra passa a correr; a partir daí verifica apenas que cada célula `form` é uma delas, não a que classe pertence realmente uma prova. |

## Normas que segue

| Documento | Número | Regras que o citam |
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

| Superfície | Estado |
|---|---|
| Harness | Faixa de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificada para aceitar tanto `0.2.0-rc.2` quanto `0.2.1-alpha.1`. **`engines.dsh` não é declarado**: não tem leitor e não pode recusar nenhum host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sem código nativo, sem rede, sem chamada ao modelo) |
| Modo de ferramenta | Funciona em `native`, `ptc` e `both`; para um diretório inteiro use `ptc` |

## What it does

A tabela de regras, os campos e o comportamento detalhado estão em [README.md](README.md#what-it-does) (versão principal em inglês). O plugin apenas lista divergências literais frente às cláusulas citadas e indica em `skipped` cada verificação que não pôde ser executada.

## Install

```sh
dsh plugin --profile <name> add dsh-evidence-check
dsh --profile <name> --dump-config | grep 'dsh-evidence-check'
```

## Configuration

Todos os parâmetros ajustáveis ficam no esquema Schemastery de `src/config.ts`, portanto mudam pelo `cordis.yml` sem editar código; os limites por regra ficam no pacote de regras sob `rules/`.

| Chave | Tipo | Padrão | Descrição |
|---|---|---|---|
| `rulesFile` | string | `rules/evidence-check.yaml` | Caminho do pacote de regras, relativo à raiz do pacote |
| `disabledRules` | string[] | `[]` | Ids de regras a desativar; cada uma aparece em `skipped` |
| `onlyRules` | string[] | `[]` | Executar apenas estas regras; vazio executa todas |
| `skipNotes` | string | `""` | Nota acrescentada a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Orçamento de tempo limite cooperativo da ferramenta |

## Material format

Aceita JSON ou YAML. O exemplo completo de campos está em [README.md](README.md#material-format) (versão principal em inglês). Os campos são opcionais na camada de leitura e validados pelo motor, de modo que uma exportação parcial gera achados sobre o que falta em vez de falhar.

## Rule sources

Os dados das regras ficam separados do código: cada regra traz documento, número, cláusula na numeração própria da fonte, trecho literal e URL de origem. O carregador impõe que o trecho seja citação real de pelo menos oito caracteres e que uma verificação baseada apenas em princípio geral (`kind: derived-from-principle`, teto `warn`) ou em política local (`kind: institutional-configuration`, teto `info`) nunca seja declarada `error`.

Os limites verificados e as conclusões deliberadamente **não** afirmadas estão em [README.md](README.md#rule-sources) (versão principal em inglês) e em `rules/evidence/`.

## Troubleshooting

- **O plugin instala mas a ferramenta não aparece**: confirme que `main` resolve para `lib/index.mjs` e que `pnpm run build` o gerou.
- **`dsh plugin add` recusa o pacote**: a faixa de peers cobre `0.1.x` e `0.2.x`; fora dela, conceda isenção explícita com `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Uma regra não executou**: leia o arranjo `skipped`.
- **`check` informa `manifest-peers` como falha**: problema conhecido do `dsh-plugin-dev`; o runtime aplica a compatibilidade na instalação.
- **Os horários parecem deslocados**: toda a aritmética é de hora local sobre as cadeias fornecidas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-evidence-check
```

O último comando copia o kit compartilhado de `../_shared` para `src/shared/`; execute-o novamente após cada alteração compartilhada.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-evidence-check contributors.
