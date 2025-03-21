include <config.scad>;


module plate(){
    w = plate_thickness;
    s = plate_sidelength;
    linear_extrude(w)
    square([s,s]);
}

module trapeze(){
    w = plate_thickness;
    //polygon([[0,0], [0,w], [w,2*w], [w,-w]]);
    //polygon([[0,0], [0,w], [w,2*w], [w,0]]);
    polygon([[0,0], [0,w], [w/2,w/2]]);
}

module slider(){
    s = plate_sidelength;
    w = plate_thickness;
    translate([0,-w])
    rotate([-90,0,0])
    linear_extrude(s+w)
    trapeze();
}
module slider2(){
    w = plate_thickness;
    s = plate_sidelength;
    translate([0,0,-w])
    mirror([0,0,1])
    slider();
}

module plate_with_slider(){
    w = plate_thickness;
    s = plate_sidelength;
    hw = wall_height;
    translate([0,-w])
    cube([s,w,hw+w]);
    plate();
    rotate([0,180,0])
    slider();
    translate([s,0,w])
    slider2();
}

module hole(nx,ny){
    g = gridsize;
    w = plate_thickness;
    translate([nx*4*g,ny*4*g,-w/2])
    union(){
        linear_extrude(w*2)
        translate([g*1.5,g*1.5])
        circle(g*1.5);
        translate([g*1.5,g*1.5,w])
        cylinder(w/2,g*1.5,g*1.5+w/2);
    }
}


module holes(coords){
    for (c = coords) {
        hole(c[0], c[1]);
    }
}

module wall_h(nx,ny){
    g = gridsize;
    hw = wall_height;
    w = plate_thickness;
    translate([0,3*g])
    translate([nx*4*g,ny*4*g])
    linear_extrude(hw+w)
    square([g*3,g]);
}

module wall_v(nx,ny){
    g = gridsize;
    hw = wall_height;
    w = plate_thickness;
    translate([3*g,0])
    translate([nx*4*g,ny*4*g])
    linear_extrude(hw+w)
    square([g,g*3]);
}


module walls(coords_h, coords_v){
    for (c = coords_h) {
        wall_h(c[0], c[1]);
    }
    for (c = coords_v) {
        wall_v(c[0], c[1]);
    }
}



module corners(coords){
    for (c = coords) {
        corner(c[0], c[1]);
    }
}
module corner(nx,ny){
    g = gridsize;
    hw = wall_height;
    w = plate_thickness;
    translate([3*g,3*g])
    translate([nx*4*g,ny*4*g])
    linear_extrude(hw+w)
    square([g,g]);
}

module maze_full(hole_coords, wall_coords_h, wall_coords_v, corner_coords){
    s = plate_sidelength;
    
    translate([s,0,0])
    rotate([0,0,90])
    union(){
        color([1,0,0]) walls(wall_coords_h, wall_coords_v);
        color([0,1,0]) corners(corner_coords);
    }
    
    difference(){
        plate_with_slider();
        translate([s,0,0])
        rotate([0,0,90])
        holes(hole_coords);
    }
}

maze_full(hole_coords, wall_coords_h, wall_coords_v, corner_coords);
//maze_full([], []);
//hole(0,0);

















