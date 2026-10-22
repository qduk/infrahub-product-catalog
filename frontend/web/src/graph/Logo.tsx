import { useState } from 'react'
import { initials, logoFor } from './logos'

// A product's logo on a tile, or its initials when no logo is on file or the file fails to load.
export function Logo({ fullName, size = 'small' }: { fullName: string; size?: 'small' | 'large' }) {
  const logo = logoFor(fullName)
  const [failed, setFailed] = useState(false)
  const sizeClass = size === 'large' ? ' logo-tile-large' : ''
  if (!logo || failed) return <span className={`logo-tile logo-initials${sizeClass}`}>{initials(fullName)}</span>
  return (
    <span className={`logo-tile logo-tile-${logo.tile}${sizeClass}`}>
      <img src={logo.url} alt="" loading="lazy" draggable={false} onError={() => setFailed(true)} />
    </span>
  )
}
