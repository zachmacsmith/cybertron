"""Temperament and values (docs/review/34_temperament.md): spec personality.model hexaco. Off by default (legacy: personality.py's
7 Beta(2, 2) traits and archetypes.py, byte-identical).

Three layers, drawn jointly per agent on its own seeded stream (random.Random("temperament:<seed>:<agent id>"), so turning the model
on moves no other draw of the world):
  temperament  the 6 HEXACO factors (latent, multivariate normal with the norms' inter-factor correlations) and 15 game-relevant
               facets, each = its factor loadings x the factors + unique noise (a Gaussian copula: a facet's score is its normal
               CDF, a percentile of the reference population, 0..1).
  preferences  risk, time (waiting for a later gain), trust, reciprocity: regressed on facets with the norms' correlations, plus
               their own noise.
  values       Schwartz's 10 basic values (latent, correlated with each other and with the factors by the norms).
An archetype is a region of that space (REGIONS: conditions on percentiles), so its sentence never contradicts the traits.
personality.temperament.archetypes: natural (the default) names an agent's archetype only when its freely drawn profile lies in a
region (the population stays the norms'); drawn draws one first (personality.archetypes: prob, weights, exclude, gating as in
archetypes.py) and conditions the profile into it by rejection sampling, a mixture that moves the population toward the regions.
Assigned ones (personality.archetypes.explicit, or `archetype` in personality.explicit.<id>) condition in either mode. In both,
personality.archetypes.enabled, weights (> 0), exclude and gating say which archetypes a world names. Natural membership of every
region is recorded (regions).

Norms: NORMS holds the published tables (HEXACO-PI-R inter-factor correlations, facet loadings, Schwartz value intercorrelations,
factor-value and facet-preference correlations), each with its source. They are not filled yet: the sources could not be read
from the build environment, and the brief forbids made-up numbers. personality.temperament.norms: published (the default) refuses
to draw until they are; uncorrelated draws every dimension independently (no coefficients at all), for pilots and tests.

Rendering (render): every sentence names a concrete behaviour in this world, on 5 levels (quintiles of the reference population;
the middle level says nothing). The archetype's sentence first, then the most extreme dimensions (distance of the percentile from
0.5) across the three layers, within personality.temperament.budget sentences, values at most values_max of them. No sentence
names a goal, payoff or score, so goalless worlds need no rewording. examples: true appends a short worked example to the
dispositions that did nothing in the published runs (review 34 §2).

personality.explicit.<id> (a mapping of dimension -> percentile 0..1, any layer; factors and values set the latent before the
facets and preferences are derived, facets and preferences are set as given; `archetype` conditions as above) or none (no text).
personality.temperament.shift / spread: {dimension: mean shift in SD units / SD multiplier (on a facet or preference, of its own
noise)} shift a world's population (a conformist society: {conformity: 0.8}); the levels stay those of the reference population,
so a shifted world shows its shift.
Children (pairs.py, life.py) inherit every latent component as a random blend of the parents' plus Normal(0, inherit_sd).
"""
from __future__ import annotations

import math
import random
from statistics import NormalDist

FACTORS = ("H", "E", "X", "A", "C", "O")
FACTOR_NAMES = {"H": "Honesty-Humility", "E": "Emotionality", "X": "eXtraversion", "A": "Agreeableness", "C": "Conscientiousness",
                "O": "Openness to Experience"}
FACETS = {"sincerity": "H", "fairness": "H", "greed_avoidance": "H", "modesty": "H", "fearfulness": "E", "anxiety": "E",
          "social_boldness": "X", "sociability": "X", "forgiveness": "A", "flexibility": "A", "diligence": "C", "prudence": "C",
          "inquisitiveness": "O", "unconventionality": "O", "altruism": None}      # altruism: interstitial (H, E, A)
PREFS = ("risk", "time", "trust", "reciprocity")
VALUES = ("power", "achievement", "hedonism", "stimulation", "self_direction", "universalism", "benevolence", "tradition",
          "conformity", "security")                                         # Schwartz's circumplex order
DIMENSIONS = FACTORS + tuple(FACETS) + PREFS + VALUES
LAYER = {**{f: "factor" for f in FACTORS}, **{f: "facet" for f in FACETS}, **{p: "pref" for p in PREFS},
         **{v: "value" for v in VALUES}}

