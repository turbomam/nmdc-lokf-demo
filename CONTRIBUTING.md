# Contributing

Small repo, short rules. The one that has actually been violated here, five times in a
single day, is the merge gate immediately below.

## Before you merge

**A pull request is ready when all six conditions below hold.** Not when the checks are green,
not when the newest review happens to report nothing, and not when you believe the findings are
addressed. A clean current review is necessary and not sufficient: it says nothing about a
suppressed finding on a superseded review, an unanswered thread, or a check still running. All
three of those have blocked a pull request here while the newest review was clean.

Those are different things, and the difference cost this repository five real findings on
2026-08-26, through two distinct failures.

**Merged before the review existed.** Pull request 16 was merged 95 seconds before its review
posted, and 17 by 36 seconds. Two Copilot jobs were visibly `in_progress` at the time.

**Merged past a review that did exist.** Pull request 7's review posted 157 seconds *before*
the merge and nobody read it. No timing discipline would have caught that one; only looking
would have.

The second is the worse habit, and the easier one to excuse. One of the five findings was a
design flaw in the guard whose whole job is catching mistakes.

The check is mechanical:

```bash
just ready 18        # or: ~/bin/pr-ready.sh <owner>/<repo> <number>
```

It exits nonzero unless all of these hold:

- a Copilot review exists **whose `commit_id` equals the head SHA**, so it saw exactly this code.
  Compare the SHAs, not the timestamps: a commit's date is set locally when you commit, so a
  review can post after that date and still have examined the previous head, if you pushed
  afterwards. A newer timestamp does not prove a newer subject.
- that review has no inline comments
- that review has no **suppressed** comments
- no superseded review has unaddressed suppressed comments
- every review thread has a reply
- no check is failing or still running

### If you do not have `pr-ready.sh`

Then the gate did not run, and you should not say it passed.

There was a hand-written version of the six checks here. It was removed after five review
rounds found five different ways it was wrong: a `--jq` filter evaluated once per page so
answered threads read as unanswered, a missing `--paginate` that would drop the newest review
past 30 rounds, a reply filter accepting any account, an incomplete list presented as the whole
check, and a headline rule weaker than the six conditions under it.

Each of those was a real bug in a second implementation of a tool that already exists. Nothing
exercised the copy, so nothing caught them until a reviewer did, one per round. Install the
helper instead.

Its own known flaw is worth knowing: it compares review timestamps rather than the reviewed
`commit_id`, which cannot prove a review saw the head commit. Tracked at
https://github.com/turbomam/bin/issues/134

## Suppressed comments are the ones you will miss

Copilot hides findings it judged low confidence inside a `<details>` block in the **review
body**. They are not review threads and not review comments, so they appear in no thread query
and no `pulls/N/comments` result. A thread audit reports clean while they sit unread.

```bash
gh api repos/<owner>/<repo>/pulls/<n>/reviews \
  --jq '.[] | select(.body|test("Suppressed")) | .body'
```

Four of the five findings missed here were of this kind or arrived post-merge. Once a pull
request is merged, its unaddressed comments vanish from every normal surface.

## Reply in the thread, not in a new comment

Answer each finding as a reply to that inline thread, so the conversation stays where the
reviewer left it. Three outcomes are all legitimate: fix it, file an issue and say where it
went, or explain why it does not apply. Never leave one unanswered.

## When rounds keep coming, change the approach

A rising or repeating finding count means the fixes are creating review surface faster than
they close it. On https://github.com/turbomam/nmdc-lokf-demo/pull/18 five rounds each refuted a
tighter claim than the last, because the paragraph kept trying to summarise what 616 lines of
someone else's agent instructions do. The fix was to stop claiming and start pointing. Read the
pattern, not the count.

## When a claim changes, change every copy of it

The same pull request corrected a claim four times in a file while its **description** still
carried the original wording. Editing the document is not enough: the description, the issue,
and any doc that repeats it all need the correction, because reviewers read the description.

## The rest

- Regenerate derived files with `just ttl`. `just check` is read-only and is what CI runs.
- Name concepts at an origin that resolves. Every subject IRI should dereference.
- Say how a claim is known. Measured, observed once, or read from the source.
