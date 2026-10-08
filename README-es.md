# dsh-evidence-check — Verificación de la completitud y la coherencia interna de una lista de pruebas judiciales

`dsh-evidence-check` lee una lista de exhibits —la cabecera del caso más una fila por exhibit— y comprueba la completitud y la coherencia interna de esa lista: que cada exhibit lleve nombre y el hecho que pretende probar (`claim`, `exhibitName`), que su `source` esté registrado, que su `form` provenga del vocabulario que usted configure, que `obtainedAt` se pueda analizar y no sea posterior a `submittedAt`, que no se repita ningún `exhibitNo`, que la cabecera declare `caseNo` y `party`, y que no quede ningún marcador de plantilla en la columna del hecho. No decide si la prueba es auténtica, si se obtuvo lícitamente o si es pertinente, ni si prueba el hecho, ni si debe admitirse o excluirse: eso lo juzga el tribunal tras el careo.

## Qué responde

| Usted pregunta | Qué responde |
|---|---|
| Presentamos dentro del plazo que fijó el tribunal. ¿Lo confirmará esta herramienta? | No. `EV-004` comprueba únicamente que las dos columnas de fecha que la propia lista trae se puedan analizar y que `obtainedAt` no sea posterior a `submittedAt`; no calcula ningún plazo de prueba, porque ese plazo lo fija el tribunal o lo acuerdan las partes, con prórrogas y suspensiones propias. Una lectura día a día de la lista no es, por tanto, una conclusión sobre la oportunidad. |
| El nombre del exhibit está puesto, pero la columna del hecho está vacía. | `EV-001` cubre `claim` y `exhibitName` en conjunto y solo pide que al menos uno de los dos esté relleno; informa de la fila en la que ambas celdas están vacías y no juzga si el exhibit basta para probar el hecho. |
| Dos filas llevan el mismo número de exhibit. | `EV-005` compara los valores de `exhibitNo` dentro de la lista, ignorando los espacios, e informa de la fila posterior junto con aquella que duplica. Solo acredita que el número no es único: si se trata de un doble registro o de un número mal copiado queda a su criterio. Una celda de número vacía no entra en esa comparación. |
| El origen de este exhibit es evidente y, aun así, la regla salta. | Porque la celda de origen no está rellena. `EV-002` exige un `source` en cada exhibit al que la lista dé esa columna; comprueba que la celda tenga contenido, no que la fuente sea lícita ni que la forma de obtenerla haya sido correcta. |
| Nuestra lista no trae número de caso ni parte que la presenta en la cabecera. | `EV-006` lee la cabecera e informa de cuál de `caseNo` y `party` no declara el material. Comprueba la declaración, no si lo declarado es correcto, y una declaración ausente se informa una sola vez para la cabecera, no fila por fila. |
| ¿Qué regla informa de `skipped` y por qué? | `EV-003` lo hace de fábrica: sus `values` vienen vacíos, es decir, el vocabulario de formas no está configurado, y el plugin no codifica una lista de clases de prueba porque los procedimientos civil, contencioso-administrativo y penal no enumeran las mismas. Rellene `values` con las clases de su procedimiento y la regla se ejecuta; entonces solo comprueba que cada celda `form` sea una de ellas, no a qué clase pertenece realmente una prueba. |

## Normas que sigue

| Documento | Número | Reglas que lo citan |
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

| Superficie | Estado |
|---|---|
| Harness | Rango de peers `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — verificado para aceptar tanto `0.2.0-rc.2` como `0.2.1-alpha.1`. **No se declara `engines.dsh`**: no tiene lector y no puede rechazar ningún host |
| Node | `^22.19.0 || >=24.0.0` |
| Plataformas | Todas (ESM puro; sin código nativo, sin red, sin llamada al modelo) |
| Modo de herramienta | Funciona en `native`, `ptc` y `both`; para un directorio completo use `ptc` |

## What it does

La tabla de reglas, los campos y el comportamiento detallado están en [README.md](README.md#what-it-does) (versión principal en inglés). El plugin sólo enumera divergencias literales frente a las cláusulas citadas e indica en `skipped` cada comprobación que no pudo ejecutarse.

## Install

```sh
dsh plugin --profile <name> add dsh-evidence-check
dsh --profile <name> --dump-config | grep 'dsh-evidence-check'
```

## Configuration

Todos los parámetros ajustables viven en el esquema Schemastery de `src/config.ts`, por lo que se cambian desde `cordis.yml` sin tocar el código; los umbrales por regla están en el paquete de reglas bajo `rules/`.

| Clave | Tipo | Predeterminado | Descripción |
|---|---|---|---|
| `rulesFile` | string | `rules/evidence-check.yaml` | Ruta del paquete de reglas, relativa a la raíz del paquete |
| `disabledRules` | string[] | `[]` | Ids de reglas que se dejan de ejecutar; cada una aparece en `skipped` |
| `onlyRules` | string[] | `[]` | Ejecutar solo estas reglas; vacío ejecuta todas |
| `skipNotes` | string | `""` | Nota añadida a cada motivo de `skipped` |
| `timeoutMs` | number | `120000` | Presupuesto de tiempo de espera cooperativo de la herramienta |

## Material format

Acepta JSON o YAML. El ejemplo completo de campos está en [README.md](README.md#material-format) (versión principal en inglés). Los campos son opcionales en la capa de lectura y los valida el motor, de modo que una exportación parcial produce hallazgos sobre lo que falta en lugar de un fallo.

## Rule sources

Los datos de las reglas están separados del código: cada regla lleva documento, número, cláusula en la numeración propia de la fuente, extracto literal y URL de origen. El cargador impone que el extracto sea una cita real de al menos ocho caracteres y que una comprobación basada sólo en un principio general (`kind: derived-from-principle`, tope `warn`) o en una política local (`kind: institutional-configuration`, tope `info`) nunca se declare `error`.

Los límites verificados y las conclusiones deliberadamente **no** afirmadas están en [README.md](README.md#rule-sources) (versión principal en inglés) y en `rules/evidence/`.

## Troubleshooting

- **El plugin se instala pero la herramienta no aparece**: compruebe que `main` resuelve a `lib/index.mjs` y que `pnpm run build` lo generó.
- **`dsh plugin add` rechaza el paquete**: la faixa de peers cubre `0.1.x` y `0.2.x`; fuera de ella, conceda una exención explícita con `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`.
- **Una regla no se ejecutó**: lea el arreglo `skipped`.
- **`check` informa `manifest-peers` como fallo**: es un problema conocido de `dsh-plugin-dev`; el runtime aplica la compatibilidad al instalar.
- **Los horarios parecen desplazados**: toda la aritmética es de hora local sobre las cadenas entregadas.

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-evidence-check
```

El último comando copia el kit compartido de `../_shared` a `src/shared/`; vuelva a ejecutarlo tras cada cambio compartido.

## License

[Apache License 2.0](LICENSE) © 2026 dsh-evidence-check contributors.