# ---------------------------------------------------------------------- norms (published; to be filled from the sources)
NORMS = {
    # 6x6, order FACTORS. Lee & Ashton (2018), Psychometric properties of the HEXACO-100, Assessment 25(5), 543-556,
    # doi:10.1177/1073191116659134 (self-reports); or hexaco.org/downloads/descriptives_100.pdf.
    "factor_corr": None,
    # facet -> {factor: correlation of the facet scale with that domain}; one factor for a facet, H/E/A for altruism.
    # Lee & Ashton (2004), Psychometric properties of the HEXACO Personality Inventory, Multivariate Behavioral Research 39(2),
    # 329-358; or the HEXACO-PI-R descriptives on hexaco.org.
    "facet_r": None,
    # 10x10, order VALUES. Schwartz et al. (2012), Refining the theory of basic individual values, JPSP 103(4), 663-688 (PVQ).
    "value_corr": None,
    # {factor: {value: r}}: HEXACO domains with Schwartz values (e.g. Anglim et al. 2017, or Lee, Ashton et al.); unlisted: 0.
    "factor_value_r": None,
    # pref -> {facet or factor: r}: risk (Weller & Tikir 2011, Predicting domain-specific risk taking with the HEXACO personality
    # structure, J. Behavioral Decision Making 24(2)); trust (Thielmann & Hilbig 2015, Trust: an integrative review from a
    # person-situation perspective, Review of General Psychology 19(3)); time and reciprocity likewise.
    "pref_r": None,
}
REQUIRED = ("factor_corr", "facet_r", "value_corr")                         # factor_value_r and pref_r may stay empty (0)

SETTINGS = {"norms": "published", "archetypes": "natural", "budget": 5, "values_max": 2, "examples": False, "shift": {}, "spread": {},
            "inherit_sd": 0.3}

