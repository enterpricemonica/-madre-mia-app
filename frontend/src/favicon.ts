// Cambia en caliente el ícono de la pestaña del navegador (favicon).
// Lo usamos para que el favicon siga al LOGO del negocio → app reusable / white-label:
// cuando el restaurante cambia su logo en el admin, el iconito de la pestaña cambia solo.
export function setFavicon(url: string) {
  let link = document.querySelector("link[rel='icon']") as HTMLLinkElement | null
  if (!link) {
    link = document.createElement('link')
    link.rel = 'icon'
    document.head.appendChild(link)
  }
  link.href = url
}
