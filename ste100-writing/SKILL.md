---
name: ste100-writing
description: 用 ASD-STE100 簡化技術英文（Simplified Technical English，航空維修手冊的受控英文）來解釋、寫作、改寫或檢查英文，也就是 Karpathy（卡帕西）建議的「叫 LLM 用 ASD-STE100 解釋事情」，預設做到約 80%。使用者提到 STE、ASD-STE100、Simplified Technical English、「像飛機維修手冊那樣寫」、航空簡化英文、簡化技術英文、卡帕西/Karpathy 的寫法時一定要用；要把 README、SOP、作業指導書、操作步驟、runbook、錯誤訊息、技術文件改成簡單清楚、非母語者也讀得懂的英文，或要檢查英文是否符合 STE 時也要用。Use for "explain X in STE", "write like an aircraft manual", "80% of the way to ASD-STE100", "rewrite this procedure in simplified English", "check this against STE".
---

# ASD-STE100 簡化技術英文

## 這是什麼

ASD-STE100（Simplified Technical English, STE）是歐洲航太業在 1980 年代為飛機維修手冊制定的受控英文。目前版本 Issue 9（2025-01）有 53 條寫作規則（分 9 節），加上一本約 900 個核准字的字典，每個字只有一個意思。設計目標：英文非母語的技師讀一次就懂，而且不會誤解。

Karpathy 在 2026-10-01 建議：請 LLM 用 ASD-STE100 解釋東西，輸出會好讀很多。標準太嚴時，改成要求「80% of the way to ASD-STE100」。

這招有效，是因為 LLM 預設的英文有幾個固定毛病：句子長、層層避險、同一件事換三個詞講、先鋪陳再講重點。STE 的規則剛好一條一條對付這些毛病。

## 第一步：選強度

| 強度 | 何時用 | 做法 |
|---|---|---|
| **80%（預設）** | 解釋概念、回答問題、內部文件、README、email 草稿 | 套用下面的「核心規則」。如果嚴格 STE 會讓句子變得彆扭（例如為了避開一個常見字而繞一大圈），保留那個自然的常用字。 |
| **strict** | 真正的作業程序、SOP、維修/操作手冊、安全警告、會被翻譯成多國語言的文件 | 套用 [references/rules.md](references/rules.md) 全部規則，然後跑檢查腳本並修正。 |
| **check** | 使用者給一段文字要你「檢查 / 審 / 看符不符合」 | 跑檢查腳本，再自己讀一遍，列出問題與修正建議。除非使用者要求，不要整段重寫。 |

使用者沒指定就用 80%。使用者說「嚴格」「完全符合」「strict」「要放進手冊」就用 strict。

## 核心規則（80% 模式就是這 13 條）

每一條都對應一種讀者會誤讀的情況。理解原因比死記重要：遇到規則沒寫到的狀況時，問自己「非母語讀者會不會讀錯？」

1. **One sentence, one idea.** Procedure sentences (instructions): max 20 words. Description sentences: max 25 words. In a long sentence, the reader cannot see which part is the main point.
2. **One instruction per sentence**, in command form: "Remove the cover." Exception: two actions that must happen at the same time.
3. **Condition first, then the action**: "If the LED is red, stop the pump." The reader must know the condition before they act.
4. **Active voice.** "The script deletes the cache", not "The cache is deleted". Passive voice hides who does the action. In descriptions, use passive only when nobody knows who or what does the action.
5. **Use the same word for the same thing.** If you call it "server", do not later call it "host", "machine" or "node". For a non-native reader, a new word means a new thing. Choose the terms before you write.
6. **Common, simple words with one meaning.** "use" not "utilize", "make sure" not "ensure", "start" not "commence", "before" not "prior to". Do not use phrasal verbs that have many meanings ("set up", "carry out", "figure out"). See [references/word-swaps.md](references/word-swaps.md).
7. **Simple verb forms.** Use the imperative, simple present, simple past and future ("will"). Do not stack helper verbs ("would have been", "has been running"). Use -ing forms only inside fixed technical names.
8. **Max three words in a noun stack.** "database connection pool timeout setting" → "the timeout setting of the database connection pool".
9. **Most important information first.** Give the answer, then the reason, then the details. One topic per paragraph, max six sentences per paragraph.
10. **Keep the small words.** Do not remove "the", "a" or "that" to make text shorter. Do not use contractions ("do not", not "don't"). Telegraphic text is short, but it is ambiguous.
11. **Be specific.** "Tighten to 25 N·m", not "tighten firmly". "After 30 seconds", not "after a while". Give numbers with units.
12. **Vertical lists** for steps and for three or more parallel items. Use a colon to start a list. Do not use semicolons.
13. **Safety notices before the step.** WARNING = risk to people. CAUTION = risk to equipment or data. Start with a command, then give the risk: "CAUTION: Do not remove the disk while the LED flashes. You can lose data."

### LLM 專屬的額外清理

