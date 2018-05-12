# GCN
Graphics Core Next (GCN) is the codename for both a series of microarchitectures as well as for an instruction set.

https://gpuopen.com/optimizing-gpu-occupancy-resource-usage-large-thread-groups/

VGPRs (Vector General-Purpose Registers)

# HOW UNREAL RENDERS A FRAME
## Particle Simulation
The frame begins with ParticleSimulation pass. It calculates particle motion and other properties for of each particle emitter we have in the scene on the GPU writing to two **render targets**,

* RGBA32_Float for positions and  
* RGBA16_Float for velocities (and a couple of time/life related data).

This, for example is the output for the RGBA32_Float rendertarget, each pixel corresponding to the world position of a sprite:

![](https://interplayoflight.files.wordpress.com/2017/10/image3.png)

## Z-Prepass
Next up is the PrePass render pass, which is essentially a z-prepass. This **renders all the opaque meshes** to an R24G8 depth buffer:

![](https://interplayoflight.files.wordpress.com/2017/10/image4.png)

It is worth noting the Unreal uses **reverse-Z** when rendering to the depth buffer, meaning that the near plane is mapped to 1 and the far plane to 0. This allows for better precision along the depth range and reduces z-fighting on distant meshes.
```
PrePass DDM_AllOpaque(Forced by DBuffer)
```
The name of the rendering pass suggests that the pass was triggered by a “**DBuffer**”. This refers to the **decal buffer** Unreal Engine uses to render deferred decals.

This requires the scene depth so it activates the **Z-prepass**. The z-buffer is used in other contexts though, such as for
* occlusion calculations  
* screen space reflections

```
PrePass DDM_AllOpaque(Forced by ForwardShading)
  View0
    BeginRenderingPrePass
  View1
ResolveSceneDepth
```
## Testing for occlusion
**BeginOcclusionTests** handles all occlusion tests in a frame. Unreal uses hardware occlusion queries for occlusion testing by default. In short, this works in 3 steps:
1. We render everything that we regard as an occluder (i.e. a large solid mesh) to a depth buffer
2. We create an occlusion query, issue it and render the prop we wish to determine occlusion for. This is done using a **z-test** and the **depth buffer** we produced in step 1. The query will return the number of pixels that passed the z-test, so if it is zero this means that the prop is behind a solid mesh. Since rendering a full prop mesh for occlusion can be expensive, we typically use the **bounding box** of that prop as a proxy. If it is not visible, then the prop is definitely not visible.
3. We read the query results back to the CPU and based on the number of pixels rendered we can decide to submit the prop for rendering or not (even if a small number of pixels are visible we might decide that it is not worth rendering the prop).
```
BeginOcclionTests
  ViewOcclionTests 0
    ShadowFrtumQueries
      DrawIndexed...
      API Calls
    PlanarReflectionQueries
    IndividualQueries   
      DrawIndexed...
      API Calls
    GroupedQueries
  ViewOcclionTests 1 //VR!!!
    ...
```

### Disadvantages
**Hardware occlusion** queries have disadvantages such as they require the renderer to submit one drawcall per mesh (or mesh batches) that needs determining occlusion for, which can **increase the number of drawcalls per frame significantly**, they require CPU-readback which introduces CPU-GPU sync points and makes the CPU wait until the GPU has finished processing the query. They are not that great for instanced geometry as well but we’ll ignore this for now.

The CPU-GPU sync point problem Unreal solves like any other engine that uses queries, by deferring reading the query data for a number of frames. This approach works, although it might introduce props popping in the screen with a fast moving camera (in practice it might not be a massive problem though since doing occlusion culling using bounding boxes is conservative, meaning that a mesh will in all likelihood be marked as visible before it actually is).

The additional drawcall overhead problem remains though and it is not easy to solve. Unreal tries mitigate it by grouping queries like this:
1. At first it *renders all opaque geometry to the z-buffer*
2. Then it issues *individual queries* for every prop it needs to test for occlusion.
3. At the end of the frame it retrieves query data from the previous (or further back) frame and decides prop visibility. If it is visible it marks it as renderable for the next frame. On the other hand, if it is invisible, it adds it to a *“grouped”* query which batches the bounding boxes of up to 8 props and uses that to determine visibility during the next frame. If the group becomes visible next frame (as a whole), it breaks it up and issues *individual queries* again.

If the camera and the props are static (or slowly moving), this approach reduces the number of necessary occlusion queries by a factor of 8. The only weirdness I noticed was during the batching of the occluded props which seems to be random and not based of spatial proximity.

This process corresponds to the **IndividualQueries** and **GroupedQueries** markers in the renderpass list above.

To wrap up the occlusion pass, **ShadowFrustumQueries** issues hardware occlusion queries for the bounding meshes of the local (point or spot) lights. If they are occluded there is no point in doing and lighting/shadowing calculations for them.

Worth noting is that although we have 4 shadow casting local lights in the scene (for which we need to calculate a shadowmap every frame frame), the number of drawcalls under ShadowFrustumQueries is 3. I suspect this is because one of the lights’ bounding volume intersects the camera’s near plane so Unreal assumes that it will be visible anyway.

Also, worth mentioning is that for **dynamic lights**, where a **cubemap shadowmap** will be calculated, we submit a sphere shape for occlusion tests,
![](https://interplayoflight.files.wordpress.com/2017/10/image6.png)

while for static dynamic lights which Unreal calculates per object shadows (more on this later), a frustum is submitted:
![](https://interplayoflight.files.wordpress.com/2017/10/image7.png)

Finally I assume that PlanarReflectionQueries refers to occlusion tests performed when calculating planar reflections (produced by transforming the camera behind/below the reflection plane and redrawing the meshes).

---

## Hi-Z buffer generation

Next, Unreal creates a **Hi-Z buffer** (passes HZB SetupMipXX) stored as a 16 floating point number (texture format R16_Float). This takes the depth buffer produced during the Z-prepass as in input and creates a mip chain (i.e. downsamples it successively) of depths. It also seems to resample the first mip to power of two dimensions for convenience:

![](https://interplayoflight.files.wordpress.com/2017/10/image8.png)
![](https://interplayoflight.files.wordpress.com/2017/10/image9.png)
![](https://interplayoflight.files.wordpress.com/2017/10/image10.png)

## Shadowmap rendering
```
ShadowDepth
  Atlas0
    Clear
    //Directional Light
    ...
  Atlas1
    Clear
    //Static Point Lights
    ...
  Atlas2
  Cubemap
    //Movable Point lights
    ...
```
For **stationary lights**, the renderer bakes shadows for static props and calculates shadows only for dynamic (movable) props.

With **movable lights** it calculates shadows for everything every frame (totally dynamic).

Finally for **static lights** it bakes light+shadows into the lightmap, so they should never appear during rendering.

???

## Light assignment
Next, the renderer switches to a **compute shader** to assign lights to a 3D grid (ComputeLightGrid pass), in a way similar to clustered shading. This light grid can be used to quickly retrieve the lights that affect a surface based on its position.

```
ComputeLightGrid
  CullLights 17x19x32 NumLights 3 NumCaptures 19 4 draws 4 prims 0 verts
  Compact 1 draws 1 prims 0 verts
```

## Volumetric Fog
Next up is volumetric fog calculations, again using compute shaders.
```
VolumetricFog
  InitializeVolumeAttributes
  LightScattering
  FinalIntegration
```
## G-Prepass
What follows is Unreal’s version of the **G-Prepass**, typically used in deferred rendering architectures. The purpose of this pass is to cache material properties in a set of rendertargets with the aim to reduce overdraw during expensive lighting and shading calculations.

---
# Wrapping up
Unreal’s renderer source is not extensively documented but it is fairly clean and easy to understand and by **following the drawcall list** it is easy to find the code that corresponds to it. It can be quite hard to follow what the shaders do in many cases, by **studying the source**, though as it uses conditional compilation extensively.

By default, Unreal’s renderer appears to place an emphasis on producing high quality images. It relies on baking of data (environment, light, volumetrics etc) as much as possible and uses temporal antialiasing to a great effect to improve image quality.

**It is worth keeping an eye out on the occlusion pass cost if you have lots of props in the scene and not many opportunities for occlusion (i.e. many large occluders). Also refraction on transparent props and particles forces them to render twice. Finally, many stationary or movable local lights may have an impact during the Lighting pass as they are rendered individually (and add to the light injection pass cost for transparencies and volumetrics).**
