# persona-audit

**Four fake users read what your tool says to real users — and tell you what makes no sense.**

You're too close to your own product to see where a stranger gets stuck. persona-audit spins up four personas who read *only* your tool's output — never the code, never the docs — and report what they misread, panic at, or can't find. A **consensus matrix** shows what several of them hit independently. That's what you fix first.

![persona-audit run on its own README — four personas, five findings](docs/hero-consensus-matrix.png)

> That screenshot is persona-audit run on *this README*. Four personas independently flagged that a tool about "seeing your own blind spots" had a glaring one — it showed no demo. So now it does. This one.

## What it looks like on a real product

Point it at, say, the daily digest your app emails users. Four personas read one real digest cold:

- **Novice:** "It says *This week: 0* — I thought the app was broken."
- **Veteran:** "*Net change* and *total* are both here and I can't tell which is which."
- **Target user:** "Nothing tells me why I should open this tomorrow."

Three different people, one shared confusion → the consensus matrix ranks it top, and you fix the line before it ships. (Full sample run: [`examples/case-study.md`](examples/case-study.md).)

## When to use

✅ A tool whose engine emits **user-facing text** ships a new version or output — report generators, daily digests, bot push copy, readout tools.
❌ Code review · pure UI/visual QA · interactive-narrative QA.

## How it works (and what the terms mean)

1. **Generate 6–8 real outputs** — cover normal cases, edge data, empty states, and the view users actually see.
2. **Four personas cold-read them** — *cold-read* = they see only the output, never your code, so they react like a true first-timer. The four: mirror (your real user), novice (jargon + panic detector), veteran (false-precision detector), new-feature target.
3. **Consensus matrix** — how many personas independently hit the same thing. Cross-angle agreement, not a single nitpick, is the signal.
4. **ABCD triage** — **A** fix now (typos, wrong numbers) · **B** real gaps to build · **C** conflicts with a deliberate design choice → *ask the owner before touching it* · **D** out of scope.
5. **Don't-cut list** — what users actually loved, flagged so you don't break it next version.

## How it's different from "synthetic users"

Those tools simulate users to *do research*, and often dress LLM output up as a measurement. persona-audit does the opposite: it audits the text you **already ship**, and it's blunt that the result is a candidate list to verify — not data.

## Honest about what it is

A single-person, zero-cost, few-minute **blind-spot scan** — not a calibrated measurement. The four personas share one base model, so a "vote" means *several angles converged*, not statistical independence. Act on cross-angle agreement; verify before you treat anything as proven.

## Install

```bash
git clone https://github.com/wjameswen888/persona-audit.git
cp -r persona-audit ~/.claude/skills/
```

It's a [Claude Code skill](https://docs.claude.com/en/docs/claude-code) — auto-triggers on the phrases in its description. Copy `LOCAL.md.example` → `LOCAL.md` to bind it to your product (gitignored; every plug point has a default, so it runs even unfilled).

## Files

| File | What |
|------|------|
| `SKILL.md` | The method — generic, portable |
| `templates.md` | 4 persona identity blocks + report skeleton + cross-domain adaptation |
| `examples/case-study.md` | A real run, start to finish |
| `LOCAL.md.example` | Template for your private product bindings |

## License

MIT — see [LICENSE](LICENSE).

---

**中文**：把"机器生成给人看的文字"丢给 4 个不同认知水平的假用户冷读——只看输出、不看代码——几个人撞同一个问题，就是你最该先修的盲区。它诚实：产出是待核实的候选清单，不是测量。
