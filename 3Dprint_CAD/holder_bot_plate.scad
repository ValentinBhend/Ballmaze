include <config.scad>;
use <MAZE.scad>;
use <CLIP.scad>;

margin = 1.05; // sizing-up scale of the fit in part


module wall(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    translate([-1.5*w,w,-h-w])
    rotate([90])
    cube([s+3*w,2*w+h+hw,w]);
}

module cutout_front(){
    s = plate_sidelength;
    w = plate_thickness;
    translate([s,w])
    rotate([90])
    linear_extrude(w)
    scale(margin)
    trapeze();
    translate([0,0])
    rotate([90,0,180])
    linear_extrude(w)
    scale(margin)
    trapeze();
    cube([s,w,w]);
}

module wall_front(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    difference(){
        wall();
        union(){
            cutout_front();
            translate([0,0,hw/2])
            cube([s,w,hw]);
        }
    }
}

module wall_back(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    wall();
}

module wall_left(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    difference(){
        translate([-1.5*w,0,-h-w])
        cube([1.5*w,s+w,2*w+h+hw]);
        
        rotate([-90,180])
        linear_extrude(s+w)
        scale(margin)
        trapeze();
    }
}

module wall_right(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    //hole_out();
    difference(){
        translate([-1.5*w,0,-h-w])
        cube([1.5*w,s+w,2*w+h+hw]);
        hole_out();
        
        rotate([-90,180])
        linear_extrude(s+w)
        scale(margin)
        trapeze();
    }
}

module walls_bot(){
    s = plate_sidelength;
    w = plate_thickness;
    wall_front();
    translate([0,s+w])
    wall_back();
    wall_left();
    translate([s,s+w])
    rotate([0,0,180])
    wall_right();
}

module bot_plate_with_cutout(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    difference(){
        plate();
        translate([s/2-pivot_offset,s/2-pivot_offset,0])
        clip_cutout(30);
    }
}

module bot_part(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    translate([2*w,w,0])
    bot_plate_with_cutout();
    translate([2*w,0,h+w])
    walls_bot();
    slide();
}

module hole_out(){
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    r = hole_out_r;
    translate([-w*1.5,s-r,r-h])
    rotate([90,0,90])
    linear_extrude(1.5*w)
    union(){
        circle(r);
        translate([-r,-r])
        square([2*r,r]);
    }
}

module slide_addon(){
    r = hole_out_r;
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    h1 = hw + h;
    d = slide_width;
    translate([-w,-d*2+w,h-1])
    cube([w,d*2,hw]);
    translate([d,0,h-1])
    cube([d,w,hw]);
    translate([d*2,w,h-1])
    rotate([90])
    linear_extrude(w)
    polygon([[0,0], [d,0], [0,hw]]);
    translate([0,-2*d+w,h-1])
    rotate([90,0,-90])
    linear_extrude(w)
    polygon([[0,0], [d,0], [0,hw]]);
}

module slide(){
    r = hole_out_r;
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    h1 = hw + h + w;
    h3 = h1/3;
    d = slide_width;
    
    translate([s+w*3.5,s+w*2,h3])
    slider_corner();
    translate([w/2,s+w*2,2*h3])
    rotate([0,0,90])
    slider_corner();
    slide1();
    slide2();
    slide3();
    brim_front();
}

module slide1(){
    r = hole_out_r;
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    h1 = hw + h + w;
    h3 = h1/3;
    d = slide_width;
    translate([s+w*3.5,0])
    union(){
        rotate([90,0,90])
        linear_extrude(d)
        polygon([[0,0], [w+d,0], [s+2*w,h3], [s+2*w,h3+w], 
        [w+d,w], [w,w], [w,hw+w*2], [w+d,hw+w*2], [s+2*w,h3+hw+w*2], 
        [s+2*w,h3+hw+3*w], [d+w,hw+w*3], [0,hw+3*w]]);
        translate([d,0,0])
        rotate([90,0,90])
        linear_extrude(w)
        polygon([[0,0], [w+d,0], [s+2*w,h3], [s+2*w,hw+h3+w*3], 
        [w+d, hw+w*3], [0,hw+w*3]]);
    }
    
}