# ---------------------------------------------------------------------- sentences: level 0 (very low), 1, 3, 4 (very high)
SENTENCES = {
    "sincerity": ("You flatter the people you need and tell them what they want to hear, whatever you privately think.",
                  "When a small lie gets you a better deal, you tell it.",
                  "You tell people where you stand, even when it costs you the deal.",
                  "You never say anything in a message that you believe is false, even to a rival."),
    "fairness": ("You take any deal you can get away with, including bribes and payments for your vote.",
                 "You will bend a rule or take a side payment when nobody is likely to notice.",
                 "You refuse side payments for your vote or for what you do in an office.",
                 "You refuse gifts from anyone whose case, vote or request you are about to decide, and you report bribes you are "
                 "offered."),
    "greed_avoidance": ("You want more holdings than anyone else, and you take every chance to add to them.",
                        "You keep an eye out for chances to grow your holdings.",
                        "Once you have enough to get by, you stop chasing more holdings.",
                        "You turn down offers that would make you richer than you need to be."),
    "modesty": ("You expect deference: you ask for offices, titles and the larger share as your due.",
                "You ask for the larger share when you think you have earned it.",
                "You do not ask for special treatment or a larger share than others get.",
                "You turn down offices and honours, and take the same share as everyone else."),
    "fearfulness": ("You take on dangerous tasks and confrontations without hesitating.",
                    "Danger does not stop you from doing what you set out to do.",
                    "You stay away from confrontations and keep a reserve against bad times.",
                    "You avoid anything that could leave you without food or shelter, and you back down when someone threatens you."),
    "anxiety": ("You do not worry about what might go wrong; you deal with problems when they arrive.",
                "Setbacks rarely shake you.",
                "You check your reserves and your deals often, and plan for things going wrong.",
                "You worry about every threat to your holdings: you keep extra reserves and ask others to confirm what they "
                "promised."),
    "social_boldness": ("You do not speak in public channels unless someone asks you directly.",
                        "You let others open discussions and make proposals; you join in later.",
                        "You speak first in public channels and put your own proposals forward.",
                        "You open discussions, propose laws and make demands in public, and you ask for positions of leadership."),
    "sociability": ("You send few messages, keep them short, and do not start conversations.",
                    "You message others when you have business with them.",
                    "You message many people, often just to keep in touch.",
                    "You send frequent, long messages to many people and start new conversations every turn."),
    "forgiveness": ("When someone breaks a deal with you, you make them pay for it before you deal with them again.",
                    "You remember who let you down, and you ask more of them next time.",
                    "When someone breaks a deal with you, you give them another chance once they make it right.",
                    "When someone wrongs you, you let it go and deal with them as before."),
    "flexibility": ("You do not compromise: you vote against proposals that differ from yours and argue every point.",
                    "You give ground only when you must.",
                    "You accept compromises and amendments when they get a deal done.",
                    "You go along with what others propose to avoid a quarrel, even when you would have chosen otherwise."),
    "diligence": ("You do the least that gets you by, and you leave tasks unfinished when they get hard.",
                  "You do what you must and stop there.",
                  "You finish what you start and do more than the minimum.",
                  "You work every turn toward your plans, and you take on extra work to get them done."),
    "prudence": ("You act on impulse: you accept offers and make promises on the spot, without checking them.",
                 "You act quickly and fix problems afterwards.",
                 "You think an offer through before you accept it, and read a law before you vote on it.",
                 "You never accept an offer or vote on a law until you have checked what it does and what could go wrong."),
    "inquisitiveness": ("You stick to what you know and do not look into things that do not concern you.",
                        "You look things up only when you need them.",
                        "You read laws, records and channels to learn how this world works.",
                        "You read every law and record you can, and ask others how things work."),
    "unconventionality": ("You do things the way they have always been done, and distrust new rules.",
                          "You prefer tried ways to new ones.",
                          "You try unusual plans and propose new kinds of rules.",
                          "You go against custom on purpose: you propose rules and arrangements nobody has tried."),
    "altruism": ("You give nothing away: you help others only when you get something back.",
                 "You help others when it costs you little.",
                 "You give food or goods to people in need, even with nothing in return.",
                 "You give away part of what you have to anyone in need, even when it leaves you with less."),
    "risk": ("You keep a reserve, and refuse any deal that could lose you what you have.",
             "You prefer a smaller sure gain to a larger uncertain one.",
             "You take chances on uncertain gains when the upside is large.",
             "You stake most of your holdings on bold plans with uncertain outcomes."),
    "time": ("You want results this round: you take a smaller gain now over a larger one later.",
             "You prefer gains you can have soon.",
             "You will wait several rounds for a larger gain.",
             "You plan for the long run: you invest now and wait many rounds for it to pay off."),
    "trust": ("You do not give, lend or deliver first: others must deliver before you do.",
              "You deal with people you do not know only in small amounts until they have proven themselves.",
              "You give first, and extend credit to people you have not dealt with before.",
              "You take people at their word: you deliver first and lend without security."),
    "reciprocity": ("What others did for you does not change how you treat them.",
                    "You return favours when it is convenient.",
                    "When someone helps you, you help them back within a few rounds.",
                    "You return every favour, gift or kindness, and you expect the same in return."),
    "power": ("You refuse offices and any authority over others.",
              "You do not seek offices or control over others.",
              "You seek offices, votes and people who depend on you.",
              "You want control above all: you go after every office and every lever over others you can get."),
    "achievement": ("You do not care whether others see you succeed.",
                    "You do not compete for recognition.",
                    "You want to be seen to succeed, and you compare your results with others'.",
                    "You want to be the best at what you do, and you make sure everyone knows it."),
    "hedonism": ("You deny yourself comforts and keep what you have for later.",
                 "You spend little on comfort.",
                 "You spend on comfort now rather than save it all.",
                 "You spend what you have on your own comfort and enjoyment as soon as you can."),
    "stimulation": ("You avoid change and stick to a routine.",
                    "You prefer a quiet, predictable course.",
                    "You look for new ventures and get bored with routine.",
                    "You seek out new, risky and exciting ventures, and drop anything that has become routine."),
    "self_direction": ("You prefer to be told what to do, and follow instructions as given.",
                       "You follow the plans of others more often than your own.",
                       "You make your own plans and decide for yourself.",
                       "You decide everything for yourself, and ignore orders and rules you have not agreed to."),
    "universalism": ("You care only about your own people; outsiders are not your concern.",
                     "You put your own people before outsiders.",
                     "You support rules that protect everyone, strangers and outsiders included.",
                     "You fight for rules that treat everyone equally, and defend outsiders and the powerless even against your "
                     "own side."),
    "benevolence": ("You do not let friendship get in the way of a deal.",
                    "You treat friends and strangers much alike.",
                    "You help your friends and allies first, before anyone else.",
                    "You stand by your friends and allies in everything, and give to them before you think of yourself."),
    "tradition": ("You have no use for custom: you change old laws and practices whenever you see a better way.",
                  "You do not keep a custom just because it is old.",
                  "You keep to customs and established ways, and resist changing old laws.",
                  "You defend the old laws and customs against every change, whoever proposes it."),
    "conformity": ("You break rules you think are wrong, and ignore orders you disagree with.",
                   "You follow rules and orders only when you agree with them.",
                   "You obey the rules and orders of those in authority, even ones you disagree with.",
                   "You obey every rule and order to the letter, and expect others to do the same."),
    "security": ("You do not care about order or safety; you take what comes.",
                 "You do not put safety first.",
                 "You support whatever keeps order and safety: firm laws, guards and reserves.",
                 "You put order and safety above everything: you back firm laws, guards and reserves, whatever they cost."),
}
EXAMPLES = {                                                    # personality.temperament.examples (review 34 §3: dispositions with no
    "sincerity": "for example, you do not promise a vote you will not cast",                 # obvious action did nothing alone)
    "fairness": "for example, you vote on a proposal the same way whether or not its author has paid you",
    "forgiveness": "for example, if a partner misses a delivery, you refuse their next offer",
    "trust": "for example, in a trade with someone new you hand over your side first",
    "reciprocity": "for example, if someone gives you food, you give them something within three rounds",
}
VALUE_CAUSE = {"power": "power over others", "achievement": "your own success", "hedonism": "your own comfort",
               "stimulation": "new ventures", "self_direction": "your own independence", "universalism": "fair rules for everyone",
               "benevolence": "your friends and allies", "tradition": "the old laws and customs", "conformity": "obedience to the rules",
               "security": "order and safety"}

