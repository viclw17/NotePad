# WebGL Fundamentals
Not a 3D API, just a rasterization engine
Runs on GPU, user provide vertex shader and fragment shader, all written in GLSL, pair together called a GLSL **program**.
Nearly all WebGL API is about setting up state for the pairs of shaders to run, AKA to supply data to GLSL program.

gl.drawArrays, gl.drawElements

# Data types
## Attributes / Buffers
Buffers are arrays of binary data upload to GPU. Contains
* positions
* normals
* texture coordinates, uv
* vertex colors
Not random access. Every time vertex shader is executed, next value from specified buffer is pulled out and assign to an attribute.

Attributes are used to specify how to pull data out of buffers and provide to vertex shader.
## Uniforms
global variables set before execute shader getProgramInfoLog

## Textures
Array of data can randomly access in shader program.

## varyings
Way for vertex shader to pass data to fragment shader.
Value set on varying by vertex shader will be interpolated while executing fragment shader.

# Hello World
WebGL only cares:
* clipspace(screenspace) coordinates
* colors
which are provided by:
* vertex shader
* fragment shader

clipspace(screenspace): -1 ~ +1
