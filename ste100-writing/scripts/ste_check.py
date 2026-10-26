#!/usr/bin/env python3
"""Heuristic checker for ASD-STE100 Simplified Technical English style.

Usage:
    python ste_check.py FILE [--json] [--max-proc 20] [--max-desc 25] [--max-para 6]
    python ste_check.py - < draft.md

Each finding is a hint to look at, not proof of a rule violation. The checker
does not know the official STE dictionary, cannot check meaning or term
consistency, and only guesses whether a sentence is a procedure or a description.
Markdown code blocks, inline code, URLs, headings and tables are skipped.
"""
import argparse
import json
import re
import sys

# Pattern -> suggestion. Keep in sync with references/word-swaps.md.
SWAPS = [
    (r"utili[sz](?:e|es|ed|ing|ation)", "use"),
    (r"ensur(?:e|es|ed|ing)", "make sure"),
    (r"commenc(?:e|es|ed|ing)", "start"),
    (r"initiat(?:e|es|ed|ing)", "start"),
    (r"terminat(?:e|es|ed|ing)", "stop / end"),
    (r"obtain(?:s|ed|ing)?", "get"),
    (r"acquir(?:e|es|ed|ing)", "get"),
    (r"assist(?:s|ed|ing)?", "help"),
    (r"facilitat(?:e|es|ed|ing)", "help"),
    (r"perform(?:s|ed|ing)?", "do"),
    (r"accomplish(?:es|ed|ing)?", "do"),
    (r"requir(?:e|es|ed|ing)", "must have / is necessary / need"),
    (r"indicat(?:e|es|ed|ing)", "show"),
    (r"demonstrat(?:e|es|ed|ing)", "show"),
    (r"modif(?:y|ies|ied|ying)", "change"),
    (r"attempt(?:s|ed|ing)?", "try"),
    (r"endeavou?r(?:s|ed|ing)?", "try"),
    (r"eliminat(?:e|es|ed|ing)", "remove"),
    (r"retain(?:s|ed|ing)?", "keep"),
    (r"resid(?:e|es|ed|ing)", "be (in)"),
    (r"notif(?:y|ies|ied|ying)", "tell"),
    (r"possess(?:es|ed|ing)?", "have"),
    (r"leverag(?:e|es|ed|ing)", "use"),
    (r"purchas(?:e|es|ed|ing)", "buy"),
    (r"make use of", "use"),
    (r"(?:is|are) able to", "can"),
    (r"ha(?:s|ve) the ability to", "can"),
    (r"it is possible to", "you can"),
    (r"set(?:s|ting)? up", "install / configure / make (say which)"),
    (r"carr(?:y|ies|ied|ying) out", "do"),
    (r"figur(?:e|es|ed|ing) out", "find"),
    (r"f(?:ind|inds|ound|inding) out", "find"),
    (r"look(?:s|ed|ing)? into", "examine"),
    (r"c(?:ome|omes|ame|oming) up with", "make / find"),
    (r"go(?:es|ing)? through|went through", "read / examine"),
    (r"point(?:s|ed|ing)? out", "show / tell"),
    (r"prior to", "before"),
    (r"subsequent(?:ly| to)", "after / then"),
    (r"(?:due|owing) to the fact that", "because"),
    (r"in the event that", "if"),
    (r"in order to", "to"),
    (r"at (?:this point in time|the present time)", "now"),
    (r"a number of", "some / many / the number"),
    (r"a variety of", "different / many"),
    (r"numerous", "many"),
    (r"sufficient(?:ly)?", "enough"),
    (r"additionally|in addition", "also"),
    (r"with (?:regard|respect) to|in terms of|regarding", "about"),
    (r"functionality", "function"),
]

FILLER = [
    r"it is (?:worth noting|important to note|important to remember) that",
    r"it's worth noting that",
    r"please note that",
    r"needless to say",
    r"basically",
    r"essentially",
    r"actually",
    r"simply",
    r"obviously",
    r"of course",
    r"in today's world",
    r"at the end of the day",
    r"seamless(?:ly)?",
    r"delv(?:e|es|ed|ing) into",
    r"(?:might|could|may) potentially",
]

