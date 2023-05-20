const mix = require("laravel-mix");

mix.setPublicPath("public");

mix.version();

if (mix.inProduction()) {
  mix.sourceMaps();
}

mix.js("resources/js/app.js", "public/js/app.js");
mix.sass("resources/sass/app.scss", "public/css/app.css");
mix.copyDirectory("resources/fonts", "public/fonts");
