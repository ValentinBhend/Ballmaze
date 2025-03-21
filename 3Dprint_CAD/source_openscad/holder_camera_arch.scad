include <config.scad>;

module circ_arch(){
    s = plate_sidelength;
    w = plate_thickness;
    hc = camera_height;
    l = holder_wall_width;
    s1 = s + 2*w;
    scale([1,1,2*hc/s1])
    translate([s1/2,l/2])
    rotate([90,0,0])
    linear_extrude(l)
    difference(){
        half_circle(s1/2);
        half_circle(s1/2-w);
    }
}

module half_circle(radius) {
    rotate(180)
    intersection() {
        circle(radius, $fn=fn);
        translate([-radius, -radius]) square([2 * radius, radius]);
    }
}

module straight_arch(){
    s = plate_sidelength;
    w = plate_thickness;
    hc = camera_height;
    l = holder_wall_width;
    c = camera_width;
    difference(){
        translate([w,l/2])
        rotate([90,0,0])
        linear_extrude(l)
        polygon([[-w,0], [0,0], [s/2,hc], [s,0], 
             [s+w,0], [s/2+w,hc+w], [s/2-w,hc+w]]);
        //translate([s/2+w,0,hc-c])
        //cube([c*4,c,c], center=true);
    }
}

module cam(){
    x = 24;
    y = 27;
    d = 2;
    d_top = 6;
    d_bot = 5;
    d_bot2 = 4;
    x0_top = 5;
    x_top = 16;
    y0_top = 8;
    y_top = 10;
    x0_bot = 0;
    x_bot = 6;
    y0_bot = 2;
    y_bot = 21;
    x0_bot2 = 6;
    x_bot2 = 17;
    y0_bot2 = 2;
    y_bot2 = 22;
    rotate([180])
    translate([0,-1,0])
    union(){
        color([1,0,0]) cube([x,y,d]);
        translate([x0_top, y0_top, d])
        color([0,1,0]) cube([x_top,y_top,d_top]);
        translate([x0_bot, y0_bot, -d_bot])
        color([0,0,1]) cube([x_bot,y_bot,d_bot]);
        translate([x0_bot2, y0_bot2, -d_bot2])
        color([1,1,1]) cube([x_bot2,y_bot2,d_bot2]);
    }
}

module straight_arch_camhole(){
    s = plate_sidelength;
    hc = camera_height;
    scale_fit = 1.05;
    difference(){
        straight_arch();
        translate([s/2-12,12.5,hc-4])
        translate([0,12.5*(scale_fit-1)])
        scale(scale_fit)
        cam();
    }
    //translate([s/2-12,12.5,hc-4])
    //cam();
}

straight_arch_camhole();
//cam();

