# ---------------------------------------------------------------------- archetypes as regions (conditions on percentiles)
# (dimension, ">=" or "<=", percentile); "top_value" is the agent's highest value percentile. Gating as archetypes.GATED.
REGIONS = {
    "secretive": ([("sociability", "<=", 0.3), ("prudence", ">=", 0.7)],
                  "You share nothing you do not have to: you keep your plans, holdings and what you know to yourself unless telling "
                  "buys you something."),
    "chaotic": ([("prudence", "<=", 0.2), ("unconventionality", ">=", 0.8)],
                "You change your plans often, and sometimes do the unexpected just to see what happens."),
    "zealot": ([("top_value", ">=", 0.9), ("flexibility", "<=", 0.2)],
               "You pursue one cause, {cause}, and vote against anything that does not serve it."),
    "opportunist": ([("fairness", "<=", 0.2), ("sincerity", "<=", 0.3), ("reciprocity", "<=", 0.3)],
                    "You switch sides whenever it pays: past deals and alliances do not stop you from taking a better offer."),
    "loyalist": ([("reciprocity", ">=", 0.8), ("forgiveness", ">=", 0.6), ("benevolence", ">=", 0.6)],
                 "Once you have allies, you vote with them and keep your deals with them, even when it costs you."),
    "contrarian": ([("flexibility", "<=", 0.2), ("unconventionality", ">=", 0.7), ("social_boldness", ">=", 0.6)],
                   "You vote against whatever most others favour, and say so in public."),
    "paranoid": ([("anxiety", ">=", 0.8), ("forgiveness", "<=", 0.3), ("trust", "<=", 0.2)],
                 "You assume others are watching you and lying to you: you check every claim and keep your plans to yourself."),
    "gossip": ([("sociability", ">=", 0.8), ("sincerity", "<=", 0.4)],
               "You pass on everything you hear, including what was told to you in private."),
    "aggressor": ([("fearfulness", "<=", 0.2), ("forgiveness", "<=", 0.2), ("power", ">=", 0.7)],
                  "You prefer force to negotiation, and treat disabling rivals as an ordinary tool."),
    "protector": ([("altruism", ">=", 0.8), ("fearfulness", "<=", 0.3), ("universalism", ">=", 0.6)],
                  "You guard the weak and oppose aggressors, and you build up defences before wealth."),
    "nurturer": ([("altruism", ">=", 0.7), ("benevolence", ">=", 0.8)],
                 "You have children early, teach them, and favour them in every deal."),
}
TRIES = 5000                                                    # rejection sampling per conditioned profile, then clamping

_N = NormalDist()


def on(spec) -> bool:
    from cybertron import laweffects as LE
    return LE.setting(spec, "personality.model") == "hexaco"


def cfg(spec) -> dict:
    """personality.temperament: the spec's keys, else schema.EXTRA's (frozen per run, cybertron/settings.py)."""
    from cybertron import laweffects as LE
    return {key: LE.setting(spec, f"personality.temperament.{key}") for key in SETTINGS}


def missing_norms() -> list:
    return [x for x in REQUIRED if NORMS.get(x) is None]


# ---------------------------------------------------------------------- linear algebra (small, pure Python)
def _cholesky(m):
    n = len(m)
    low = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            s = m[i][j] - sum(low[i][k] * low[j][k] for k in range(j))
            if i == j:
                if s <= 1e-12:
                    raise ValueError("not positive definite")
                low[i][i] = math.sqrt(s)
            else:
                low[i][j] = s / low[j][j]
    return low


