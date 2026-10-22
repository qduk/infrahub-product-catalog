import { useState } from 'react'
import { initials, logoFor } from './logos'

// A product's logo on a tile, or the initials of the product name when no logo is on file or the
// file fails to load. Logos are looked up by full name, because product names repeat across publishers.
export function Logo({ fullName, name, size = 'small' }: { fullName: string; name: string; size?: 'small' | 'large' }) {
  const logo = logoFor(fullName)
  const [failed, setFailed] = useState(false)
  const sizeClass = size === 'large' ? ' logo-tile-large' : ''
  if (!logo || failed) return <span className={`logo-tile logo-initials${sizeClass}`}>{initials(name)}</span>
  return (
    <span className={`logo-tile logo-tile-${logo.tile}${sizeClass}`}>
      <img src={logo.url} alt="" loading="lazy" draggable={false} onError={() => setFailed(true)} />
    </span>
  )
}
