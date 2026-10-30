// The submission form's rules. They match the service (frontend/api/catalog_web/submissions.py),
// so a form that passes here is accepted there.

import { z } from 'zod'

export const NAME_MAX = 100
export const TEXT_MAX = 1000
export const TITLE_MAX = 200
export const URL_MAX = 500
export const SOURCES_MAX = 20

const url = z
  .string()
  .trim()
  .min(1, 'Enter a link.')
  .max(URL_MAX, `Use at most ${URL_MAX} characters.`)
  .refine((value) => {
    try {
      return ['http:', 'https:'].includes(new URL(value).protocol)
    } catch {
      return false
    }
  }, 'Enter a link that starts with http:// or https://.')

const text = (max: number, label: string) =>
  z.string().trim().min(1, `Enter ${label}.`).max(max, `Use at most ${max} characters.`)

const sourceKeys = z.array(z.string()).max(SOURCES_MAX)

export const submissionSchema = z
  .object({
    product: z.object({
      name: text(NAME_MAX, 'the product name'),
      description: text(TEXT_MAX, 'a description'),
      homepage_url: url,
      license_model: z.enum(['', 'open_source', 'open_core', 'commercial']),
      status: z.enum(['active', 'discontinued']),
      status_date: z.string(),
    }),
    publisherMode: z.enum(['existing', 'new']),
    publisherExisting: z.string(),
    publisherNew: z.object({ name: z.string(), homepage_url: z.string() }),
    sources: z
      .array(z.object({ key: z.string(), title: text(TITLE_MAX, 'a title'), url }))
      .min(1, 'Add at least one source.')
      .max(SOURCES_MAX, `Use at most ${SOURCES_MAX} sources.`),
    factSources: z.object({
      publisher: sourceKeys.min(1, 'Pick the source that names the publisher.'),
      description: sourceKeys.min(1, 'Pick the source that supports the description.'),
      license_model: sourceKeys,
      status: sourceKeys,
    }),
    claims: z
      .array(
        z.object({
          block: z.string().min(1, 'Pick a building block.'),
          note: z.string().max(TEXT_MAX, `Use at most ${TEXT_MAX} characters.`),
          sources: sourceKeys.min(1, 'Pick the source that supports this claim.'),
        }),
      )
      .min(1, 'Add at least one building block the product covers.')
      .max(6),
  })
  .superRefine((form, ctx) => {
    if (form.publisherMode === 'existing' && !form.publisherExisting) {
      ctx.addIssue({ code: 'custom', path: ['publisherExisting'], message: 'Pick a publisher.' })
    }
    if (form.publisherMode === 'new') {
      const name = form.publisherNew.name.trim()
      if (!name || name.length > NAME_MAX) {
        ctx.addIssue({ code: 'custom', path: ['publisherNew', 'name'], message: `Enter a name of up to ${NAME_MAX} characters.` })
      }
      const link = url.safeParse(form.publisherNew.homepage_url)
      if (!link.success) {
        ctx.addIssue({ code: 'custom', path: ['publisherNew', 'homepage_url'], message: link.error.issues[0].message })
      }
    }
    if (form.product.license_model && !form.factSources.license_model.length) {
      ctx.addIssue({ code: 'custom', path: ['factSources', 'license_model'], message: 'Pick the source that states the license model.' })
    }
    if (form.product.status !== 'active' && !form.factSources.status.length) {
      ctx.addIssue({ code: 'custom', path: ['factSources', 'status'], message: 'Pick the source that states the status.' })
    }
    const urls = form.sources.map((source) => source.url.trim())
    urls.forEach((value, index) => {
      if (value && urls.indexOf(value) !== index) {
        ctx.addIssue({ code: 'custom', path: ['sources', index, 'url'], message: 'This link is already in the list.' })
      }
    })
    const seen = new Set<string>()
    form.claims.forEach((claim, index) => {
      if (claim.block && seen.has(claim.block)) {
        ctx.addIssue({ code: 'custom', path: ['claims', index, 'block'], message: 'Only one claim per building block.' })
      }
      seen.add(claim.block)
    })
  })

export type SubmissionForm = z.input<typeof submissionSchema>

let nextKey = 0
export const newSourceKey = () => `s${Date.now().toString(36)}${(nextKey++).toString(36)}`

export function emptyForm(): SubmissionForm {
  return {
    product: { name: '', description: '', homepage_url: '', license_model: '', status: 'active', status_date: '' },
    publisherMode: 'existing',
    publisherExisting: '',
    publisherNew: { name: '', homepage_url: '' },
    sources: [{ key: newSourceKey(), title: '', url: '' }],
    factSources: { publisher: [], description: [], license_model: [], status: [] },
    claims: [{ block: '', note: '', sources: [] }],
  }
}

export function toPayload(form: SubmissionForm) {
  return {
    product: {
      name: form.product.name.trim(),
      description: form.product.description.trim(),
      homepage_url: form.product.homepage_url.trim(),
      license_model: form.product.license_model || null,
      status: form.product.status,
      status_date: form.product.status_date || null,
    },
    publisher:
      form.publisherMode === 'existing'
        ? { existing: form.publisherExisting }
        : { new: { name: form.publisherNew.name.trim(), homepage_url: form.publisherNew.homepage_url.trim() } },
    sources: form.sources.map((source) => ({ key: source.key, title: source.title.trim(), url: source.url.trim() })),
    fact_sources: {
      publisher: form.factSources.publisher,
      description: form.factSources.description,
      license_model: form.product.license_model ? form.factSources.license_model : [],
      status: form.product.status !== 'active' ? form.factSources.status : [],
    },
    claims: form.claims.map((claim) => ({
      block: claim.block,
      note: claim.note.trim() || null,
      sources: claim.sources,
    })),
  }
}