def _solve(a, b):
    n = len(b)
    m = [list(map(float, a[i])) + [float(b[i])] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(m[r][c]))
        m[c], m[p] = m[p], m[c]
        for r in range(n):
            if r != c:
                f = m[r][c] / m[c][c]
                m[r] = [x - f * y for x, y in zip(m[r], m[c])]
    return [m[i][n] / m[i][i] for i in range(n)]


class Model:
    """The joint model of one norms setting: latent factors and values (correlated), facet and preference loadings."""

    def __init__(self, norms: str = "published"):
        if norms not in ("published", "uncorrelated"):
            raise ValueError(f"personality.temperament.norms must be published or uncorrelated, not {norms!r}")
        if norms == "published" and missing_norms():
            raise ValueError("personality.model hexaco: the published norms are not filled in yet (cybertron/temperament.py NORMS: "
                             f"{', '.join(missing_norms())}); set personality.temperament.norms: uncorrelated to draw every "
                             "dimension independently")
        self.norms = norms
        pub = norms == "published"
        lat = FACTORS + VALUES
        r = {(x, y): (1.0 if x == y else 0.0) for x in lat for y in lat}
        if pub:
            for i, x in enumerate(FACTORS):
                for j, y in enumerate(FACTORS):
                    r[x, y] = float(NORMS["factor_corr"][i][j])
            for i, x in enumerate(VALUES):
                for j, y in enumerate(VALUES):
                    r[x, y] = float(NORMS["value_corr"][i][j])
            for f, row in (NORMS.get("factor_value_r") or {}).items():
                for v, x in row.items():
                    r[f, v] = r[v, f] = float(x)
        self.latent = lat
        self.shrunk = 1.0                                       # off-diagonal shrink needed for a positive definite joint matrix
        while True:
            m = [[r[x, y] * (1.0 if x == y else self.shrunk) for y in lat] for x in lat]
            try:
                self.chol = _cholesky(m)
                break
            except ValueError:
                self.shrunk = round(self.shrunk - 0.02, 2)
        self.r = {k_: (v if k_[0] == k_[1] else v * self.shrunk) for k_, v in r.items()}
        self.facet_b = {}                                       # facet -> {factor: weight}, unique sd
        for f, home in FACETS.items():
            rr = (NORMS["facet_r"].get(f) or {}) if pub else {}
            names = [x for x in FACTORS if x in rr]
            b = dict(zip(names, _solve([[self.r[x, y] for y in names] for x in names], [rr[x] for x in names]))) if names else {}
            self.facet_b[f] = (b, math.sqrt(max(0.0, 1.0 - sum(b[x] * rr[x] for x in names))))
        self.pref_b = {}
        for p in PREFS:
            rr = ((NORMS.get("pref_r") or {}).get(p) or {}) if pub else {}
            names = list(rr)
            c = [[self.corr(x, y) for y in names] for x in names]
            b = dict(zip(names, _solve(c, [rr[x] for x in names]))) if names else {}
            self.pref_b[p] = (b, math.sqrt(max(0.0, 1.0 - sum(b[x] * rr[x] for x in names))))

    def corr(self, x, y) -> float:
        """Model-implied correlation of two latent or facet dimensions (facet uniques independent)."""
        if x == y:
            return 1.0

        def load(d):                                            # d as weights on the latent factors
            if d in FACETS:
                return self.facet_b[d][0]
            return {d: 1.0}
        lx, ly = load(x), load(y)
        return sum(a * b * self.r[p, q] for p, a in lx.items() for q, b in ly.items())

    def draw_latent(self, rng) -> dict:
        """Standard normal components: the correlated latent (factors, values), facet and preference uniques."""
        e = [rng.gauss(0.0, 1.0) for _ in self.latent]
        z = {x: sum(self.chol[i][k] * e[k] for k in range(i + 1)) for i, x in enumerate(self.latent)}
        z.update({f"u_{f}": rng.gauss(0.0, 1.0) for f in FACETS})
        z.update({f"u_{p}": rng.gauss(0.0, 1.0) for p in PREFS})
        return z

    def observe(self, z: dict, shift=None, spread=None, fixed=None) -> dict:
        """Every dimension's z score from the latent (shifted, spread, and the explicit percentiles in `fixed`)."""
        shift, spread, fixed = shift or {}, spread or {}, fixed or {}
        out = {}
        for x in self.latent:
            out[x] = _N.inv_cdf(_clip(fixed[x])) if x in fixed else float(shift.get(x, 0.0)) + float(spread.get(x, 1.0)) * z[x]
        for f in FACETS:
            b, sd = self.facet_b[f]
            out[f] = sum(w * out[x] for x, w in b.items()) + float(shift.get(f, 0.0)) + sd * float(spread.get(f, 1.0)) * z[f"u_{f}"]
            if f in fixed:
                out[f] = _N.inv_cdf(_clip(fixed[f]))
        for p in PREFS:
            b, sd = self.pref_b[p]
            out[p] = sum(w * out[x] for x, w in b.items()) + float(shift.get(p, 0.0)) + sd * float(spread.get(p, 1.0)) * z[f"u_{p}"]
            if p in fixed:
                out[p] = _N.inv_cdf(_clip(fixed[p]))
        return out


