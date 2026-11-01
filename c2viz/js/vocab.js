// c2viz/js/vocab.js: every word of the engine the renderer knows, in one place: which tool a technique is worked with, which fittings show a fire, what water names a river, which covers stop a river, crop and stage colours by the engine's crop families and stages, what height each road terrain stands at, which events are not marked. When the engine adds or renames one of these, this is the file to change.
(function (X) {
  "use strict";
  const TECH_TOOL = { fell: "fell", reap: "reap", forage: "forage", hay: "reap", hunt: "hunt", mine: "mine", quarry: "mine", milk: "milk",
    ditch: "dig", bury: "dig", fence: "make", wall: "make", herd: "herd", sow: "sow", dibble: "sow", plough: "dig", hoe: "dig", weed: "dig",
    dung: "carry", smelt: "make", charcoal: "make", coin: "make" };
  const toolFor = (a) => !a ? null : TECH_TOOL[a.tech] || (a.verb === "make" || a.verb === "build" ? "make" : a.verb === "gather" ? "forage" : a.verb === "work" ? "dig" : a.verb === "give" || a.verb === "take" ? "carry" : null);
  const RIVER = /river|brook|stream|leat|beck|burn|creek|race/i;
  const LOTS = { built: 6 }, STOPS = new Set(["built", "field", "rock"]);
  const FIRES = ["hearth", "oven", "anvil", "fire ring"];
  const CROP_PAL = {
    grain: { new: ["#9a7a50", "#86b44a"], green: ["#a8d050", "#8cb83e"], high: ["#c0d050", "#a8b838"], ripe: ["#e8c840", "#d4ac30"] },
    "winter grain": { new: ["#9a7a50", "#7aa848"], green: ["#98c858", "#80b048"], high: ["#b8c460", "#a0ac48"], ripe: ["#d8b850", "#c4a03c"] },
    legumes: { new: ["#9a7a50", "#6aa040"], green: ["#5f9a3a", "#4e8a30"], high: ["#5f9a3a", "#4e8a30"], ripe: ["#8a8a3a", "#7a6e30"] },
  };
  const STAGE_PAL = { rotting: ["#a88a30", "#8a7028"], blighted: ["#a89c84", "#8f846e"], killed: ["#9aa0a0", "#868c8c"] };
  const TERRAIN_LAND = { plain: [0.3, 0, 0.1], farmland: [0.3, 0.1, 0.1], woodland: [0.38, 1, 0.2], marsh: [0.1, 0.25, 1], "river valley": [0.15, 0.2, 0.5],
    hills: [0.62, 0.2, 0.1], mountain: [0.88, 0.05, 0] };
  const QUIET_EVENTS = ["speech", "work", "store", "make", "build", "give", "take", "trade"];   // events not marked on the map
  Object.assign(X, { TECH_TOOL, toolFor, RIVER, LOTS, STOPS, FIRES, CROP_PAL, STAGE_PAL, TERRAIN_LAND, QUIET_EVENTS });
})(C2X);
