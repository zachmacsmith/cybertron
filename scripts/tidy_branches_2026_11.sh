#!/usr/bin/env bash
# One-off (6 Nov 2026): delete the 56 branches listed in docs/branches.md. Their commits are all in main or archive.
# Run from any clone of zachmacsmith/cybertron with push access: bash scripts/tidy_branches_2026_11.sh
# A branch whose tip has moved since the tidy-up is kept and reported, so nothing new is deleted.
set -euo pipefail
remote=${1:-origin}
del=()
while read -r b sha; do
  cur=$(git ls-remote --heads "$remote" "refs/heads/$b" | cut -f1)
  if [ -z "$cur" ]; then echo "already gone  $b"; continue; fi
  if [ "$cur" != "$sha" ]; then echo "MOVED, kept   $b (now $cur, recorded $sha)"; continue; fi
  del+=("$b")
done <<'LIST'
bench/first-batch 3f20912fad4f14f3731afa9229f18dc6045e9a57
build/buildings-02zh 23ce8c54bade9f3382a84d035bbaed835d7dfcc7
build/generator-37.2 25728e420ae5165d62edbc13d4cc535697f37e4b
claude/charming-wozniak-4iqwdk 7cf91231b650f974309aa39736dac2db92849ebf
claude/zen-fermat-pwepak 3570b95737b3622c730b14f7184ceeb3eb81f62f
coord 8aaede867bd8906481eba814ec7288d78fdf530b
design/benchmark-scenarios 133a0673a3551a056b4b70c83737469130ada49a
doc/26-run-comparison 0dd786b7e60d7406bfddd6eabc951dce433a4f2c
doc/27-systems-inventory 4ac7220a2f4978c42c3968de2e77e3d979dc87c3
doc/28-scenario-suite 68f4303ce8adc01b342655cb7b592de2c8a7e861
doc/29-takeover-bench 51e5949cfaf68d58a5b614ac4798c7ed26691dc0
doc/30-world-benchmarks c7cd4523aa46b0116bbddbeb00b7e8de14c24bd8
econ/37.2-thicker-economy 12da73e0734efee7e0a1b734b594d030a4ae49ef
integrate/batch2 09ba13a79139646a226061cabb1aae67b6c6d590
subsistence 09ba13a79139646a226061cabb1aae67b6c6d590
trial/publish-complete a9d5191c5a7455b0cf1f9262848d2182ed8e6648
wp/channel-purposes 7a53ccc3b32a5ae3c376c375e2ffa183b126fbf5
wp/channels-delivery e0829f207a0d9318b4e4aee1ea4c5d61049d66a2
wp/coop-world f3f04123b35550f92a706197321a9b918f49305a
wp/courts-records 2d480fc3e662be2234183285fb0963166241669f
wp/cybertron2 ddd84a42a9bd61e30a3f6d1140547551f4b63ec5
wp/dataset-naming 49a788edfd81739542b724de2643fa525168f7f1
wp/demography 8185fe74f8199974a49f1f23343dcb785c06c0f4
wp/documents 44115206d19acfba1b8b36457824f5a5e900211a
wp/econ-plumbing 0310200c30cb5dfe2829bf0085247c595fd72c45
wp/engine-bugs 3b2ba4f7dae52d96a221ed6fce8acd9bcfb86e63
wp/environment 0d52782b75f785837e53fb25fde1ac2ef9f2c824
wp/established-worlds 68ff97eb7164cdcf5b40596f124d4489014f8f1d
wp/farming 31d1ac0c61567bef40679787ec32fe9e4d1e1bdd
wp/force 03d59a9559376def0c7dfbc23140a06e52214db7
wp/ic-horizon 86712e38cde86046adc6919faa4a3f1db4198372
wp/inst-cross 779ab564f0e510c04cec8a1cbed02c87bbea29c9
wp/inst-metrics 41da74df5712f6eae26f4a473644449da278e8a0
wp/interview 355cd7114bee9bba82d24e3a749e018e899213cf
wp/law-imports 0bb9d3ed38e7ceb78b16c6726e1bb5789ba20b53
wp/laws-loud 7a4d5dcaf9782fb7f23e2286c10c7a4cdd1e3b7e
wp/lawyer-expert 497d610c8af296514137526b06bf967051591cbb
wp/lead 164b27cec8045814c5dd854d5fb9b93b9b9c5ff1
wp/merchant-world 82d5c9fd0a027d0caebc24c70b3eac82ce2b9314
wp/obligations 05aed0a73c76f93bfbad5a5092b8ca89b9fe0810
wp/obligations2 ef48ff92fa07a02a7336d6bfb24f9921d09b3041
wp/old-code-cleanup c2869e8ee141bcc53da6d547f8bfd660469303e1
wp/positions 634db57637e28426057610f0fd062eb4c19f34d6
wp/private-final dfa3d5807277d7a4972687d8d65fa9fd34d8b065
wp/private-world 08725d43113c9b8560ba4883ae9bf260cb63827e
wp/publish-complete 3f2495aaf3ba4c58629fe82ca2743a8d8fbc0873
wp/publish-privacy c522565254bde416f542e73929f2bd44268a03b1
wp/shadowed-effects cb24d6583fc01006ce57aa57b94dd46d5d7869b7
wp/similar-flag 608081943c8cc8bb99e8e81d023a0ebef8f66a43
wp/site-archive dece01d21f588f9f060353261e2fddcf0ff44dcb
wp/site-cybertron1 687ae3cb5715cc182fb9b87c437b371804cd7fbf
wp/site-v2 8e1b37de72919434fe675cd9ab60b3ec1195ccf6
wp/state-world 844540e87d3bdcd8c79026ec600439c900b02f76
wp/takeover-index 07363f3395b0ff6ed710947f61f6861bf143c435
wp/takeover-worlds 7cbf4a6ec1fd580d0616e53bb946ea6dd17aa9bf
wp/usability-fixes a2796cdc5cbe27a72a5b17e2452b8057bdc0ea32
LIST
if [ ${#del[@]} -gt 0 ]; then
  git push "$remote" --delete "${del[@]}"
  echo "deleted ${#del[@]} branches"
fi
git fetch "$remote" --prune
echo "remaining:"; git ls-remote --heads "$remote" | sed 's#.*refs/heads/#  #'

# Cybertron 2 (separate repository): the archive tag this session could not push.
# git clone https://github.com/zachmacsmith/Cybertron2 && cd Cybertron2 && \
#   git tag -a archive/cybertron1-inherited ddd84a42 -m "Last commit carrying the inherited Cybertron 1 package, docs, site and tests" && \
#   git push origin archive/cybertron1-inherited