IMPERATIVE_VERBS = set("""
add adjust align apply assemble attach build calculate call change check choose clean clear click close
compile configure connect copy create cut delete deploy disable disassemble discard disconnect do download
drag drain drop edit enable enter examine fasten fill find follow get give go grease hold inspect install
insert keep let lift load lock log loosen lower lubricate make mark measure monitor move note open operate
paste pick plug point pour prepare press pull push put raise read reboot record refer release reload remove
repeat replace reset restart rotate run save scroll see select send set shut sign start stop switch tap
tighten touch turn type unlock unplug update upload use verify view wait wipe write
""".split())

ABBREVIATIONS = {
    "e.g", "i.e", "etc", "vs", "mr", "mrs", "ms", "dr", "fig", "no", "approx", "min", "max", "ref",
    "para", "vol", "inc", "ltd", "co", "jan", "feb", "mar", "apr", "jun", "jul", "aug", "sep",
    "sept", "oct", "nov", "dec", "u.s", "u.k", "st", "nr",
}

IRREGULAR_PARTICIPLES = set("""
built done made sent set put kept held found given taken written shown known seen cut left lost paid sold
told brought bought caught taught thought understood chosen driven frozen hidden stolen spoken broken worn
torn drawn grown thrown begun hung shut spent lent bent meant dealt felt led fed fit hit lit won bound
wound ground split spread cast quit upset forgotten gotten
""".split())

NOT_PARTICIPLE = set("""
often open even seven eleven ten then when token garden heaven oxygen children kitchen women men citizen
screen green between queen teen need speed feed seed bed shed bleed embed exceed proceed succeed indeed
breed hundred sacred
""".split())

NOT_ING = set("""
thing things something anything nothing everything during string strings spring ring rings king wing wings
bring brings sing sting swing cling fling sling ceiling morning evening pudding
""".split())

PASSIVE_RE = re.compile(
    r"\b(am|is|are|was|were|be|been|being)\s+(?:(?:not|also|then|only|now|\w+ly)\s+)?([a-z]+)\b",
    re.IGNORECASE,
)
CONTRACTION_RE = re.compile(r"\b[A-Za-z]+(?:n't|'re|'ll|'ve|'d|'m)\b|\b(?:it|that|there|what|let)'s\b", re.IGNORECASE)
ING_RE = re.compile(r"\b([A-Za-z]{2,}ing)\b")
VAGUE_REF_RE = re.compile(
    r"^(This|That|These|Those|It)\s+(is|are|was|were|means|meant|makes|made|will|can|could|may|might|should|"
    r"would|does|did|has|have|allows|lets|causes|gives|shows|helps)\b"
)
SHOULD_RE = re.compile(r"\bshould\b", re.IGNORECASE)
TWO_INSTRUCTIONS_RE = re.compile(r"(?:\band\b|\bthen\b|,)\s+(?:then\s+)?(?:[a-z]+ly\s+)?([a-z]+)\b", re.IGNORECASE)
LIST_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")
WORD_RE = re.compile(r"[A-Za-z0-9][\w'’\-./%°·]*")


def compile_list(patterns):
    return [re.compile(r"\b(?:" + p + r")\b", re.IGNORECASE) for p in patterns]


SWAP_RES = [(re.compile(r"\b(?:" + p + r")\b", re.IGNORECASE), s) for p, s in SWAPS]
FILLER_RES = compile_list(FILLER)


def mostly_cjk(text):
    letters = [c for c in text if not c.isspace()]
    if not letters:
        return False
    cjk = sum(1 for c in letters if "　" <= c <= "鿿" or "豈" <= c <= "﫿")
    return cjk / len(letters) > 0.3


