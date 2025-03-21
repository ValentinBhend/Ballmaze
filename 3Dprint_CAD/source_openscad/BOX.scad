include <config.scad>;
use <CLIP.scad>;
use <ARM.scad>; // only for visual

module servo_cutout(){
    r = 1.1;
    d = plate_thickness;
    rotate([90])
    linear_extrude(d){
        translate([0,11])
        circle(r, $fn=fn);
        translate([0,-26])
        circle(r, $fn=fn);
        translate([-8,-22.5])
        square([16,30]);
    }
}

module servo_visual(angle){
    d = plate_thickness;
    color([1,0,0])
    translate([-8,20,-22.5])
    rotate([90])
    linear_extrude(37)
    square([16,30]);
    translate([0,-14-d])
    rotate([90,90-angle])
    arm();
}

module box_wall(){
    h = box_height;
    w1 = box_width1;
    d = plate_thickness;
    rotate([90,0,90])
    linear_extrude(d)
    square([w1,h]);
}

module box_top(){
    h = box_height;
    w1 = box_width1;
    d = plate_thickness;
    translate([0,0,h-d])
    difference(){
        linear_extrude(d)
        square(w1);
        union(){
            translate([w1/2,w1/2,-d])
            clip_cutout(30);
            translate([3,26.5,0])
            cube([10,20,10]);
            translate([26.5,3,0])
            cube([20,10,10]);
        }
        
    }
}

module box(visual = false, 
           arm_anglex=105, arm_angley=105){
    h = box_height;
    w = box_width;
    w1 = box_width1;
    h_servo = servo_h_offset;
    d = plate_thickness;
    bs = box_shift;
    
    if (visual)
        translate([d,w/2+bs,h-h_servo])
        rotate(-90)
        servo_visual(arm_angley);
    difference(){
        box_wall();
        translate([d,w/2+bs,h-h_servo])
        rotate(-90)
        servo_cutout();
    }
    
    if (visual)
        translate([w/2+bs,d,h-h_servo])
        servo_visual(arm_anglex);
    
    difference(){
        translate([0,d])
        rotate(-90)
        box_wall();
        translate([w/2+bs,d,h-h_servo])
        servo_cutout();
    }
    translate([w1-d,0])
    difference(){
        box_wall();
        translate([0,w/2,h-5])
        rotate([90,0,90])
        linear_extrude(d)
        square([25,5], center=true);
    }
    translate([0,w1])
    rotate(-90)
    difference(){
        box_wall();
        translate([0,w/2,70])
        rotate([90,0,90])
        linear_extrude(d)
        circle(10);
    }
    
    difference(){
        box_top();
    }
    
    if (visual)
        rotate([0,0,180])
        translate([-w/2-bs,-w/2-bs,h])
        clip_dummy();
}


//box(true);
box();
//servo_visual();
//servo_cutout();














