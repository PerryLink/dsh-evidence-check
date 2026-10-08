# dsh-evidence-check — न्यायालयीन साक्ष्य-सूची की पूर्णता और आंतरिक संगति की जाँच

`dsh-evidence-check` एक न्यायालयीन साक्ष्य-सूची पढ़ता है — मुकदमे का हेडर और प्रत्येक साक्ष्य की एक पंक्ति — और उसी सूची की पूर्णता तथा आंतरिक संगति की जाँच करता है: क्या प्रत्येक साक्ष्य का नाम और वह तथ्य दर्ज है जिसे सिद्ध करना है (`claim`, `exhibitName`), क्या उसका `source` दर्ज है, क्या उसका `form` आपके द्वारा कॉन्फ़िगर की गई सूची से है, क्या `obtainedAt` पढ़ा जा सकता है और `submittedAt` के बाद का नहीं है, क्या कोई `exhibitNo` दोहराया नहीं गया, क्या हेडर `caseNo` और `party` घोषित करता है, और क्या तथ्य-कॉलम में कोई टेम्पलेट प्लेसहोल्डर शेष नहीं है। यह तय नहीं करता कि साक्ष्य असली है, वैध रूप से प्राप्त हुआ है या प्रासंगिक है, कि वह तथ्य सिद्ध करता है, या कि उसे स्वीकार या अस्वीकार किया जाना चाहिए — वह जिरह के बाद न्यायालय का निर्णय है।

## यह किन सवालों का जवाब देता है

| आपका सवाल | इसका जवाब |
|---|---|
| हमने न्यायालय द्वारा तय अवधि के भीतर दाखिल किया। क्या यह उपकरण इसकी पुष्टि करेगा? | नहीं। `EV-004` केवल यह देखता है कि सूची में दर्ज दोनों तिथि-कॉलम पढ़े जा सकते हैं और `obtainedAt` `submittedAt` के बाद का नहीं है; यह कोई साक्ष्य-अवधि नहीं निकालता, क्योंकि वह अवधि न्यायालय तय करता है या पक्षकार तय करते हैं, और उसमें विस्तार तथा स्थगन के अपने नियम हैं। इसलिए सूची की तिथियों को दिन-प्रतिदिन पढ़ना समय-पालन पर कोई निष्कर्ष नहीं है। |
| साक्ष्य का नाम भरा है, पर तथ्य-कॉलम खाली है। | `EV-001` `claim` और `exhibitName` दोनों को साथ लेता है और केवल इतना चाहता है कि इनमें से कम से कम एक भरा हो; दोनों कोठरियाँ खाली होने पर वह पंक्ति दर्ज करता है, और यह नहीं आँकता कि वह साक्ष्य उस तथ्य को सिद्ध करने के लिए पर्याप्त है। |
| दो पंक्तियों में एक ही साक्ष्य-क्रमांक दर्ज है। | `EV-005` सूची के भीतर `exhibitNo` के मानों की तुलना करता है, रिक्त स्थान को छोड़कर, और बाद वाली पंक्ति के साथ वह पंक्ति दर्ज करता है जिसकी वह पुनरावृत्ति है। यह केवल यह स्थापित करता है कि क्रमांक अद्वितीय नहीं है — यह दोहरा पंजीकरण है या क्रमांक की प्रतिलिपि में चूक, यह आपको तय करना है। खाली क्रमांक वाली कोठरी इस तुलना में नहीं आती। |
| इस साक्ष्य का स्रोत स्पष्ट है, फिर भी नियम दर्ज हो रहा है। | क्योंकि स्रोत की कोठरी भरी नहीं है। `EV-002` हर उस साक्ष्य पर `source` की अपेक्षा करता है जिसे सूची यह कॉलम देती है; यह देखता है कि कोठरी में कुछ है, यह नहीं कि स्रोत वैध है या उसे प्राप्त करने का तरीका उचित था। |
| हमारी सूची के हेडर में न मुकदमा-क्रमांक है न दाखिल करने वाला पक्ष। | `EV-006` हेडर पढ़ता है और बताता है कि सामग्री `caseNo` और `party` में से क्या घोषित नहीं करती। यह घोषणा की जाँच करता है, यह नहीं कि घोषित मान सही है, और अनुपस्थित घोषणा हेडर के लिए एक ही बार दर्ज होती है, पंक्ति-दर-पंक्ति नहीं। |
| कौन-सा नियम `skipped` दर्ज करता है, और क्यों? | फ़ैक्टरी स्थिति में `EV-003`: उसके `values` खाली आते हैं, अर्थात् साक्ष्य-रूप की शब्दावली कॉन्फ़िगर नहीं है, और यह प्लगइन साक्ष्य की श्रेणियों की कोई सूची कठोर-कोडित नहीं करता, क्योंकि दीवानी, प्रशासनिक और आपराधिक प्रक्रियाएँ एक जैसी श्रेणियाँ नहीं गिनातीं। अपनी प्रक्रिया की श्रेणियाँ `values` में भरें तो यह नियम चलने लगता है; तब यह केवल देखता है कि प्रत्येक `form` कोठरी उन्हीं में से है, यह नहीं कि कोई साक्ष्य वास्तव में किस श्रेणी का है। |

## यह किन मानकों पर आधारित है

