// @ts-check
import { defineConfig } from 'astro/config';
import remarkLokfLinks from './remark-lokf-links.mjs';
import remarkStripLeadingTitle from './remark-strip-leading-title.mjs';

// `site` + `base` are where the HTML is published, and the bundle's `base_iri`
// is deliberately the same origin, so every concept IRI dereferences to that
// concept's own page. An earlier version named concepts under w3id.org, which
// was never registered, so all six subjects 404'd. If a permanent identifier
// is wanted later, register w3id.org/turbomam first and move the IRIs after,
// not before. BASE_IRI in src/lib/lokf.ts must keep matching
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
