# Environment Cubemap
As a first step, the game renders a cubemap of the environment. This cubemap is _generated in realtime at each frame_, its purpose is to help render realistic reflections later. This part is **forward-rendered**.

This is exactly how the game does: each face is rendered into a 128x128 HDR texture. The same process is repeated for the 5 remaining faces, and we finally obtain the cubemap:

![](http://www.adriancourreges.com/img/blog/2015/gtav/a/01_cubemap_cube_shadow.png)

# Cubemap to Dual-Paraboloid Map
The environment cubemap we obtained is then converted to a dual-paraboloid map.

![](http://www.adriancourreges.com/img/blog/2015/gtav/a/a_01_cube_face_cross_tra.png)

![](http://www.adriancourreges.com/img/blog/2015/gtav/a/a_cubemap_to_sphere.jpg)

![](http://lh3.ggpht.com/GraphicsRunner/SH4TpImkomI/AAAAAAAAASw/Tsc2v951RAw/paraboloid5.jpg)

Why such a conversion? I guess it is (as always) about **optimization**: with a cubemap the fragment shader can potentially access _6 faces of 128x128 texels_, here the dual-paraboloid map brings it down to _2 “hemispheres” of 128x128_. Even better: since the camera is most of the time on the top of the car, most of the accesses will be done to the top hemisphere.
_The dual-paraboloid projection preserves the details of the reflection right at the top and the bottom, at the expense of the sides._ For GTA it’s fine: the car roofs and the hoods are usually facing up, they mainly need the reflection from the top to look good.

Plus, cubemaps can be problematic around their edges: if each face is mip-mapped independently some seams will be noticeable around the borders, and GPUs of older generation don’t support filtering across faces. A dual-paraboloid map does not suffer from such issues, it can be mip-mapped easily without creating seams.

>Update: as pointed-out in the comments below, it seems GTA IV was also relying on dual-paraboloid map, except it was not performed as a post-process from a cubemap: the meshes were distorted directly by a vertex-shader.

# Culling and Level of Detail
This step is processed by a **compute shader**, so I don’t have any illustration for it.

>Compute shaders operate differently from other shader stages. All of the other shader stages have a well-defined set of input values, some built-in and some user-defined. The frequency at which a shader stage executes is specified by the nature of that stage; vertex shaders execute once per input vertex, for example (though some executions can be skipped via caching). Fragment shader execution is defined by the fragments generated from the rasterization process.

>Compute shaders work very differently. The "space" that a compute shader operates on is largely abstract; it is up to each compute shader to decide what the space means. The number of compute shader executions is defined by the function used to execute the compute operation. Most important of all, compute shaders have no user-defined inputs and no outputs at all. The built-in inputs only define where in the "space" of execution a particular compute shader invocation is.

>Therefore, if a compute shader wants to take some values as input, it is up to the shader itself to fetch that data, via texture access, arbitrary image load, shader storage blocks, or other forms of interface. Similarly, if a compute shader is to actually compute anything, it must explicitly write to an image or shader storage block

Depending on its distance from the camera, an object will be drawn with a lower or higher-poly mesh, or not drawn at all.
For example, beyond a certain distance the grass or the flowers are never rendered. So this step calculates for each object if it will be rendered and at which LOD.

This is actually where the pipeline differs between a PS3 (lacking compute shader support) and a PC or a PS4: on the PS3 all these calculations would have to be run on the Cell or the SPUs.

# G-Buffer Generation
The “main” rendering is happening here. All the visible meshes are drawn one-by-one, but instead of calculating the shading immediately, the draw calls simply _output some shading-related information into different buffers called G-Buffer_.

GTA V uses **MRT(Multiple Render Targets)** so each draw call can output to 5 render targets at once.
Later, all these buffers are combined to calculate the final shading of each pixel. _Hence the name “deferred” in opposition to “forward” for which each draw call calculates the final shading value of a pixel._
For this step, only the opaque objects are drawn, transparent meshes like glass need special treatment in a deferred pipeline and will be treated later.

![](http://www.adriancourreges.com/img/blog/2015/gtav/a/02_gb_diffuse_2.jpg)  |  ![](http://www.adriancourreges.com/img/blog/2015/gtav/a/02_gb_normal_2.jpg)
--|--
![](http://www.adriancourreges.com/img/blog/2015/gtav/a/02_gb_spec_2.jpg) |  ![](http://www.adriancourreges.com/img/blog/2015/gtav/a/02_gb_irr_2.jpg)  

All these render targets are **LDR(Low dynamic range) buffers (RGBA, 8 bits per channel)** storing different information involved later in the calculation of the final shading value.
The buffers are:
- **Diffuse map**: it stores the “intrinsic color” of the mesh. It represents a property of the material, it is in theory not influenced by the lighting. But do you notice the white highlights on the car’s hood? Interestingly GTA V calculates the shading resulting from the sun directional light before outputting to the diffuse map.
  - **alpha channel** contains special “blending” information (more on that later).
- **Normal map**: it stores the normal vector for each pixel (R, G, B).
  - **alpha channel** is also used although I am not certain in which way: it looks like a binary mask for certain plants close to the camera.
- **Specular map**: it contains information related to specular/reflections:
  - Red: specular intensity
  - Green: glossiness (smoothness)
  - Blue: fresnel intensity (usually constant for all the pixels belonging to the same material)
- **Irradiance map**:
  - **Red channel** seems to contain the irradiance each pixel receives from the sun (based on the pixel’s normal and position, and the sun shining direction).
  - **Green channel** looks like the irradiance from a second light source.
  - **Blue channel** is the emissive property of the pixel (non-zero for neon, light bulbs).
  - Most of the **alpha channel** is not used except for marking the pixels corresponding to the character’s skin or the vegetation.

So, I was talking before about outputting simultaneously to 5 render targets, but I only presented 4 of them. 
The last render target is a **special depth-stencil buffer**. Here is what it looks like at the end of this pass:
