Hi Guys, Speaking just to the graphics performance here are my observations, from the Razor GPU capture Jake shared 2018-04-20 14:31:

-The depth passes have a lot of *VGPRs* being initialized by the SPI (14/16) which is killing wave front launch rate, I recommend simplifying/reducing the vgprs set up in your depth only passes, ideally just UV coordinates if alpha testing. This will speed up batches 1-405

-Depth Target 0 is decompressed in place in batch 406, then used as a texture (and a depth at the same time?!) in batch 605, I strongly recommend you decompress your depth targets to a copy, there is a Gnmx helper function to accomplish this. That way, subsequent color passes using Depth target 0 can use it in it's compressed form and speed up rendering/reduce bandwidth. This should pretty much speed up all color batches using depth there on. A way to ensure this is done correctly is to view the depth target's "HTile Planes" in Razor during the color passes, and ensure they are not all white (expanded).

Another note about using a depth prep-ass, you can set the depth comparison to 'depth equal' when rendering everything in the color passes which is not blending transparencies, but this should definitely be used for any alpha tested draws. This goes into more detail than is needed, this game is just single fragment depth, but I recommend going through these notes if you want an in depth explanation:

https://ps4.siedev.net/forums/thread/211278/

# I also think you guys could benefit from more a aggressive LOD system, I'm seeing very high vertex density of objects far off on the horizon.

If you guys can make some of these changes and post another Razor GPU capture before next week so we can further optimize from that, that would be awesome, but if not I understand.

All the best,

-Ryan

*minimal lod unreal variable*

effect 2
post 2
blomm 4

HELP for 'r.BloomQuality':
0: off, no performance impact.
1: average quality, least performance impact.
2: average quality, least performance impact.
3: good quality.
4: good quality.
5: Best quality, most significant performance impact. (default)
5: force experimental higher quality on mobile (can be quite slow on some hardware)
r.BloomQuality = "5"      LastSetBy: DeviceProfile

shadowquality 1ms
decal 1ms
msaa 4ms
0: MSAA disabled (Temporal AA enabled)
1: MSAA disabled
2: Use 2x MSAA
4: Use 4x MSAA8: Use 8x MSAA
