# Lumen Grid: panning pixel dioramas on a 64×64 LED matrix

Small living dioramas for the Divoom Pixoo 64. The camera tracks slowly across a scene built in parallax
layers while small details move: candles flicker, smoke rises, a servo-skull bobs past. Every pixel is
placed in code as a hand-drawn pixel map. The repo has no imported bitmaps. Each GIF loops with no seam.

| Cathedral-ship nave |
|:-:|
| ![nave](out/nave_512.gif) |

## The scenes

**Cathedral-ship nave**: an endless nave aboard an Imperial starship in the Warhammer 40,000 universe.
- Each bay has a tall stained-glass lancet showing a saint with a gold halo, a red robe and a gold sword.
  A band of light sweeps across the panes (colour cycling).
- Below each lancet is a riveted bronze void-port onto space. Through the ports you see stars, a faint
  nebula and an escort ship. Once per loop the ship fires a lance strike.
- Ribbed vaulting meets in gilt bosses overhead. A skull rests in a niche on each pier.
- On the floor a hooded pilgrim kneels beside a candle stand whose three flames flicker out of step.
- In the foreground a dark fluted pillar slides past at twice the speed of the wall, which gives the
  depth. A red banner ripples, a censer swings on its chain and trails incense, and a servo-skull bobs
  by with a blinking red lens.

## Run

```bash
pip install -r requirements.txt
python render.py                 # out/<scene>_64.gif (native, 1 pixel = 1 LED) + out/<scene>_512.gif
python render.py --only nave     # one scene
python -m pytest -q              # Pixoo limits, ≤ 5 MB, square, seamless loop
```

| File | Use |
|---|---|
| `out/*_64.gif` | Native panel resolution. Send this to the Pixoo. |
| `out/*_512.gif` | Nearest-neighbour 8× upscale: crisp pixels, square, under 5 MB. |

## How it's built

- **Pixel maps, not geometry.** Each layer is a grid of characters, one per palette colour, drawn like a
  sprite in a pixel editor. The code only scrolls the layers, cycles the light colours and places the
  moving props.
- **Parallax that loops exactly.** The void behind the ports stays fixed on screen: stars at infinity
  don't move when the camera moves. The wall moves 1 px per frame and repeats every 30 px. The
  foreground moves 2 px per frame and repeats every 60 px. In 30 frames each layer shifts exactly one
  tile, and every other motion (flicker, smoke, sway, bob, blink) has a period that divides 30. A test
  checks that frame 30 is identical to frame 0. The test was mutation-proven: a pan that stops one pixel
  short makes it fail.
- **Built for the Pixoo.** The device replays only the first 30–32 frames of a GIF, so each scene is
  30 frames at 10 fps. Movement is in whole-pixel steps, because fractional steps shimmer on LEDs. The
  palette stays under 64 colours, there is no dithering, and the scene is mostly black, because black
  means the LED is off. Light comes from small saturated sources.

```
ledviz/core.py          grid size, GIF export
ledviz/scenes/nave.py   cathedral-ship nave
ledviz/effects.py       scene registry (frames, fps)
render.py               CLI renderer
tests/                  Pixoo limits + seamless-loop check
```

## Credits

- Unofficial fan art inspired by the Warhammer 40,000 universe. It is not affiliated with or endorsed by
  Games Workshop. Everything is drawn from scratch; no official artwork, logos or assets are used.
- Target hardware: [Divoom Pixoo 64](https://divoom.com/products/pixoo-64).
- [Pillow](https://python-pillow.org/) and [NumPy](https://numpy.org/).