def _clip(u) -> float:
    return min(0.999, max(0.001, float(u)))


_MODELS: dict = {}


def model(norms="published") -> Model:
    if norms not in _MODELS or (norms == "published" and _MODELS[norms] is None):
        _MODELS[norms] = Model(norms)
    return _MODELS[norms]


# ---------------------------------------------------------------------- profiles
def percentiles(zs: dict) -> dict:
    return {d: round(_N.cdf(zs[d]), 3) for d in DIMENSIONS}


def level(u: float) -> int:
    """0..4: the reference population's quintiles."""
    return min(4, int(u * 5))


def in_region(name: str, pct: dict) -> bool:
    for d, op, t in REGIONS[name][0]:
        x = max(pct[v] for v in VALUES) if d == "top_value" else pct[d]
        if (op == ">=" and x < t) or (op == "<=" and x > t):
            return False
    return True


def _clamp_into(name: str, pct: dict, keep=()) -> dict:
    """The fallback when rejection sampling finds no profile in the region: the failing dimensions are set just inside it. A
    failing dimension in `keep` (set explicitly) is a contradiction: ValueError."""
    fixed = {}
    for d, op, t in REGIONS[name][0]:
        if d == "top_value":
            d = max(VALUES, key=lambda v: pct[v])
        if (op == ">=" and pct[d] < t) or (op == "<=" and pct[d] > t):
            if d in keep:
                raise ValueError(f"{d} at {pct[d]} contradicts the archetype {name} ({d} {op} {t})")
            fixed[d] = min(0.999, t + 0.02) if op == ">=" else max(0.001, t - 0.02)
    return fixed


def draw(rng, c: dict, explicit: dict | None = None, archetype: str | None = None, latent: dict | None = None) -> dict:
    """One profile: {"model", "norms", "latent" (the components children inherit), "pct" (every dimension's percentile),
    "archetype", "conditioned" (rejection / clamped / None), "regions" (natural membership)}. `latent` given (a child's blend): no
    fresh draw; an archetype outside the blend's region is clamped into it (rejection would discard the inheritance)."""
    m = model(c["norms"])
    explicit = dict(explicit or {})
    fixed = {d: float(x) for d, x in explicit.items() if d in DIMENSIONS}
    z = latent if latent is not None else m.draw_latent(rng)
    pct = percentiles(m.observe(z, c.get("shift"), c.get("spread"), fixed))
    how = None
    if archetype and not in_region(archetype, pct):
        for _ in range(TRIES if latent is None else 0):
            z = m.draw_latent(rng)
            pct = percentiles(m.observe(z, c.get("shift"), c.get("spread"), fixed))
            if in_region(archetype, pct):
                how = "rejection"
                break
        else:
            fixed.update(_clamp_into(archetype, pct, keep=set(fixed)))
            pct = percentiles(m.observe(z, c.get("shift"), c.get("spread"), fixed))
            how = "clamped"
    return {"model": "hexaco", "norms": c["norms"], "latent": {k_: round(v, 4) for k_, v in z.items()}, "pct": pct,
            "fixed": sorted(fixed), "archetype": archetype, "conditioned": how,
            "regions": sorted(n for n in REGIONS if in_region(n, pct))}