def to_blocks(text):
    """Split markdown into prose blocks. Return list of (kind, [(line_no, text), ...]).

    kind is "para" for a normal paragraph or "item" for one list item.
    """
    blocks = []
    current = []
    kind = "para"
    in_fence = False

    def flush():
        nonlocal current
        if current:
            blocks.append((kind, current))
        current = []

    for no, raw in enumerate(text.splitlines(), start=1):
        line = raw.rstrip()
        if re.match(r"^\s*(```|~~~)", line):
            flush()
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("|") or re.match(r"^[-=*_]{3,}$", stripped):
            flush()
            kind = "para"
            continue
        stripped = re.sub(r"^>\s?", "", stripped)
        if LIST_RE.match(stripped):
            flush()
            kind = "item"
            stripped = LIST_RE.sub("", stripped)
        stripped = re.sub(r"`[^`]*`", "CODE", stripped)
        stripped = re.sub(r"https?://\S+", "URL", stripped)
        stripped = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", stripped)
        stripped = stripped.replace("**", "").replace("__", "")
        current.append((no, stripped))
    flush()
    return blocks


def split_sentences(text):
    """Return list of (offset, sentence)."""
    sentences = []
    start = 0
    for m in re.finditer(r"[.!?]+(?=[\"')\]”’]*(?:\s|$))", text):
        end = m.end()
        before = text[start:m.start()]
        last = re.findall(r"[A-Za-z][A-Za-z.]*$", before)
        if m.group() == "." and last and last[0].lower().rstrip(".") in ABBREVIATIONS:
            continue
        rest = text[end:].lstrip(" \"')]”’")
        if rest and not (rest[0].isupper() or rest[0].isdigit() or rest[0] in "\"'([*`“"):
            continue
        chunk = text[start:end]
        lead = len(chunk) - len(chunk.lstrip())
        if chunk.strip():
            sentences.append((start + lead, chunk.strip()))
        start = end
    chunk = text[start:]
    if chunk.strip():
        lead = len(chunk) - len(chunk.lstrip())
        sentences.append((start + lead, chunk.strip()))
    return sentences


def instruction_part(sentence):
    """Drop a leading condition: "If X, do Y." -> "do Y."."""
    s = sentence.strip(" \"'*")
    if re.match(r"^(If|When|After|Before|While|Until)\b", s) and "," in s:
        s = s.split(",", 1)[1].strip()
    return s


def is_procedure(sentence):
    s = instruction_part(sentence)
    words = s.split()
    if not words:
        return False
    first = re.sub(r"[^a-z]", "", words[0].lower())
    if first in ("do", "never", "always") or s.lower().startswith("make sure"):
        return True
    return first in IMPERATIVE_VERBS


def snippet(sentence, limit=70):
    return sentence if len(sentence) <= limit else sentence[: limit - 3] + "..."