| दस्तावेज़ | संख्यांक | इन्हें उद्धृत करने वाले नियम |
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

| सतह | स्थिति |
|---|---|
| Harness | peer रेंज `>=0.1.2-rc.1 <0.2.0 \|\| >=0.2.0-0 <0.3.0` — `0.2.0-rc.2` और `0.2.1-alpha.1` दोनों को स्वीकार करने के लिए सत्यापित। **`engines.dsh` जानबूझकर घोषित नहीं**: इसका कोई पाठक नहीं और यह किसी होस्ट को अस्वीकार नहीं कर सकता |
| Node | `^22.19.0 || >=24.0.0` |
| प्लेटफ़ॉर्म | सभी (शुद्ध ESM; कोई नेटिव कोड नहीं, कोई नेटवर्क नहीं, कोई मॉडल कॉल नहीं) |
| टूल मोड | `native`, `ptc` और `both` में काम करता है; पूरे फ़ोल्डर के लिए `ptc` चुनें |

## What it does

नियम-सूची, फ़ील्ड और विस्तृत व्यवहार [README.md](README.md#what-it-does) (अंग्रेज़ी मुख्य संस्करण) में हैं। यह प्लगइन केवल उद्धृत धाराओं के सामने शाब्दिक अंतर सूचीबद्ध करता है और हर न चल पाई जाँच को `skipped` में बताता है।

## Install

```sh
dsh plugin --profile <name> add dsh-evidence-check
dsh --profile <name> --dump-config | grep 'dsh-evidence-check'
```

## Configuration

सभी समायोज्य पैरामीटर `src/config.ts` की Schemastery स्कीमा में हैं, इसलिए कोड बदले बिना `cordis.yml` से बदले जा सकते हैं; प्रति-नियम सीमाएँ `rules/` के नियम-पैक में हैं।

| कुंजी | प्रकार | डिफ़ॉल्ट | विवरण |
|---|---|---|---|
| `rulesFile` | string | `rules/evidence-check.yaml` | नियम-पैक का पथ, पैकेज रूट के सापेक्ष |
| `disabledRules` | string[] | `[]` | बंद करने वाले नियम id; प्रत्येक `skipped` में दिखता है |
| `onlyRules` | string[] | `[]` | केवल ये नियम चलाएँ; खाली होने पर सभी नियम चलते हैं |
| `skipNotes` | string | `""` | हर `skipped` कारण के आगे जोड़ी जाने वाली टिप्पणी |
| `timeoutMs` | number | `120000` | उपकरण का सहकारी समय-सीमा बजट |

## Material format

JSON या YAML स्वीकार्य है। पूरा फ़ील्ड उदाहरण [README.md](README.md#material-format) (अंग्रेज़ी मुख्य संस्करण) में है। पढ़ने की परत में फ़ील्ड वैकल्पिक हैं और जाँच इंजन उन्हें सत्यापित करता है, इसलिए आंशिक निर्यात पर क्रैश के बजाय "अनुपस्थित" श्रेणी के निष्कर्ष मिलते हैं।

## Rule sources

नियम-डेटा कोड से अलग है: प्रत्येक नियम में दस्तावेज़, संख्या, स्रोत की अपनी क्रमांकन-प्रणाली के अनुसार धारा, शब्दशः उद्धरण और स्रोत URL होता है। लोडर लागू करता है कि उद्धरण कम से कम आठ अक्षरों का वास्तविक उद्धरण हो, और जिस जाँच का आधार केवल सामान्य सिद्धांत (`kind: derived-from-principle`, अधिकतम `warn`) या स्थानीय नीति (`kind: institutional-configuration`, अधिकतम `info`) हो, उसे कभी `error` घोषित न किया जाए।

सत्यापित सीमाएँ और जान-बूझकर **न** कहे गए निष्कर्ष [README.md](README.md#rule-sources) (अंग्रेज़ी मुख्य संस्करण) और `rules/evidence/` में हैं।

## Troubleshooting

- **प्लगइन इंस्टॉल हो गया पर टूल दिखता नहीं**: जाँचें कि `main` `lib/index.mjs` पर जाता है और `pnpm run build` ने उसे बनाया है।
- **`dsh plugin add` असंगत बताकर मना करता है**: peer range `0.1.x` और `0.2.x` दोनों को कवर करती है; बाहर होने पर स्पष्ट छूट दें: `dsh plugin --profile <name> allow-version <pkg@ver> --dsh-version <runtime> --accept-risk`।
- **कोई नियम नहीं चला**: `skipped` सरणी देखें।
- **`check` में `manifest-peers` विफल दिखता है**: यह `dsh-plugin-dev` की ज्ञात अपस्ट्रीम समस्या है; रनटाइम इंस्टॉल के समय अनुकूलता लागू करता है।
- **समय खिसका हुआ लगता है**: सारी गणना दिए गए स्ट्रिंग पर वॉल-क्लॉक है।

## Development

```sh
pnpm install
pnpm run typecheck
pnpm test
pnpm run build
node ../scripts/sync-shared.mjs dsh-evidence-check
```

अंतिम कमांड `../_shared` का साझा किट `src/shared/` में कॉपी करता है; हर साझा बदलाव के बाद इसे दोबारा चलाएँ।

## License

[Apache License 2.0](LICENSE) © 2026 dsh-evidence-check contributors.
