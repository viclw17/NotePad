​The primary benefits of precomputed visibiliity volumes is that it will store the visibility of Actors based on their location in the world. This is extremely usefule for mobile platforms which do not support *hardware occlusion queries*, and to *save rendering thread time* in rendering thread bottlenecked scenarios like split screen on consoles.

**Precomputed visibility** decreases rendering thread time in game at the cost of increasing runtime memory and lighting build time.

It saves rendering thread time by reducing the number of primitives that have to be handled by the *dynamic occlusion system (hardware occlusion queries)* and because it works immediately, while the dynamic occlusion system needs time to converge, which often means poor performance coming around a corner or rotating the view quickly.

This technique is only useful for medium sized levels or smaller, as the memory and computation requirements grow with the level size. It is also only useful for games with mostly static environments, restricted player movement and somewhat 2d play areas.

---
