Everything was designed in OpenSCAD which is a free CAD-software which is script-based. <br>
I printed everything on a Bambu Lab P1S 3D printer with PLA. Earlier version were also made on a Prusa MK3S with PLA and PETG. 

The .scad source file scripts have gotten really messy over time. So if you want to costumize something, brace yourself. 

The printplates are also available as .3mf files here. 

<ins>**Some remarks on the different models:**</ins>

**CLIP**: This is a slightly modified version of the part "Clip-On-2DOF-Joint (no torsion)" shared by the user "mechadense" on thingyverse: [https://www.thingiverse.com/thing:5533090](https://www.thingiverse.com/thing:5533090). It us licenced under the [Attribution-ShareAlike 3.0 Unported](https://creativecommons.org/licenses/by-sa/3.0/) licence and therefore also my version is. <br>
It is great, it enables tilting the maze without allowing it to rotate. 

**HOLDER**: This is the only part with sketchy overhangs and a lot of bridges. It might be safer to print the camera-holder-triangle on top seperately and in a different orientation, then glue it on. But it has worked for me as a single part. 

**MAZE**: The maze is best printed with ironing enabled for a smooth surface (might need advanced/expert options enabled). <br>
There is an empty maze without holes which can be useful for testing or learning the exact dynamics of the system. <br>
The maze layout can be modified with the lists "hole_coords, wall_coords_h, wall_coords_v and corner_coords" in the config.scad file
