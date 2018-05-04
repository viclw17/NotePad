# GCN
Graphics Core Next (GCN) is the codename for both a series of microarchitectures as well as for an instruction set.

https://gpuopen.com/optimizing-gpu-occupancy-resource-usage-large-thread-groups/

VGPRs (Vector General-Purpose Registers)

# HOW UNREAL RENDERS A FRAME

Particle Simulation

The frame begins with ParticleSimulation pass. It calculates particle motion and other properties for of each particle emitter we have in the scene on the GPU writing to two **render targets**,

* RGBA32_Float for positions and  
* RGBA16_Float for velocities (and a couple of time/life related data).

This, for example is the output for the RGBA32_Float rendertarget, each pixel corresponding to the world position of a sprite:

![](https://interplayoflight.files.wordpress.com/2017/10/image3.png)

## Z-Prepass

Next up is the PrePass render pass, which is essentially a z-prepass. This **renders all the opaque meshes** to an R24G8 depth buffer:

![](https://interplayoflight.files.wordpress.com/2017/10/image4.png?w=1024)

It is worth noting the Unreal uses **reverse-Z** when rendering to the depth buffer, meaning that the near plane is mapped to 1 and the far plane to 0. This allows for better precision along the depth range and reduces z-fighting on distant meshes.

The name of the rendering pass suggests that the pass was triggered by a “**DBuffer**”. This refers to the **decal buffer** Unreal Engine uses to render deferred decals.

This requires the scene depth so it activates the Z-prepass. The z-buffer is used in other contexts though, such as for occlusion calculations and screen space reflections as we will see next.

* PrePass DDM_AllOpaque(Forced by DBuffer)
  * View0
    * BeginRenderingPrePass
  * View1
* ResolveSceneDepth

## Testing for occlusion

**BeginOcclusionTests** handles all occlusion tests in a frame. Unreal uses hardware occlusion queries for occlusion testing by default. In short, this works in 3 steps:
1. We render everything that we regard as an occluder (i.e. a large solid mesh) to a depth buffer
2. We create an occlusion query, issue it and render the prop we wish to determine occlusion for. This is done using a *z-test* and the *depth buffer* we produced in step 1. The query will return the number of pixels that passed the z-test, so if it is zero this means that the prop is behind a solid mesh. Since rendering a full prop mesh for occlusion can be expensive, we typically use the *bounding box* of that prop as a proxy. If it is not visible, then the prop is definitely not visible.
3. We read the query results back to the CPU and based on the number of pixels rendered we can decide to submit the prop for rendering or not (even if a small number of pixels are visible we might decide that it is not worth rendering the prop).


* BeginOcclionTests
  * ViewOcclionTests 0
    * ShadowFrtumQueries
    * IndividualQueries
    * GroupedQueries
  * ViewOcclionTests 1 *VR!!!*
    * ShadowFrtumQueries
    * IndividualQueries
    * GroupedQueries

---

## Hi-Z buffer generation

Next, Unreal creates a **Hi-Z buffer** (passes HZB SetupMipXX) stored as a 16 floating point number (texture format R16_Float). This takes the depth buffer produced during the Z-prepass as in input and creates a mip chain (i.e. downsamples it successively) of depths. It also seems to resample the first mip to power of two dimensions for convenience:
