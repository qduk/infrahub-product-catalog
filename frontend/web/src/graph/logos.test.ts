import { existsSync, readdirSync, readFileSync } from 'node:fs'
import { join } from 'node:path'
import { describe, expect, it } from 'vitest'
import { initials, LOGOS, logoUrl, slugify } from './logos'

const LOGO_DIR = join(__dirname, '..', '..', 'public', 'logos')
const BRAND_DIR = join(__dirname, '..', '..', 'public', 'brand')
const filesOnDisk = existsSync(LOGO_DIR) ? readdirSync(LOGO_DIR) : []
const brandFiles = existsSync(BRAND_DIR) ? readdirSync(BRAND_DIR) : []

describe('logo manifest', () => {
  it('gives every logo file a source page and the address it was downloaded from', () => {
    for (const entry of LOGOS.filter((item) => item.file)) {
      expect(entry.source_page, entry.slug).toMatch(/^https?:\/\//)
      expect(entry.file_url, entry.slug).toMatch(/^https?:\/\//)
      expect(filesOnDisk, entry.slug).toContain(entry.file)
    }
  })

  it('lists every file on disk in the manifest', () => {
    const listed = new Set(LOGOS.map((entry) => entry.file))
    for (const file of filesOnDisk) expect(listed.has(file), file).toBe(true)
  })

  it('has one entry per slug', () => {
    const slugs = LOGOS.map((entry) => entry.slug)
    expect(new Set(slugs).size).toBe(slugs.length)
  })

  it('keeps SVG logos free of scripts, event handlers, embedded content and external links', () => {
    const svgs = [
      ...filesOnDisk.filter((name) => name.endsWith('.svg')).map((name) => join(LOGO_DIR, name)),
      ...brandFiles.filter((name) => name.endsWith('.svg')).map((name) => join(BRAND_DIR, name)),
    ]
    for (const file of svgs) {
      const svg = readFileSync(file, 'utf8')
      expect(svg, file).not.toMatch(/<script/i)
      expect(svg, file).not.toMatch(/\son[a-z]+\s*=/i)
      expect(svg, file).not.toMatch(/<foreignObject/i)
      expect(svg, file).not.toMatch(/(?:xlink:)?href\s*=\s*["']\s*(?:https?:|\/\/|javascript:)/i)
      expect(svg, file).not.toMatch(/url\(\s*["']?(?:https?:|\/\/)/i)
    }
  })
})

describe('logo lookup', () => {
  it('turns a full name into the file slug', () => {
    expect(slugify('Cloud Native Computing Foundation (CNCF) Backstage')).toBe(
      'cloud-native-computing-foundation-cncf-backstage',
    )
    expect(slugify("Slurp'it Slurp'it")).toBe('slurp-it-slurp-it')
  })

  it('returns no logo for an unknown product, so the node shows initials', () => {
    expect(logoUrl('Nobody Unknown Tool')).toBeNull()
    expect(initials('Nobody Unknown Tool')).toBe('NU')
    expect(initials('Kentik')).toBe('KE')
  })
})