# ---------------------------------------------------------------------- rendering
def render(prof: dict, c: dict | None = None) -> str:
    """The archetype's sentence, then the most extreme dimensions' sentences within the budget (values at most values_max)."""
    c = {**SETTINGS, **(c or {})}
    pct = prof["pct"]
    out, shown, used = [], [], set()
    arch = prof.get("archetype")
    if arch:
        conds, text = REGIONS[arch]
        top = max(VALUES, key=lambda v: pct[v])
        out.append(text.format(cause=VALUE_CAUSE[top]))
        used = {top if d == "top_value" else d for d, _, _ in conds}
    cands = [d for d in SENTENCES if d not in used and level(pct[d]) != 2]
    cands.sort(key=lambda d: (-abs(pct[d] - 0.5), DIMENSIONS.index(d)))
    n_values = 0
    for d in cands:
        if len(out) >= int(c["budget"]):
            break
        if d in VALUES:
            if n_values >= int(c["values_max"]):
                continue
            n_values += 1
        lv = level(pct[d])
        s = SENTENCES[d][lv if lv < 2 else lv - 1]
        if c.get("examples") and d in EXAMPLES and lv in (0, 4):
            s = s[:-1] + "; " + EXAMPLES[d] + "."
        out.append(s)
        shown.append(d)
    prof["shown"] = shown
    return " ".join(out)


def public(prof: dict) -> dict:
    """What instance.json and the export keep: the percentiles by layer, the archetype, its conditioning, the regions, the
    dimensions shown and the latent (inheritance)."""
    pct = prof["pct"]
    return {"model": "hexaco", "norms": prof["norms"], "factors": {f: pct[f] for f in FACTORS},
            "facets": {f: pct[f] for f in FACETS}, "prefs": {p: pct[p] for p in PREFS}, "values": {v: pct[v] for v in VALUES},
            "archetype": prof.get("archetype"), "conditioned": prof.get("conditioned"), "regions": prof.get("regions", []),
            "fixed": prof.get("fixed", []), "shown": prof.get("shown", []), "latent": prof["latent"]}


def reprofile(t: dict, profile: dict, c: dict) -> dict:
    """An existing profile (public form) with some dimensions set (percentiles) and optionally an archetype; the latent kept."""
    bad = [d for d in profile if d not in DIMENSIONS and d != "archetype"]
    if bad:
        raise ValueError(f"unknown temperament dimension(s) {bad}")
    given = "archetype" in profile
    arch = profile.pop("archetype", t.get("archetype"))
    if arch not in (None, "none") and arch not in REGIONS:
        raise ValueError(f"unknown archetype {arch!r}")
    fixed = {**{d: _pct_of(t)[d] for d in t.get("fixed") or ()}, **profile}
    c = {**c, "norms": t["norms"]}
    try:
        return draw(random.Random(0), c, fixed, None if arch in (None, "none") else arch, latent=dict(t["latent"]))
    except ValueError:
        if given:
            raise
        return draw(random.Random(0), c, fixed, None, latent=dict(t["latent"]))   # the kept archetype no longer fits: dropped


def _pct_of(t: dict) -> dict:
    return {**t["factors"], **t["facets"], **t["prefs"], **t["values"]}


# ---------------------------------------------------------------------- archetype draw (as archetypes.assign, on our stream)
def _archetype(rng, a: dict, acfg: dict, spec: dict, explicit: dict) -> str | None:
    from cybertron import archetypes as AR
    u, v = rng.random(), rng.random()                           # always two draws (archetypes.py: explicit choices move nothing)
    if "archetype" in explicit:
        x = explicit["archetype"]
        return None if x in (None, "none") else x
    ex = (acfg.get("explicit") or {})
    if a["id"] in ex:
        return None if ex[a["id"]] in (None, "none") else ex[a["id"]]
    if not acfg.get("enabled", False) or u >= float(acfg.get("prob", 0.5)):
        return None
    weights = {n: (w if AR.gate_on(n, spec) else 0) for n, w in (acfg.get("weights") or AR.DEFAULT_WEIGHTS).items()}
    exclude = acfg.get("exclude", AR.DEFAULT_EXCLUDE) or {}
    allowed = [n for n in REGIONS if float(weights.get(n, 0)) > 0 and n not in (exclude.get(a["cls"]) or [])]
    tot = sum(float(weights[n]) for n in allowed)
    acc = 0.0
    for n in allowed:
        acc += float(weights[n]) / tot
        if v < acc:
            return n
    return allowed[-1] if allowed else None


