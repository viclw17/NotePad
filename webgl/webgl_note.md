# WebGL Fundamentals
Not a 3D API, just a rasterization engine
Runs on GPU, user provide vertex shader and fragment shader, all written in GLSL, pair together called a GLSL **program**.
Nearly all WebGL API is about setting up state for the pairs of shaders to run, AKA to supply data to GLSL program.

gl.drawArrays, gl.drawElements

## Data types
### Attributes / Buffers
Buffers are **arrays of binary data** upload to GPU. Contains
* positions
* normals
* texture coordinates, uv
* vertex colors
Not random access. Every time vertex shader is executed, next value from specified buffer is pulled out and assign to an attribute.

Attributes are used to specify how to pull data out of buffers and provide to vertex shader.
### Uniforms
global variables set before execute shader getProgramInfoLog

### Textures
Array of data can randomly access in shader program.

### varyings
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
> Converting from clip space to screen space if the canvas size happened to be 400x300:
clip space      screen space
   0, 0       ->   200, 150
   0, 0.5     ->   200, 225
 0.7, 0       ->   340, 150

# How it works
* 1. processes vertices (or streams of data) into clipspace vertices.
* 2. draw pixels based on the first part.

```javascript
function setGeometry(gl){
    gl.bufferData(
        gl.ARRAY_BUFFER,
        new Float32Array([
               0, -100,
             150,  125,
            -175,  100]),
        gl.STATIC_DRAW);
}
function drawScene(){
    //...
    var primitiveType = gl.TRIANGLES;
    var offset = 0;
    var count = 3;
    gl.drawArrays(primitiveType, offset, count);
}
```
```c
// vertex shader
varying vec4 v_color;
attribute vec4 a_position;
void main(){
    gl_Position = a_position;
    v_color = gl_Position * 0.5 + 0.5;
}
// fragment shader
varying vec4 v_color;
void main(){
    gl_FragColor = v_color;
}
```
Buffers are the way of getting vertex and other per-vertex data onto GPU.
* *var buf = gl.createBuffer();*
* *gl.bindBuffer(gl.ARRAY_BUFFER, buf);* - set that buffer as the working buffer
* *gl.bufferData(gl.ARRAY_BUFFER, someData, gl.STATIC_DRAW);* - copy data into buffer
these are all **initialization**.

Pull data out of buffer and provide it to the vertex shader's **attributes**.

Attributes can use *float, vec2, vec3, vec4, mat2, mat3, mat4* as types.

* *var positionLoc = gl.getAttribLocation(someShaderProgram, "a_position");* - given a shader program you made, first we look up what locations it assigned to the attributes.
* *gl.enableVertexAttribArray(positionLoc);* - turn on pull data out of a buffer for this attribute
* gl.bindBuffer(gl.ARRAY_BUFFER, someBuffer);
* *gl.vertexAttribPointer(
    location,
    numComponents,
    typeOfData,
    normalizeFlag,
    strideToNextPieceOfData,
    offsetIntoBuffer);*
these are all **initialization**.

> The **Float32Array** typed array represents an array of 32-bit floating point numbers (corresponding to the C float data type) in the platform byte order.

bit = 1 or 0
8bits       --> 1byte, 2^8 = 256
32bit float --> 4byte, 2^32 = 4294967296
16bit short --> 2byte, 2^16 = 65536

* BYTE goes from -128 to 127
* UNSIGNED_BYTE goes from 0 to 255
* SHORT goes from -32768 to 32767

https://web.stanford.edu/class/cs101/bits-bytes.html

> Using a full float each for red, green, blue and alpha would use 16 bytes per vertex per color. If you have complicated geometry that can add up to a lot of bytes. Instead you could convert your colors to UNSIGNED_BYTEs where 0 represents 0.0 and 255 represents 1.0. Now you'd only need 4 bytes per color per vertex, a 75% savings.

# GLSL
## vertex shader
* It's job is to generate clipspace coordinates.
* It's called once per vertex.

get data in 3 ways:
* Attributes (data pulled from buffers), see previous section # How it works.
* Uniforms (values that stay the same during for all vertices of a single draw call)
* Textures (data from pixels/texels)
