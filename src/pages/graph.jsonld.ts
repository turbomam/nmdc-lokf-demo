import type { APIRoute } from 'astro';
import { loadBundle, iriOf, resolveRef, RELATION_SLOTS } from '../lib/lokf';

/** The LOKF JSON-LD context published by the lokf project, pinned.
 *
 * a723ac0a8ab84b910f55d1f714de980ed49ebe8c is the commit tagged v0.5.0 upstream, matching the `lokf==0.5.0` this
 * repository pins everywhere else. It was on `main` before, which meant every
 * term in the published graph meant whatever that file said at the moment a
 * consumer resolved it: an upstream edit would have changed this graph's
 * semantics with no commit here and nothing to notice.
 *
 * A commit rather than the tag, because a tag can be moved and a commit cannot,
 * and vocabulary drift is invisible in a way tooling drift is not. Tooling
 * drift breaks a build; this would have broken nothing and changed meaning.
 *
 * Verified identical to `main` and to the context inside the installed 0.5.0
 * wheel when pinned, so this changed stability and not semantics.
 */
const CONTEXT =
  'https://raw.githubusercontent.com/nicholsn/lokf/a723ac0a8ab84b910f55d1f714de980ed49ebe8c/lokf.context.jsonld';

/**
 * The whole bundle as one JSON-LD document — this is the LOKF thesis: the
 * concepts' frontmatter, with the published @context attached, IS the RDF
 * graph. Load it with any JSON-LD/RDF tool.
 */
export const GET: APIRoute = async () => {
  const { concepts } = await loadBundle();
  const graph = concepts.map((c) => {
    const data = { ...(c.data as Record<string, unknown>) };
    // Resolve bundle-relative relation targets to full IRIs so the RDF edges
    // are unambiguous (mirrors the toolkit); `id` = the concept's own IRI.
    for (const slot of RELATION_SLOTS) {
      const v = data[slot];
      if (v === undefined) continue;
      data[slot] = (Array.isArray(v) ? v : [v]).map((t) =>
        typeof t === 'string' ? resolveRef(t) : t,
      );
    }
    return { ...data, id: iriOf(c), ...(c.body ? { body: c.body } : {}) };
  });
  const doc = { '@context': CONTEXT, '@graph': graph };
  return new Response(JSON.stringify(doc, null, 2), {
    headers: { 'Content-Type': 'application/ld+json; charset=utf-8' },
  });
};
