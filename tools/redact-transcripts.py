#!/usr/bin/env python3
"""Make a role's transcript publishable, by fixed rules.

    tools/redact-transcripts.py claude SRC.jsonl OUT.jsonl
    tools/redact-transcripts.py codex  SRC      OUT   (also any text file)

The agent's own work is kept whole: every prompt it was given, every
message it wrote, every tool call and every tool result. Only context the
agent tooling injected on the owner's behalf is removed, and each removal
leaves a marker saying what kind of thing it was. The rules (also in
transcripts/README.md):

1. claude: only the conversation is kept: the `user` and `assistant`
   entries, and every message sent to the agent while it worked (the
   `queued_command` attachments), with their timestamps. The tooling's own bookkeeping entries
   (`api-request*`, `attachment`, `data-flow-records` and the like) are
   dropped.
2. claude: each <system-reminder> block is kept if it is one of the
   harmless kinds listed in KEEP (the date, the model, a file-changed
   note, the hand-back instruction, the commit attribution line, auto
   mode), and otherwise replaced by
   "[redacted by tools/redact-transcripts.py: KIND]". The kinds removed:
   the owner's Claude memory index; the lists of the owner's connected
   tools, MCP servers and their instructions, skills and agent types; the
   environment description; anything else not on the KEEP list.
3. claude: where an agent's own text paraphrases the memory index's
   entries, the paraphrase is replaced by a marker; the agent's statement
   that the index was put into its context is kept.
4. both: the owner's home directory is written as ~ ("/Users/<name>" and
   the "-Users-<name>-" form of project folder names), and the account
   name anywhere else (the owner column of `ls -l`, for instance) as
   <owner>, and the owner's email address (in `git log` output, for
   instance) as <owner-email>.

After writing, the output is screened for what the rules are meant to
remove, and the script fails if any of it is left.
"""
import json, re, sys

HOME = "/Users/christopherhay"
HOME_DASH = "-Users-christopherhay-"
USER = "christopherhay"
EMAIL = re.compile(r"[\w.+-]+@googlemail\.com")
KEEP = ("Today's date", "You are powered by", "Note: ", "Your final report is delivered",
        "Attribution for git commits", "While auto mode", "<artifact-content-authored-by-others/>",
        "Called the Read tool", "Result of calling the Read tool")
KINDS = [("MEMORY.md", "the owner's Claude memory index"),
         ("tools just became available", "the owner's connected tools (list)"),
         ("deferred tools", "the owner's connected tools (list)"),
         ("MCP Server Instructions", "instructions of the owner's MCP servers"),
         ("skills are available", "the owner's installed skills (list)"),
         ("Available agent types", "the agent types available (list)"),
         ("# Environment", "the environment description"),
         ("userEmail", "the owner's account context")]
SCREEN = re.compile(r"googlemail|@gmail|absys-sources-access|Absys sources access|no-commit-trailers|No commit trailers|"
                    r"source papers and commit trailers|Absys(?:\s|\\n)+sources|commit(?:\s|\\n)+trailers|mcp__|"
                    r"claude_ai_|creator-os|chuk-experiments|chuk-train|Google_Drive|Gmail|Canva|"
                    r"userEmail|christopherhay|gh[pousr]_[A-Za-z0-9]{30}|sk-ant-|AGE-SECRET-KEY-1[0-9A-Z]{50}")
REM = re.compile(r"<system-reminder>(.*?)</system-reminder>", re.S)
counts = {}


def reminder(m):
    body = re.sub(r"^(?:\s|\\n)+", "", m.group(1)).strip()
    if body.startswith("[redacted by tools/redact-transcripts.py:"):
        return m.group(0)
    if any(body.startswith(k) or body[:200].find(k) == 0 for k in KEEP) and not SCREEN.search(body):
        return m.group(0)
    kind = next((k for p, k in KINDS if p in body), "other context injected by the tooling")
    counts[kind] = counts.get(kind, 0) + 1
    return f"<system-reminder>[redacted by tools/redact-transcripts.py: {kind}]</system-reminder>"


# Each agent's own words for what the memory index's entries are about.
# Words may be split by spaces, line breaks, or an escaped "\\n" in JSON.
PARAPHRASES = ["two one-line entries about absys source papers and commit trailers",
               "titles only: one on access to Absys sources, one on commit trailers",
               "titles on access to Absys sources and on commit trailers",
               "two titles, about Absys sources and commit trailers",
               "two lines about commit trailers and Absys sources",
               "about a different project's sources and commit trailers"]
SEP = r"(?:\s|\\n)+"
PARA = re.compile("|".join(SEP.join(re.escape(w) for w in p.split()) for p in PARAPHRASES))


def clean(x):
    if isinstance(x, str):
        n = len(PARA.findall(x))
        if n:
            counts["an agent's paraphrase of the memory index entries"] = counts.get("an agent's paraphrase of the memory index entries", 0) + n
            x = PARA.sub("[redacted by tools/redact-transcripts.py: what the entries are about]", x)
        x = EMAIL.sub("<owner-email>", x)
        return REM.sub(reminder, x).replace(HOME_DASH, "-HOME-").replace(HOME, "~").replace(USER, "<owner>")
    if isinstance(x, list):
        return [clean(v) for v in x]
    if isinstance(x, dict):
        return {k: clean(v) for k, v in x.items()}
    return x


def main(kind, src, out):
    lines = []
    if kind == "claude":
        for l in open(src, encoding="utf-8"):
            d = json.loads(l)
            a = d.get("attachment") or {}
            if d.get("type") == "attachment" and a.get("type") == "queued_command":
                lines.append(json.dumps({"type": "queued_command", "timestamp": d.get("timestamp"),
                                         "prompt": clean(a.get("prompt"))}, ensure_ascii=False))
                continue
            if d.get("type") not in ("user", "assistant"):
                counts["tooling bookkeeping entries (dropped)"] = counts.get("tooling bookkeeping entries (dropped)", 0) + 1
                continue
            lines.append(json.dumps({"type": d["type"], "timestamp": d.get("timestamp"),
                                     "message": clean(d.get("message"))}, ensure_ascii=False))
    else:
        lines = [clean(open(src, encoding="utf-8").read().rstrip("\n"))]
    text = "\n".join(lines) + "\n"
    left = sorted(set(SCREEN.findall(text)))
    if left:
        sys.exit(f"{src}: still contains {left}")
    open(out, "w", encoding="utf-8").write(text)
    print(json.dumps({"source": src.replace(HOME, "~"), "out": out, "redactions": counts}))


if __name__ == "__main__":
    main(*sys.argv[1:4])
