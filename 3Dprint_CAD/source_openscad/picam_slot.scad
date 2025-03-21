



module PicamV13(){
    thickness = 1;
    length = 24;
    width = 24;
    components_offset_width = 2;
    components_height = 2;
    components_width = 20;
    components_length = 20;
    plug_width = width;
    plug_length = 6;
    plug_height = 3;
    plug_offset_length = length - plug_length;
    plug_offset_width = 0;
    cam_sidelength = 9;
    cam_height = 6;
    cam_offset_width = 13-cam_sidelength/2;
    cam_offset_length = 12-cam_sidelength/2;
    
    translate([-cam_offset_length-cam_sidelength/2,-cam_offset_width-cam_sidelength/2,0])
    union(){
        cube([length, width, thickness]);
    
        translate([0, components_offset_width, thickness])
        color("blue", 1)
        cube([components_length, components_width, components_height]);
        
        translate([cam_offset_length,cam_offset_width,-cam_height])
        color("red", 1)
        union(){
            cube([cam_sidelength+7.5, cam_sidelength, cam_height]);
            translate([-7.5,0,2])
            cube([7.5, cam_sidelength, 4]);
        }
        
        translate([plug_offset_length,plug_offset_width,thickness])
        color("green", 1)
        cube([plug_length, plug_width, plug_height]);
    }
}


module straight_arch(){
    s = 100;
    w = 3;
    hc = 150;
    l = 35;
    cut = 130;
    translate([-s/2,0,-cut])
    difference(){
        translate([0,l/2])
        rotate([90,0,0])
        linear_extrude(l)
        polygon([[-w,0], [0,0], [s/2,hc], [s,0], 
             [s+w,0], [s/2+w,hc+w], [s/2-w,hc+w]]);
        
        translate([-200,-200])
        cube([500,500,cut]);
    }
}

module Cam_Top(){
    difference(){
        l = 35;
        w = 10;
        h = 8;
        union(){
            straight_arch();
            translate([-w-5,-l/2,h-1])
            color("orange", 1)
            union(){
                difference(){
                    cube([w,l,h]);
                    //translate([2,15,h-1])
                    //linear_extrude(1)
                    //text("x");
                }
                translate([h,l,-h])
                rotate([90,-90])
                linear_extrude(l)
                polygon([[2,3], [h,h], [h,0]]);
            }
        }
        sc = 1.12;
        translate([0,0,10])
        scale([sc,sc,sc])
        PicamV13();
    }
}

Cam_Top();
//PicamV13();