這些不是 STE 原文規則，但精神相同，專門處理 LLM 的習慣：

- No preamble ("Great question!", "Sure, here is...") and no closing summary that repeats the text.
- No stacked hedges ("might potentially possibly"). If something is uncertain, say it one time and say what is uncertain.
- No filler: "it is worth noting that", "it is important to remember", "basically", "essentially".
- No idioms, metaphors or rhetorical questions ("under the hood", "a silver bullet", "So what does this mean?").
- Define each acronym and technical noun the first time you use it.

## 解釋模式（Karpathy 的用法）

使用者要你「用 STE 解釋 X」時：

1. First sentence: the direct answer.
2. Then short paragraphs, one topic each.
3. If there is a process, use a numbered list of steps.
4. When a technical noun appears for the first time, define it in one short sentence.
5. Use one concrete example if it helps (real values, real names).

範例（80%，解釋資料庫索引）：

> An index is a separate data structure that helps the database find rows quickly.
>
> Without an index, the database must read every row in the table to find a value. With an index on a column, the database first finds the value in the index. Then the index tells the database where the matching rows are.
>
> An index has a cost. When you insert, update or delete a row, the database must also change the index. As a result, write operations are slower, and the database uses more disk space.

## 改寫模式

1. Read all of the source text. List its facts. The rewrite must keep all of these facts and add no new facts. STE makes text clearer. It must not change what the text says.
2. Make a term list: one word for each concept. Use the term that the source uses most, or the most common one.
3. Classify each part: **procedure** (the reader does something) or **description** (the reader learns something). The sentence limit and the voice rule depend on this.
4. Rewrite. Do not change code blocks, commands, file paths, identifiers, UI labels, error message text or direct quotes. Readers search for these exact strings.
5. If the source is ambiguous (for example, "it" can mean two things, or the order of steps is not clear), do not guess. Ask the user, or mark it in the text: `[UNCLEAR: ...]`. STE exists to remove ambiguity, and a confident guess only hides it.
6. In strict mode, or when the text is longer than about 300 words, run the checker and fix what it finds.
7. Output the rewritten text. After it, add a short note only when it is useful: the term choices you made and the `[UNCLEAR]` items. Do not explain every change.

範例（strict）：

> **Before:** In order to ensure that the configuration changes are properly applied, it is recommended that the service be restarted after the config file has been modified, although in some cases this may not be strictly necessary.
>
> **After:**
> 1. Edit the configuration file.
> 2. Restart the service to apply the changes.
>
> [UNCLEAR: The source says that a restart is "not always necessary", but it does not say when. Which changes apply without a restart?]

## 檢查腳本

`scripts/ste_check.py`（只用 Python 標準函式庫）。用 skill 資料夾的絕對路徑執行：

```bash
python <skill-dir>/scripts/ste_check.py draft.md
python <skill-dir>/scripts/ste_check.py draft.md --json
python <skill-dir>/scripts/ste_check.py - < draft.md
```

它會找：句子太長（依句首動詞猜是程序句 20 字或描述句 25 字）、段落超過 6 句、可能的被動語態、-ing 形式、分號、縮寫（don't）、替換清單裡的字詞、填充語、句首的 "This/It + 動詞"（指代不明）。程式碼區塊、行內程式碼、表格、標題會被略過。

這是啟發式工具。它無法檢查意思、術語一致性、多字名詞堆疊，也沒有官方字典。把每個結果當成「去看一下這裡」，不是「這裡一定錯」。例如 "The valve is closed" 描述狀態，是 STE 允許的（過去分詞當形容詞），但腳本仍會標成可能的被動。

## 中文使用者

- **用中文問、但要求 STE：** 用 STE 英文回答。STE 本來就是為非母語讀者設計的，這正是它的用途。使用者需要的話，可以在最後附一兩句中文重點。
- **要「用同樣精神寫中文」：** 這不屬於 STE 標準，但原則可以轉移：一句一事、步驟用編號的祈使句、條件放前面、主動語態、同一事物固定用同一個詞、先講結論、少用成語和四字堆疊、數字帶單位、句子盡量控制在約 35 字內（經驗值，不是標準）。

## 不適用的情況與限制

- **行銷文案、創意寫作、個人風格的文字、法律條文：** STE 會讓它們變得平板，甚至改變法律意義。先告訴使用者這點，問過再套用。
- **STE 改善的是清楚度，不是正確性。** 寫得很清楚的錯誤句子仍然是錯的。改寫時不能動到事實。
- **官方字典沒有附在這裡**（約 900 個核准字、約 1,200 個非核准字與替代字，有版權）。在 strict 模式下，要告訴使用者「沒有逐字對照官方字典」。官方版本可以在 asd-ste100.org 免費申請。如果使用者把字表放進 `references/`，就以它為準。
- **網路上流傳的 STE 小抄有錯**：例如 "approximately" 其實是核准字；"test" 只能當名詞用。細節見 [references/word-swaps.md](references/word-swaps.md)。
