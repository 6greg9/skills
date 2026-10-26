# STE 規則摘要（strict 模式用）

這是依 ASD-STE100 的九個主題區塊，用自己的話整理的摘要，**不是官方條文**。條文編號與完整字典請看官方版本（asd-ste100.org 可免費申請；Issue 9，2025-01-15）。

目錄：
1. 用字（Words）
2. 多字名詞（Multi-word nouns）
3. 動詞（Verbs）
4. 句子（Sentences）
5. 程序寫作（Procedural writing）
6. 描述寫作（Descriptive writing）
7. 安全指示（Safety instructions）
8. 標點與字數計算（Punctuation and word counts）
9. 寫作習慣（Writing practices）

---

## 先分類：程序 vs 描述

動筆前，先決定每一段是哪一種：

- **Procedure（程序）**：讀者要「做」事。用祈使句，每句最多 20 字，只能用主動語態。
- **Description（描述）**：讀者要「知道」事。每句最多 25 字，段落最多 6 句，盡量用主動語態。

很多規則只適用其中一種，所以這一步不能省。

---

## 1. 用字

- 只用核准字，而且只用它核准的詞性和意思。例：`TEST` 只核准當名詞 → 不寫 "Test the valve"，寫 "Do a test of the valve"。
- 另外允許兩類專業字：
  - **Technical nouns**（技術名詞）：零件名稱、工具、材料、單位、軟體名稱、標籤上的文字等。照原樣使用，不要把它當動詞用。
  - **Technical verbs**（技術動詞）：特定的製程或電腦操作（例如 drill, weld, compile, click）。只當動詞用。
- 同一件事永遠用同一個字。不要為了「變化」而換同義字。
- 一個字如果有好幾個意思，換成只有一個意思的字。
- 比較級、最高級只用核准的形式。

範例：
- ✗ "Utilize the provided wrench to secure the fitting."
- ✓ "Use the wrench to tighten the fitting."

## 2. 多字名詞

- 名詞堆疊最多 3 個字。超過時，用介系詞拆開，或第一次出現時完整寫出並說明。
- 一組字被當成一個單位使用時，可以用連字號表示它們的關係。

範例：
- ✗ "the hydraulic pump pressure relief valve adjustment screw"
- ✓ "the adjustment screw of the pressure relief valve on the hydraulic pump"

## 3. 動詞

- 允許的動詞形式：不定詞、祈使句、簡單現在式、簡單過去式、未來式（will）、過去分詞（只能當形容詞用）。
- 不用完成式和複雜的助動詞組合（"has been removed", "would have been"）。
- 過去分詞只能當形容詞："The valve is closed"（描述狀態，可以）。
- -ing 形式只能出現在固定的技術名詞裡（例如某個零件或系統的正式名稱），不要拿來造句。
- 程序寫作只能用主動語態。描述寫作盡量用主動語態，只有在不知道動作者時才用被動。
- 用動詞表達動作，不要把動作藏進名詞裡："Turn the knob"，不是 "Give the knob a turn"。

範例：
- ✗ "The filter should have been replaced before the system was being restarted."
- ✓ "Replace the filter before you start the system again."

## 4. 句子

- 一句只講一個主題。
- 不要為了縮短句子而省略冠詞、"that"、動詞，也不要用縮寫（don't → do not）。
- 複雜內容用直式清單（vertical list）。
- 相關的句子之間用連接詞（then, but, because, as a result）讓邏輯關係清楚。

範例：
- ✗ "Check pressure, if low replenish."
- ✓ "Read the pressure. If the pressure is low, add fluid."

## 5. 程序寫作

- 每句最多 20 字，越短越好。
- 一句一個指令。只有兩個動作必須同時進行時，才放在同一句。
- 用祈使句（命令句）。
- 句子以條件開頭時（"If...", "When..."），條件和指令之間加逗號。條件一定放在前面。
- Note（注意事項）只用來提供資訊，不能夾帶指令。

範例：
- ✗ "The cover can then be removed and the operator should disconnect the cable, after making sure the power is off."
- ✓
  1. Make sure that the power is off.
  2. Remove the cover.
  3. Disconnect the cable.

## 6. 描述寫作

- 每句最多 25 字。
- 最重要的資訊放最前面（主題句先行）。
- 用段落表現邏輯結構，一段一個主題。
- 每段最多 6 句。

範例：
- ✗ "Due to the fact that the system, which was originally designed in 2019 for a different purpose, has been extended several times, its behavior under load can sometimes be somewhat unpredictable."
- ✓ "The system can be unpredictable under load. The original design was for a different purpose. Engineers extended it several times after 2019."

（注意：「engineers」是改寫者補上的動作者。如果原文沒有說是誰擴充的，就寫成描述狀態或標 `[UNCLEAR]`，不要自己發明。）

## 7. 安全指示

- **WARNING**：可能傷人或致死。**CAUTION**：可能損壞設備或資料。
- 放在它所適用的步驟**之前**。
- 先給一個簡短清楚的命令，再說明具體風險與後果。
- 不要把安全指示寫成一般敘述，也不要在一個 WARNING 裡塞好幾個不相關的風險。

範例：
- ✗ "Be careful, since the capacitor may still hold some charge even after power-off."
- ✓ "WARNING: Discharge the capacitor before you touch it. The capacitor can hold a dangerous voltage after you remove the power."

## 8. 標點與字數計算

- 標點照一般英文用法。
- 不用分號。
- 冒號用來引出直式清單。
- 括號少用，主要用於參照或標籤文字。
- 字數計算：數字、代號、識別碼、標籤文字通常算一個字；有連字號的字算一個字。

## 9. 寫作習慣

- 具體：給數字、單位、名稱，不寫 "properly"、"as needed"、"a while"。
- 指代清楚："it"、"this"、"they" 可能指兩個東西時，直接寫名詞。
- 盡量用肯定句，少用雙重否定。
- 格式一致：相同類型的內容用相同結構。
- 內容複雜時，考慮用表格或圖代替長段文字。