def check(text, max_proc, max_desc, max_para):
    findings = []
    stats = {"sentences": 0, "paragraphs": 0, "procedure_like": 0, "description_like": 0}

    def add(line, severity, rule, message):
        findings.append({"line": line, "severity": severity, "rule": rule, "message": message})

    for kind, lines in to_blocks(text):
        joined = ""
        starts = []
        for no, part in lines:
            starts.append((len(joined), no))
            joined += part + " "

        def line_of(offset):
            line = starts[0][1]
            for pos, no in starts:
                if pos <= offset:
                    line = no
            return line

        sentences = split_sentences(joined)
        if kind == "para":
            stats["paragraphs"] += 1
            if len(sentences) > max_para:
                add(starts[0][1], "ERROR", "paragraph-length",
                    f"paragraph has {len(sentences)} sentences (max {max_para})")

        for offset, sent in sentences:
            line = line_of(offset)
            stats["sentences"] += 1
            words = WORD_RE.findall(sent)
            proc = is_procedure(sent)
            stats["procedure_like" if proc else "description_like"] += 1
            limit = max_proc if proc else max_desc
            if len(words) > limit:
                label = "procedure" if proc else "description"
                add(line, "ERROR", "sentence-length",
                    f"{len(words)} words ({label}, max {limit}): \"{snippet(sent)}\"")

            for m in PASSIVE_RE.finditer(sent):
                word = m.group(2).lower()
                if word in NOT_PARTICIPLE:
                    continue
                if re.fullmatch(r"[a-z]{2,}(?:ed|en)", word) or word in IRREGULAR_PARTICIPLES:
                    tail = sent[m.end():m.end() + 4].lower()
                    note = " followed by 'by'" if tail.startswith(" by") else ""
                    add(line, "WARN", "passive",
                        f"possible passive \"{m.group(0)}\"{note}. OK if it describes a state "
                        f"(the valve is closed); if it is an action, use active voice")

            for m in CONTRACTION_RE.finditer(sent):
                add(line, "WARN", "contraction", f"\"{m.group(0)}\": write the full form")

            if ";" in sent:
                add(line, "WARN", "semicolon", "semicolon: split into two sentences or use a list")

            for rx, suggestion in SWAP_RES:
                for m in rx.finditer(sent):
                    add(line, "WARN", "word-choice", f"\"{m.group(0)}\" -> {suggestion}")

            for rx in FILLER_RES:
                for m in rx.finditer(sent):
                    add(line, "WARN", "filler", f"\"{m.group(0)}\": delete or rewrite")

            if VAGUE_REF_RE.match(sent):
                add(line, "INFO", "vague-reference",
                    f"sentence starts with \"{sent.split()[0]}\" + verb: name the thing if it can be unclear")

            if proc:
                for m in TWO_INSTRUCTIONS_RE.finditer(instruction_part(sent)):
                    if m.group(1).lower() in IMPERATIVE_VERBS:
                        add(line, "WARN", "two-instructions",
                            f"\"{m.group(0).strip(', ')}\": one instruction per sentence, unless the "
                            f"actions happen at the same time")
                        break

            if proc and SHOULD_RE.search(sent):
                add(line, "INFO", "should", "\"should\" in an instruction: use a command")

            for m in ING_RE.finditer(sent):
                if m.group(1).lower() in NOT_ING or m.group(1)[0].isupper() and m.start() > 0:
                    continue
                add(line, "INFO", "ing-form",
                    f"\"{m.group(1)}\": -ing is OK only inside a technical noun")

    return stats, findings


def main():
    ap = argparse.ArgumentParser(description="Heuristic ASD-STE100 style checker.")
    ap.add_argument("file", help="text or markdown file, or - for stdin")
    ap.add_argument("--json", action="store_true", help="print JSON")
    ap.add_argument("--max-proc", type=int, default=20, help="max words in a procedure sentence")
    ap.add_argument("--max-desc", type=int, default=25, help="max words in a description sentence")
    ap.add_argument("--max-para", type=int, default=6, help="max sentences in a paragraph")
    args = ap.parse_args()

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    if args.file == "-":
        if hasattr(sys.stdin, "reconfigure"):
            sys.stdin.reconfigure(encoding="utf-8", errors="replace")
        text = sys.stdin.read()
    else:
        with open(args.file, encoding="utf-8", errors="replace") as f:
            text = f.read()

    if mostly_cjk(text):
        print("Text is mostly Chinese/Japanese/Korean. This checker only works for English.")
        return

    stats, findings = check(text, args.max_proc, args.max_desc, args.max_para)
    order = {"ERROR": 0, "WARN": 1, "INFO": 2}
    findings.sort(key=lambda f: (f["line"], order[f["severity"]]))
    counts = {s: sum(1 for f in findings if f["severity"] == s) for s in order}

    if args.json:
        print(json.dumps({"stats": stats, "counts": counts, "findings": findings}, indent=2, ensure_ascii=False))
        return

    print(f"Checked {stats['sentences']} sentences in {stats['paragraphs']} paragraphs "
          f"({stats['procedure_like']} look like procedures, {stats['description_like']} like descriptions).")
    for f in findings:
        print(f"line {f['line']:>4}  {f['severity']:<5}  {f['rule']:<16} {f['message']}")
    print(f"\n{counts['ERROR']} errors, {counts['WARN']} warnings, {counts['INFO']} info.")
    print("Not checked: meaning, term consistency, multi-word nouns, official STE dictionary.")


if __name__ == "__main__":
    main()