module slide2(){
    r = hole_out_r;
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    h1 = hw + h + w;
    h3 = h1/3;
    d = slide_width;
    translate([s+w*3.5,s+2*w])
    union(){
        rotate([-90,180,0])
        linear_extrude(d)
        union(){
            polygon([[0,h3], [s+3*w,2*h3], [s+3*w,2*h3+w], [0,h3+w]]);
            translate([0,hw+2*w])
            polygon([[0,h3], [s+3*w,2*h3], [s+3*w,2*h3+w], [0,h3+w]]);
        }
        translate([0,d,h3])
        rotate([-90,180,0])
        union(){
            linear_extrude(w)
            polygon([[0,0], [s+3*w,h3], [s+3*w,h3+hw+w*3], [0,hw+3*w]]);
            translate([0,0,-d-w])
            linear_extrude(w)
            polygon([[0,0], [s+3*w,h3], [s+3*w,h3+hw+w*3], [0,hw+3*w]]);
        }
        
    }
}

module slide3(){
    r = hole_out_r;
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    h1 = hw + h + w;
    h3 = h1/3;
    d = slide_width;
    translate([w/2,s+2*w])
    union(){
        rotate([-90,180,90])
        union(){
            linear_extrude(d)
            polygon([[s+w,3*h3+w], [s+w-d,3*h3+w], [0,2*h3+w], 
            [0,2*h3], [s+w-d,3*h3], [s+2*w,3*h3], 
            [s+2*w,3*h3+w*3+hw], [s+w,3*h3+w*3+hw], 
            [s+w-d, 3*h3+w*3+hw], [0,2*h3+w*3+hw], 
            [0,2*h3+w*2+hw], [s+w-d, 3*h3+w*2+hw], [s+w, 3*h3+w*2+hw]]);
            translate([0,1,-6*w])
            linear_extrude(d+6*w)
            polygon([[s+w,3*h3+w], [s+2*w, 3*h3+w], 
            [s+2*w, 3*h3+hw+3*w-1], [s+w, 3*h3+hw+3*w-1]]);
        }
        translate([-d,0,2*h3])
        rotate([-90,180,90])
        union(){
            linear_extrude(w)
            polygon([[0,0], [s+w-d,h3], [s+2*w,h3], [s+2*w,h3+hw+3*w], 
            [s+w-d,h3+hw+3*w], [0,hw+3*w]]);
            translate([0,0,-d-w])
            linear_extrude(w)
            polygon([[0,0], [s+w-d,h3],
            [s+w-d,h3+hw+3*w], [0,hw+3*w]]);
        }
    }
}

module brim_front(){
    r = hole_out_r;
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    h1 = hw + h + w;
    h3 = h1/3;
    d = slide_width;
    translate([0,w,w+1])
    union(){
        rotate([90,0,0])
        union(){
            linear_extrude(d+w)
            polygon([[-d-w/2,h1], [s+4.5*w+d,h1], 
            [s+4.5*w+d,h1+w], [-d-w/2,h1+w]]);
            linear_extrude(w)
            polygon([[s+2*w,h1-2*w], [s+3*w,h1-2*w], [s+3*w,h1-3*w],
            [s+4.5*w+d,h1-3*w], 
            [s+4.5*w+d,h1+w], [s+2*w,h1+w]]);
            translate([w/2,hw+w*4,0])
            cube([w*1.5,w,w]);
        }
        
    }
}

module slider_corner(){
    r = hole_out_r;
    s = plate_sidelength;
    w = plate_thickness;
    h = bot_plate_maze_space;
    hw = wall_height;
    h1 = hw + h + w;
    h3 = h1/3;
    d = slide_width;
    
    difference(){
        cube([d+w, d+w, hw+3*w]);
        translate([0,0,w])
        cube([d,d,hw+w]);
    }
}

//slider_corner();
bot_part();

//slide();
//wall_with_slide();














