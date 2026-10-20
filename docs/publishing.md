# Publishing: the dataset id, and repacking a raw archive

Publishing itself (layout, catalog, releases) is described in `cybertron/publish.py`'s docstring and in
[data_format.md](data_format.md) ("Layout on Hugging Face", "Versions and releases"). This page covers two maintenance tasks.

## The dataset id

The Hugging Face dataset id is written once in code:

- Python: `DATASET` in `cybertron/publish.py`. `publish.default_repo()` returns `$CYBERTRON_DATASET` when that is set, else
  `DATASET`; `--repo` on the command line overrides both.
- Site: `DATASET_REPO` in `site/lib/cybertron-data.js`. `site/assets/site.js` re-exports it (with `DATASET_URL`), the run page
  passes it to `views.js`, and `index.html` fills its dataset link and its DuckDB example from it.

`tests/test_dataset_naming.py` fails if the id is written anywhere else in Python, the site or the tests.

Prose links are left literal. When the dataset is renamed (e.g. to `zachmacsmith/cybertron-runs`), change the two constants and
then the prose in one pass:

    git grep -l "zachmacsmith/charter-runs" -- README.md docs/data_format.md \
      | xargs sed -i 's#zachmacsmith/charter-runs#zachmacsmith/cybertron-runs#g'
    sed -i 's#dataset-charter--runs#dataset-cybertron--runs#' README.md            # the shields.io badge escapes "-" as "--"

`docs/review/*.md` are dated review notes; they keep the name the dataset had when they were written.

## Repacking a published raw archive

When `publish.NEVER` gains a pattern (files that must never be public), archives already on the Hub may still hold such
members. `repack_remote_archive` rebuilds one of them in place:

1. download `raw/<spec>/<run_id>.tar.gz` from the dataset;
2. copy it member by member without the members `NEVER` matches (and any absolute or `..` member, link or device); kept members
   keep their names, sizes, mtimes and modes, nothing is extracted;
3. update the catalog rows whose `raw` is that path, for the archive facts they record (`ARCHIVE_FIELDS`: `bytes_archive`,
   `bytes_raw`, `raw_files`, `raw_sha256`, `archive_sha256`). Today's catalog records none of them, only the `raw` path, so
   normally only the archive is uploaded; `rows_json` counts table rows and does not change;
4. upload the new archive (with `catalog.json` / `catalog.parquet` when a row changed) in one commit, no deletions.

Without `--push` (or with `dry_run=True`, the default) nothing is uploaded: the summary lists the members that would be dropped,
sizes and sha256 before and after, and the staging directory holding the repacked archive. When no member is dropped nothing is
uploaded either.

    python -m cybertron publish --repack-raw raw/E0/pub1.tar.gz                      # dry run: report only
    python -m cybertron publish --repack-raw raw/E0/pub1.tar.gz --push               # upload the repacked archive
    python -m cybertron publish --repack-raw raw/E0/pub1.tar.gz --repo me/data --staging /tmp/repack1

    from cybertron import publish as P
    s = P.repack_remote_archive("zachmacsmith/charter-runs", "raw/E0/pub1.tar.gz", dry_run=True)
    s["dropped"], s["before"], s["after"], s["catalog_updated"]

To repack every published archive, loop over `P.remote_catalog(repo)` and pass each row's `raw`.

The old archive stays in the dataset's git history (and in any tag, e.g. a release, that points at an earlier commit). If the
dropped members must disappear entirely, the history has to be rewritten as well (e.g. `HfApi.super_squash_history` on main; tags
that point at older commits keep the old archive until they are deleted or moved); decide that separately, it is not done here. A repack is a PATCH-level change at most; mention it in the
next release's notes.
