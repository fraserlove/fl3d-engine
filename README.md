
![alt text](https://github.com/fraserlove/fl3d-engine/blob/master/images/FL3D_small.png)
# FL3D - 3D Rendering Engine
A 3D rendering engine to create, display and transform basic 3D objects. Includes a fully featured GUI, world lighting and object database storage. Currently the engine only has support for Windows however a Linux version may be avaliable soon. This engine was designed and developed by Fraser Love - me@fraser.love. For more detail into the design and implementation of the engine see the development report under the docs folder.

I wanted to create my own matrix functions and so I created a matrix class that can use the matrix_math module included to perform matrix operations to transform, rotate and scale the objects in the scene. This project was not meant to be the most efficient engine by using numpy and other libraries, but was instead intended to allow me to get a better understanding of 3d graphics.

The included lighting system has a very basic implementation that uses the average y position of the nodes in a surface on the screen to calculate the lighting based on a map between the height of the screen and 0 to 255. The engine also uses insertion sort to order all of the surfaces in the screen by their z position so that the closest surfaces get drawn last. The engines GUI allows for the creation, deletion of objects as well as editing their attributes. A sqlite database implementation is used to store object data so that so called 'world spaces' (all the objects in the scene) can be imported and saved.
