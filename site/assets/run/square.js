// The square: the whole society at one moment, played event by event (the old run page's square, on the shared clock, with
// the villagers as its people). Its sprites come from one hidden sheet of <symbol>s, one per villager and mood.
import { mountSquare } from "../core/square.js";
import { villagerSymbol, MOODS } from "../core/villagers.js";

export function squareView(ctx, el) {
  const { S, F, st } = ctx;
  el.className = "wrap v-square";
  let sheet = null, sq = null;
  function ensureSheet() {
    if (sheet) return;
    sheet = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    sheet.setAttribute("width", "0"); sheet.setAttribute("height", "0"); sheet.style.position = "absolute";
    sheet.innerHTML = "<defs>" + S.agents.map((a) => MOODS.map((m) => villagerSymbol(F.sprite(a.id), m, `m${a.n}-${m}`)).join("")).join("")
      + villagerSymbol({ id: "anon", cls: "observer" }, "ok", "m-anon") + "</defs>";
    document.body.prepend(sheet);
  }
  return {
    el,
    render() {
      ensureSheet();
      if (!sq) {
        el.innerHTML = `<p class="sq-intro">Everyone in the village at once. Villagers grow with their wealth and smile or sweat as it moves; lines are
          the day's private letters (dashed: forged), bubbles its public posts. Press play to watch the run event by event; click a villager to open their page.</p><div class="sq-host"></div>`;
        sq = mountSquare(el.querySelector(".sq-host"), { S, round: st.round }, (r) => { st.round = r; ctx.go({ round: r }); });
      } else sq.setRound(st.round);
    },
    togglePlay() { if (sq) sq.togglePlay(); },
    leave() { if (sq) { sq.stop(); sq = null; el.innerHTML = ""; } },
  };
}
