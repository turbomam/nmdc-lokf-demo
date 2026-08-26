# Contributing

Small repo, short rules. The only one that has actually been violated here is the last one.

## Before you merge

**A pull request is ready when a Copilot review that examined the current code reports
nothing.** Not when the checks are green, and not when you believe the findings are addressed.

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

- a Copilot review exists **whose timestamp is newer than the head commit**, so it saw this code
- that review has no inline comments
- that review has no **suppressed** comments
- no superseded review has unaddressed suppressed comments
- every review thread has a reply
- no check is failing or still running

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
