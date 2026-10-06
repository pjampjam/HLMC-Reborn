// Owner artwork in a separate folder survives BlueMap webapp regeneration.
const brand = new URL('holylois-brand/', document.baseURI);
const link = (rel, name, type) => {
  document.querySelectorAll(`link[rel="${rel}"]`).forEach(el => el.remove());
  const el = document.createElement('link');
  el.rel = rel; el.href = new URL(name, brand).href; if (type) el.type = type;
  document.head.append(el);
};
link('icon', 'favicon-32.png', 'image/png');
link('manifest', 'site.webmanifest', 'application/manifest+json');
link('apple-touch-icon', 'apple-touch-icon.png');
document.title = 'Holy Lois - Live map';
for (const [name, content] of Object.entries({
  'theme-color': '#ffff55', 'description': 'The Holy Lois Minecraft live map, powered by BlueMap.',
  'og:site_name': 'Holy Lois', 'og:title': 'Holy Lois - Live map',
  'og:description': 'The Holy Lois Minecraft live map, powered by BlueMap.',
  'og:image': new URL('icon-512.png', brand).href
})) {
  let el = document.querySelector(`meta[name="${name}"]`);
  if (!el) { el = document.createElement('meta'); el.name = name; document.head.append(el); }
  el.content = content;
}