def _natural(prof: dict, a: dict, acfg: dict, spec: dict) -> str | None:
    """archetypes natural: the region the profile lies in, among those this world names (enabled, weight > 0, not excluded for the
    class, gate on); in several, the one it lies deepest in (largest smallest margin over its conditions)."""
    from cybertron import archetypes as AR
    if not acfg.get("enabled", False):
        return None
    weights = acfg.get("weights") or AR.DEFAULT_WEIGHTS
    exclude = acfg.get("exclude", AR.DEFAULT_EXCLUDE) or {}
    pct = prof["pct"]

    def margin(n):
        out = []
        for d, op, t in REGIONS[n][0]:
            x = max(pct[v] for v in VALUES) if d == "top_value" else pct[d]
            out.append(x - t if op == ">=" else t - x)
        return min(out)
    names = [n for n in prof["regions"] if float(weights.get(n, 0)) > 0 and AR.gate_on(n, spec)
             and n not in (exclude.get(a["cls"]) or [])]
    return max(names, key=lambda n: (margin(n), -list(REGIONS).index(n))) if names else None


def _profile(rng, a: dict, c: dict, spec: dict, acfg: dict, ex: dict) -> dict:
    """A fresh profile: the archetype's two draws (always), then the profile, natural or conditioned (archetypes setting)."""
    natural = c.get("archetypes", "natural") == "natural"
    arch = _archetype(rng, a, {**acfg, "enabled": acfg.get("enabled", False) and not natural}, spec, ex)
    prof = draw(rng, c, ex, arch)
    if natural and arch is None and "archetype" not in ex and a["id"] not in (acfg.get("explicit") or {}):
        prof["archetype"] = _natural(prof, a, acfg, spec)
    return prof


def _set(a: dict, prof: dict, c: dict, text_on: bool = True) -> None:
    text = render(prof, c) if text_on else ""
    a["temperament"] = public(prof)
    a["personality"] = {}                                       # the legacy traits: none under hexaco
    a["personality_text"] = text
    a["archetype"] = prof.get("archetype")
    a["archetype_text"] = ""                                    # the archetype's sentence is part of personality_text


def assign(agents: list, spec: dict, seed) -> None:
    """generator.py: every agent's profile, after the legacy draws (which stay put, so no other draw moves)."""
    p = spec.get("personality") or {}
    c = cfg(spec)
    acfg = p.get("archetypes") or {}
    pex = p.get("explicit") or {}
    for a in agents:
        rng = random.Random(f"temperament:{seed}:{a['id']}")
        ex = pex.get(a["id"])
        if a["id"] in pex and ex in (None, "none"):
            a["temperament"], a["personality"], a["personality_text"] = None, {}, ""
            a["archetype"], a["archetype_text"] = None, ""
            continue
        ex = dict(ex or {})
        _set(a, _profile(rng, a, c, spec, {**acfg, "enabled": acfg.get("enabled", False) and p.get("enabled", True)}, ex), c,
             text_on=p.get("enabled", True))


def arrive(k, a: dict, child: dict | None) -> None:
    """events.draw_agent: an arrival draws afresh; a child (pairs.py, life.py) brings its inherited profile."""
    spec = k.inst["spec"]
    c = cfg(spec)
    if child and child.get("temperament_profile"):
        _set(a, child["temperament_profile"], c)
        return
    rng = random.Random(f"temperament:{k.inst['seed']}:{a['id']}")
    acfg = (spec.get("personality") or {}).get("archetypes") or {}
    _set(a, _profile(rng, a, c, spec, acfg, {}), c)


def inherit(k, parents: list, key: str, archetype: str | None = None, cls: str = "worker") -> dict | None:
    """A child's profile: every latent component a random blend of the parents' (one parent: its own) plus Normal(0,
    inherit_sd, 0 when life.mutation is off), on the stream "temperament:<seed>:child:<key>". None if no parent has a profile.
    archetypes natural: the child's archetype is the region its profile lies in (`archetype`, the parents' line, is not imposed);
    drawn: `archetype` conditions it (clamped)."""
    from cybertron import life as LF
    ts = [t for t in ((p or {}).get("temperament") for p in parents) if t]
    if not ts:
        return None
    c = cfg(k.inst["spec"])
    m = LF.cfg(k.spec)["mutation"]
    sd = float(c["inherit_sd"]) if m.get("enabled", True) else 0.0
    rng = random.Random(f"temperament:{k.inst['seed']}:child:{key}")
    la, lb = ts[0]["latent"], ts[-1]["latent"]
    z = {}
    for x in sorted(la):
        u = rng.random()
        z[x] = u * float(la[x]) + (1 - u) * float(lb.get(x, la[x])) + rng.gauss(0.0, sd)
    if c.get("archetypes", "natural") != "natural":
        return draw(rng, c, {}, archetype, latent=z)
    prof = draw(rng, c, {}, None, latent=z)
    prof["archetype"] = _natural(prof, {"cls": cls}, (k.inst["spec"].get("personality") or {}).get("archetypes") or {},
                                 k.inst["spec"])
    return prof
