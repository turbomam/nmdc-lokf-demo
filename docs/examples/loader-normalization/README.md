# Loader normalization: the same data, four verdicts

A reduced case for the finding in [../../atlas-as-linkml.md](../../atlas-as-linkml.md). One
schema, one required multivalued slot, one value expressed four ways.

```
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T empty.yaml   # No issues found
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T empty.json   # 'tags' is a required property in /
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T null.yaml    # None is not of type 'array' in /tags
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T null.json    # 'tags' is a required property in /
```

`empty.yaml` passes and `empty.json` fails on the same data, because LinkML's JSON loader runs
`json_clean` and strips empty collections and nulls, while the YAML loader passes
`yaml.safe_load_all` output through unchanged. The presence check then fires on a document that
no longer contains the key.

`lokf validate` reaches the JSON path because it writes a temporary `.bundle.json`, so a bundle
author sees the JSON behaviour without ever writing JSON.

Measured on linkml 1.11.1. Pin the version when re-running: this is loader behaviour and could
reasonably change.
