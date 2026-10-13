/** Tailwind config for the static website (static_site/). */
module.exports = {
  content: [__dirname + "/../static_site/**/*.html", __dirname + "/../static_site/assets/site.js"],
  theme: { extend: {} },
  plugins: [],
};
