"""A fire under no roof in the night's weather (D4-83): more fuel in rain and snow, a chance it goes out in a downpour or a gale
(less with a fire ring), and a sound house's hearth untouched."""
from cybertron2.engine import night as N
from cybertron2.engine.world import World, load_spec


def _w(weather):
    s = load_spec("cybertron2/specs/wild_bands.yaml")
    s["weather"] = {1: weather}
    return World(s)


def test_fuel_by_the_nights_weather():
    assert N.weather_fuel(_w("clear")) == 1.0
    assert N.weather_fuel(_w("rain")) == 1.5
    assert N.weather_fuel(_w("snow")) >= 1.25


def test_a_downpour_or_a_gale_may_put_a_fire_out_and_a_ring_keeps_it_better():
    for kind, lo, hi in (("clear", 0.0, 0.0), ("rain", 0.0, 0.0), ("heavy rain", 0.4, 0.6), ("gale", 0.4, 0.6)):
        w = _w(kind)
        share = sum(N.fire_goes_out(w, ("camp", f"c{i}"), False) for i in range(400)) / 400
        assert lo <= share <= hi, (kind, share)
    w = _w("heavy rain")
    ring = sum(N.fire_goes_out(w, ("camp", f"c{i}"), True) for i in range(400)) / 400
    bare = sum(N.fire_goes_out(w, ("camp", f"c{i}"), False) for i in range(400)) / 400
    assert ring < bare
