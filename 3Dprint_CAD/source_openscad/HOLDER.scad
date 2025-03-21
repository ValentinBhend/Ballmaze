include <config.scad>;
use <holder_bot_plate.scad>;
use <holder_camera_arch.scad>;

module holder(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    translate([w,s/2+w,h+hw+2*w])
    straight_arch_camhole();
    bot_part();
}

holder();








