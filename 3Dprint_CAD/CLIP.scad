include <config.scad>;
use <clip_Tracta2022_mechadense.scad>

module clip_dummy(){
    w_clip = 20;
    linear_extrude(h_clip)
    square(w_clip, center=true);
}

function r(angle) = 
    sin(4*angle)^2;

module clip_cutout(w){
    r0 = 5;
    r1 = 7.5;
    p = [for (i=[0:360]) (r0+(r1-r0)*r(i))*[cos(i),sin(i)]];
        
    scale(1/clip_scale)
    linear_extrude(w)
    polygon(p);
}

module clip_single_visual(){
    sleeve();
    slider();
}

module clip_visual(){
    translate([22,0]){
        clip_single_visual();
        rotate([90,180])
        clip_single_visual();
    }
}

module clip_print(){
    scale(1/clip_scale)
    printplate();
}
//clip_dummy();
//clip_cutout(2);

//printplate();
//clip_single_visual();
//clip_visual();
clip_print();
