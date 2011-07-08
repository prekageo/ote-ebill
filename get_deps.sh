#!/bin/sh

curl "http://flot.googlecode.com/files/flot-0.6.tar.gz" | tar xz

mkdir -p jqueryui/js
mkdir -p jqueryui/css/smoothness/images

get_image() {
  wget -nv -O jqueryui/css/smoothness/images/$1 "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/smoothness/images/$1"
}

get_image "ui-bg_flat_0_aaaaaa_40x100.png"
get_image "ui-bg_flat_75_ffffff_40x100.png"
get_image "ui-bg_glass_55_fbf9ee_1x400.png"
get_image "ui-bg_glass_65_ffffff_1x400.png"
get_image "ui-bg_glass_75_dadada_1x400.png"
get_image "ui-bg_glass_75_e6e6e6_1x400.png"
get_image "ui-bg_glass_95_fef1ec_1x400.png"
get_image "ui-bg_highlight-soft_75_cccccc_1x100.png"
get_image "ui-icons_222222_256x240.png"
get_image "ui-icons_2e83ff_256x240.png"
get_image "ui-icons_454545_256x240.png"
get_image "ui-icons_888888_256x240.png"
get_image "ui-icons_cd0a0a_256x240.png"

wget -nv -O jqueryui/css/smoothness/jquery-ui-1.8.6.custom.css "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/themes/smoothness/jquery-ui.css"
wget -nv -O jqueryui/js/jquery-1.4.2.min.js                    "http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"
wget -nv -O jqueryui/js/jquery-ui-1.8.6.custom.min.js          "http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.6/jquery-ui.min.js"
