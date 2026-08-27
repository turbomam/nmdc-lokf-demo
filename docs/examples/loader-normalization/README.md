# Loader normalization: two values, four runs, three verdicts

A reduced case for the finding in [../../atlas-as-linkml.md](../../atlas-as-linkml.md). One
schema, one required multivalued slot, and two semantically different values (an empty list and
a null), each serialised as YAML and as JSON.

```
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T empty.yaml   # No issues found
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T empty.json   # 'tags' is a required property in /
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T null.yaml    # None is not of type 'array' in /tags
uvx --from 'linkml==1.11.1' linkml-validate -s s.yaml -C T null.json    # 'tags' is a required property in /
```

Four runs, three distinct verdicts. `empty.yaml` passes and `empty.json` fails on the same
data, because LinkML's JSON loader runs `json_clean` and strips empty collections and nulls,
while the YAML loader passes `yaml.safe_load_all` output through unchanged. The presence check
then fires on a document that no longer contains the key.

The two JSON runs matter precisely because they agree. An empty list and a null are different
values, and the YAML column shows the validator treating them differently, one accepted and one
a type error. In the JSON column both produce the identical presence error, word for word the
one an absent key produces. Two distinct inputs collapsing onto the same verdict is what
identifies a normalization step rather than a stricter rule.

`lokf validate` reaches the JSON path because it writes a temporary `.bundle.json`, so a bundle
author sees the JSON behaviour without ever writing JSON.

Measured on linkml 1.11.1. Pin the version when re-running: this is loader behaviour and could
reasonably change.
