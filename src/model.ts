/**
 * dsh-evidence-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'evidence_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  exhibitNo: ['证据编号', '编号', '证据序号', 'exhibitNo'],
  claim: ['待证事实', '证明对象', '事实', 'claim'],
  exhibitName: ['证据名称', '证据材料', '材料名称', 'exhibitName'],
  form: ['证据形式', '证据种类', '形式', 'form'],
  source: ['来源', '证据来源', '取得方式', 'source'],
  pages: ['页码', '页数', '所在页', 'pages'],
  original: ['原件', '是否原件', '原件核对', 'original'],
  obtainedAt: ['取得日期', '形成日期', '日期', 'obtainedAt'],
  submittedAt: ['提交日期', '举证日期', '提交时间', 'submittedAt'],
  custodian: ['保管人', '持有人', '提交人', 'custodian'],
  crossRef: ['对应条款', '关联证据', '交叉引用', 'crossRef'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'items', 'exhibits', '证据'],
  columns: COLUMNS,
  header: {
  caseNo: ['caseNo', '案号', '案件编号'],
  caseName: ['caseName', '案由', '案件名称'],
  party: ['party', '举证方', '当事人'],
  hearingAt: ['hearingAt', '开庭日期', '举证期限'],
  checklist: ['checklist', '证据清单名称'],
  checkedAt: ['checkedAt', '核对日期'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '证据名称',
  'exhibitName',
  '待证事实',
  'claim',
  '证据编号',
  'exhibitNo',
  '页码',
  'pages',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
