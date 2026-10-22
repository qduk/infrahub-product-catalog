// Logo lookup. Files live in public/logos/ and are listed, with their sources, in logos.json.

import manifest from './logos.json'

export interface LogoEntry {
  slug: string
  file: string | null
  logo_of: 'product' | 'publisher'
  source_page: string | null
  file_url: string | null
  brand_guidelines_url: string | null
  notes: string | null
  tile: 'light' | 'dark'
}

export const LOGOS = manifest as LogoEntry[]

const bySlug = new Map(LOGOS.filter((entry) => entry.file).map((entry) => [entry.slug, entry]))

export function slugify(fullName: string): string {
  return fullName
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

export function logoFor(fullName: string): { url: string; tile: 'light' | 'dark' } | null {
  const entry = bySlug.get(slugify(fullName))
  return entry?.file ? { url: `/logos/${entry.file}`, tile: entry.tile } : null
}

export function logoUrl(fullName: string): string | null {
  return logoFor(fullName)?.url ?? null
}

export function initials(name: string): string {
  const words = name.split(/[^A-Za-z0-9]+/).filter(Boolean)
  const letters = words.length > 1 ? words[0][0] + words[1][0] : (words[0] ?? '?').slice(0, 2)
  return letters.toUpperCase()
}
