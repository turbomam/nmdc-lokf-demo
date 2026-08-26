// @ts-check
import { defineConfig } from 'astro/config';
import remarkLokfLinks from './remark-lokf-links.mjs';
import remarkStripLeadingTitle from './remark-strip-leading-title.mjs';

// `site` + `base` are the site's WEB location; the bundle's `base_iri` is the
// RDF identity and is deliberately different. The pages are served from
// GitHub Pages, while concept IRIs are w3id.org so they survive a move. Keep
// these two distinct: `site` must match where the HTML is actually published
// or the canonical link is wrong, and BASE_IRI in src/lib/lokf.ts must match
// knowledge/index.md's base_iri or fallback IRIs will not match the graph.
//
// `base` handles project-page hosting, so the site works both on a custom
// domain (base "/") and as a GitHub project page (base "/<repo>").
// Internal links use the href() helper in src/lib/lokf.ts,
// which prefixes import.meta.env.BASE_URL. The remark plugins rewrite concept
// `.md` cross-links to base-aware routes and drop a body's redundant leading
// `# Title` (the layout renders it from frontmatter).
export default defineConfig({
  site: 'https://turbomam.github.io',
  base: '/nmdc-lokf-demo',
  markdown: {
    remarkPlugins: [
      [remarkLokfLinks, { base: '/nmdc-lokf-demo' }],
      remarkStripLeadingTitle,
    ],
  },
});
