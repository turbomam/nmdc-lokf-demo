import type { APIRoute } from 'astro';
import { readFileSync } from 'node:fs';

/**
 * The committed Turtle, served at the origin that names the concepts.
 *
 * Serves `knowledge.ttl` from the repository root rather than regenerating the
 * projection here. That file is produced by `just ttl` (the Python toolkit) and
 * CI fails if it has drifted from the concepts, so publishing it means what a
 * consumer fetches is exactly the artifact already guarded. Re-deriving Turtle
 * in TypeScript would be a second projection to keep in step with the first,
 * and this repository has spent the day paying for pairs of code paths that
 * were supposed to agree.
 *
 * GitHub Pages does not set `text/turtle` for a `.ttl` file, which is why this
 * is an endpoint rather than something dropped in `public/`.
 */
export const GET: APIRoute = () => {
  const ttl = readFileSync(new URL('../../knowledge.ttl', import.meta.url), 'utf8');
  return new Response(ttl, {
    headers: { 'Content-Type': 'text/turtle; charset=utf-8' },
  });
};
