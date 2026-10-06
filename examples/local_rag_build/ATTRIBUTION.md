# Attribution & licensing

Every full-text paper under `corpus/` is **open access** and redistributed here
under a license that permits redistribution **and** derivative works (cleaning,
chunking, embedding). Per-paper provenance is in [`manifest.csv`](manifest.csv)
(`doi`, `publisher`, `crossref_license`, `unpaywall_license`, `oa_status`).

## How this set was vetted

- **1000** papers were first sampled from 10 fully-OA publishers (judged by DOI
  prefix): PLOS, MDPI, BMC, Frontiers, PeerJ, eLife, F1000Research, Hindawi,
  Copernicus, JMIR.
- Each DOI was then **license-audited against both Crossref and Unpaywall**
  (see [`LICENSE_AUDIT.csv`](LICENSE_AUDIT.csv), all 1000 rows).
- Only papers classified **GREEN** were kept: license ∈ {CC-BY, CC-BY-SA, CC0,
  public-domain}. Result: **973** papers.
- **27 were excluded** and are *not* redistributed here:
  - 5 carry a **no-derivatives** license (CC-BY-NC-ND) — cleaning/chunking would
    be a prohibited derivative;
  - 1 is **CC-BY-NC** (non-commercial restriction);
  - 2 have **no usable open license** (gold "free to read" ≠ redistributable);
  - 19 are **conservative holds** (Crossref exposes only a TDM license while
    Unpaywall reports CC-BY; very likely CC-BY but not confirmed, so dropped).

## Attribution

Each paper is © its authors and is reproduced under its stated CC license.
Cite the original work via the `doi` in `manifest.csv`. CC-BY / CC-BY-SA require
attribution to the original authors; CC0 / public-domain do not but attribution
is still provided for provenance.

This example corpus is provided for **research reproducibility** of the DToR
local-RAG pipeline.
