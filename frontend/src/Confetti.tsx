// Confeti puramente en CSS (sin librerías): un puñado de papelitos de colores que
// caen desde arriba. Cada uno arranca en una posición/tiempo/giro aleatorio para
// que se vea natural. Respeta prefers-reduced-motion (no se muestra si el usuario
// pidió menos movimiento — eso se controla en App.css).
const COLORS = ['#f4b400', '#e8643c', '#3aa655', '#4a90d9', '#d94aa0']

export function Confetti({ count = 36 }: { count?: number }) {
  const pieces = Array.from({ length: count }, (_, i) => {
    const left = Math.random() * 100          // dónde cae (horizontal, %)
    const delay = Math.random() * 0.5          // arranque escalonado (s)
    const duration = 1.8 + Math.random() * 1.4 // unos caen más lento que otros (s)
    const size = 6 + Math.random() * 6         // tamaño del papelito (px)
    return (
      <span
        key={i}
        className="confetti-piece"
        style={{
          left: `${left}%`,
          backgroundColor: COLORS[i % COLORS.length],
          width: `${size}px`,
          height: `${size * 0.4}px`,
          animationDelay: `${delay}s`,
          animationDuration: `${duration}s`,
        }}
      />
    )
  })
  return (
    <div className="confetti" aria-hidden="true">
      {pieces}
    </div>
  )
}
