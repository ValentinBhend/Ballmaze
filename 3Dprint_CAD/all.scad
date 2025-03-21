include <config.scad>;
use <HOLDER.scad>;
use <MAZE.scad>;
use <BOX.scad>;
use <CLIP.scad>;

module holder_maze(){
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    translate([0.5*w,-0.5*w,h+hw-w])
    maze_full(hole_coords, wall_coords_h, wall_coords_v, corner_coords);
    translate([-1.5*w,-1.5*w,0])
    holder();
}

module all(anglex=0, angley=0){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    po = pivot_offset;
    hc = h_clip;
    hb = box_height;
    wb = box_width;
    bs = box_shift;
    
    a=wb/2;
    translate([a,a])
    rotate([anglex,-angley])
    translate([-a,-a])
    holder_maze();
    translate([wb/2+s/2-po+bs,wb/2+s/2-po+bs,-hc-hb])
    rotate([0,0,180])
    box(true, 180, 0);
}

all(0,-0);
//all();
