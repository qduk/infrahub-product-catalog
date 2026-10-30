import { useState, type CSSProperties, type ReactNode } from 'react'
import { useFieldArray, useForm, useWatch, type FieldErrors, type Resolver } from 'react-hook-form'
import { submitProduct, type Catalog } from '../api'
import { blockStyle, byFrameworkOrder } from '../graph/blockStyle'
import { emptyForm, newSourceKey, submissionSchema, toPayload, type SubmissionForm } from './schema'

// Connects the Zod rules to React Hook Form, so each error shows next to its field.
const zodResolver: Resolver<SubmissionForm> = async (values) => {
  const result = submissionSchema.safeParse(values)
  if (result.success) return { values, errors: {} }
  const errors: Record<string, unknown> = {}
  for (const issue of result.error.issues) {
    let target = errors
    issue.path.forEach((part, index) => {
      const key = String(part)
      if (index === issue.path.length - 1) {
        target[key] ??= { type: issue.code, message: issue.message }
      } else {
        target[key] ??= {}
        target = target[key] as Record<string, unknown>
      }
    })
  }
  return { values: {}, errors: errors as FieldErrors<SubmissionForm> }
}

function errorAt(errors: FieldErrors<SubmissionForm>, path: string): string | undefined {
  let node: unknown = errors
  for (const part of path.split('.')) node = (node as Record<string, unknown> | undefined)?.[part]
  const message = (node as { message?: unknown } | undefined)?.message
  return typeof message === 'string' ? message : undefined
}

function FieldError({ errors, path }: { errors: FieldErrors<SubmissionForm>; path: string }) {
  const message = errorAt(errors, path)
  return message ? (
    <p className="field-error" role="alert">
      {message}
    </p>
  ) : null
}

function Step({ number, title, hint, children }: { number: number; title: string; hint?: string; children: ReactNode }) {
  return (
    <section className="form-step">
      <header className="form-step-header">
        <span className="form-step-number">{number}</span>
        <div>
          <h3>{title}</h3>
          {hint && <p className="form-step-hint">{hint}</p>}
        </div>
      </header>
      <div className="form-step-body">{children}</div>
    </section>
  )
}

function Field({ label, children, wide }: { label: string; children: ReactNode; wide?: boolean }) {
  return (
    <label className={wide ? 'field field-wide' : 'field'}>
      <span className="field-label">{label}</span>
      {children}
    </label>
  )
}

interface SourceChipsProps {
  label: string
  sources: SubmissionForm['sources']
  value: string[]
  onChange: (value: string[]) => void
}

function SourceChips({ label, sources, value, onChange }: SourceChipsProps) {
  const named = sources.filter((source) => source.title.trim() || source.url.trim())
  return (
    <div className="source-chips">
      <span className="field-label">{label}</span>
      {named.length === 0 ? (
        <p className="form-step-hint">Add a source in step 3 first.</p>
      ) : (
        <div className="chip-row">
          {named.map((source) => (
            <button
              key={source.key}
              type="button"
              className="chip"
              aria-pressed={value.includes(source.key)}
              onClick={() =>
                onChange(value.includes(source.key) ? value.filter((key) => key !== source.key) : [...value, source.key])
              }
            >
              {source.title || source.url}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

interface Props {
  catalog: Catalog
  onDone: () => void
}

export function SubmitForm({ catalog, onDone }: Props) {
  const [result, setResult] = useState<{ reference?: string; error?: string } | null>(null)
  const {
    register,
    control,
    handleSubmit,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<SubmissionForm>({ defaultValues: emptyForm(), resolver: zodResolver, mode: 'onSubmit' })
  const sources = useFieldArray({ control, name: 'sources' })
  const claims = useFieldArray({ control, name: 'claims' })
  const values = useWatch({ control }) as SubmissionForm
  const blocks = [...catalog.blocks].sort((a, b) => byFrameworkOrder(a.name, b.name))

  const onSubmit = async (form: SubmissionForm) => {
    const response = await submitProduct(toPayload(form))
    setResult(response.ok ? { reference: response.reference } : { error: response.message })
  }

  if (result?.reference) {
    return (
      <div className="form-card submit-done">
        <div className="submit-done-mark" aria-hidden="true">
          ✓
        </div>
        <h2>Thank you</h2>
        <p>
          Your submission was saved with the reference <code>{result.reference}</code>. A maintainer checks each fact
          against its source before it appears in the catalog.
        </p>
        <button type="button" className="primary-button" onClick={onDone}>
          Back to the catalog
        </button>
      </div>
    )
  }

  const pickSources =
    (path: `factSources.${'publisher' | 'description' | 'license_model' | 'status'}` | `claims.${number}.sources`) =>
    (value: string[]) =>
      setValue(path, value, { shouldDirty: true })
  const sourceList = values.sources ?? []

  return (
    <form className="form-card submit-form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <header className="form-intro">
        <h2>Submit a product</h2>
        <p>
          Every fact needs a source, such as the vendor's documentation. A maintainer reviews each submission before it
          appears in the catalog.
        </p>
      </header>

      <Step number={1} title="Product">
        <div className="field-grid">
          <Field label="Name">
            <input {...register('product.name')} maxLength={100} placeholder="e.g. NetBox" />
          </Field>
          <Field label="Home page">
            <input {...register('product.homepage_url')} type="url" maxLength={500} placeholder="https://" />
          </Field>
          <FieldError errors={errors} path="product.name" />
          <FieldError errors={errors} path="product.homepage_url" />
          <Field label="What the product does, in neutral words" wide>
            <textarea {...register('product.description')} maxLength={1000} rows={3} />
          </Field>
          <div className="field-wide">
            <FieldError errors={errors} path="product.description" />
          </div>
          <Field label="License model">
            <select {...register('product.license_model')}>
              <option value="">Not stated by any source</option>
              <option value="open_source">Open source</option>
              <option value="open_core">Open core</option>
              <option value="commercial">Commercial</option>
            </select>
          </Field>
          <Field label="Status">
            <select {...register('product.status')}>
              <option value="active">Active</option>
              <option value="discontinued">Discontinued</option>
            </select>
          </Field>
          {values.product?.status !== 'active' && (
            <Field label="Status date (optional)">
              <input {...register('product.status_date')} type="date" />
            </Field>
          )}
        </div>
      </Step>

      <Step number={2} title="Publisher">
        <div className="segmented" role="radiogroup" aria-label="Publisher">
          <label className="segment">
            <input type="radio" value="existing" {...register('publisherMode')} />
            <span>Already in the catalog</span>
          </label>
          <label className="segment">
            <input type="radio" value="new" {...register('publisherMode')} />
            <span>New publisher</span>
          </label>
        </div>
        {values.publisherMode === 'existing' ? (
          <div className="field-grid">
            <Field label="Publisher" wide>
              <select {...register('publisherExisting')}>
                <option value="">Choose a publisher</option>
                {catalog.publishers.map((publisher) => (
                  <option key={publisher.name} value={publisher.name}>
                    {publisher.name}
                  </option>
                ))}
              </select>
            </Field>
            <div className="field-wide">
              <FieldError errors={errors} path="publisherExisting" />
            </div>
          </div>
        ) : (
          <div className="field-grid">
            <Field label="Name">
              <input {...register('publisherNew.name')} maxLength={100} />
            </Field>
            <Field label="Home page">
              <input {...register('publisherNew.homepage_url')} type="url" maxLength={500} placeholder="https://" />
            </Field>
            <FieldError errors={errors} path="publisherNew.name" />
            <FieldError errors={errors} path="publisherNew.homepage_url" />
          </div>
        )}
      </Step>

      <Step number={3} title="Sources" hint="Each page that states a fact about the product. You link facts to them in the next step.">
        <div className="source-rows">
          {sources.fields.map((field, index) => (
            <div key={field.id} className="source-row">
              <input {...register(`sources.${index}.title`)} maxLength={200} placeholder="Title, e.g. Product documentation" aria-label="Source title" />
              <input {...register(`sources.${index}.url`)} type="url" maxLength={500} placeholder="https://" aria-label="Source link" />
              <button
                type="button"
                className="icon-button"
                onClick={() => sources.remove(index)}
                disabled={sources.fields.length === 1}
                aria-label="Remove this source"
              >
                ×
              </button>
              <FieldError errors={errors} path={`sources.${index}.title`} />
              <FieldError errors={errors} path={`sources.${index}.url`} />
            </div>
          ))}
        </div>
        {sources.fields.length < 20 && (
          <button type="button" className="add-button" onClick={() => sources.append({ key: newSourceKey(), title: '', url: '' })}>
            + Add a source
          </button>
        )}
        <FieldError errors={errors} path="sources" />
      </Step>

      <Step number={4} title="Which source states each fact">
        <SourceChips label="Publisher" sources={sourceList} value={values.factSources?.publisher ?? []} onChange={pickSources('factSources.publisher')} />
        <FieldError errors={errors} path="factSources.publisher" />
        <SourceChips label="Description" sources={sourceList} value={values.factSources?.description ?? []} onChange={pickSources('factSources.description')} />
        <FieldError errors={errors} path="factSources.description" />
        {values.product?.license_model && (
          <>
            <SourceChips label="License model" sources={sourceList} value={values.factSources?.license_model ?? []} onChange={pickSources('factSources.license_model')} />
            <FieldError errors={errors} path="factSources.license_model" />
          </>
        )}
        {values.product?.status !== 'active' && (
          <>
            <SourceChips label="Status" sources={sourceList} value={values.factSources?.status ?? []} onChange={pickSources('factSources.status')} />
            <FieldError errors={errors} path="factSources.status" />
          </>
        )}
      </Step>

      <Step number={5} title="Building blocks covered" hint="A maintainer checks each block against the framework's MUST and SHOULD requirements during review.">
        <div className="claim-cards">
          {claims.fields.map((field, index) => {
            const blockName = values.claims?.[index]?.block ?? ''
            return (
              <div
                key={field.id}
                className="claim-card"
                style={{ '--block-color': blockName ? blockStyle(blockName).color : 'var(--border-strong)' } as CSSProperties}
              >
                <div className="claim-card-top">
                  <select {...register(`claims.${index}.block`)} aria-label="Building block">
                    <option value="">Choose a building block</option>
                    {blocks.map((block) => (
                      <option key={block.name} value={block.name}>
                        {block.name}
                      </option>
                    ))}
                  </select>
                  <button
                    type="button"
                    className="icon-button"
                    onClick={() => claims.remove(index)}
                    disabled={claims.fields.length === 1}
                    aria-label="Remove this building block"
                  >
                    ×
                  </button>
                </div>
                <FieldError errors={errors} path={`claims.${index}.block`} />
                <textarea {...register(`claims.${index}.note`)} maxLength={1000} rows={2} placeholder="Note (optional)" aria-label="Note" />
                <SourceChips
                  label="Source for this claim"
                  sources={sourceList}
                  value={values.claims?.[index]?.sources ?? []}
                  onChange={pickSources(`claims.${index}.sources`)}
                />
                <FieldError errors={errors} path={`claims.${index}.sources`} />
              </div>
            )
          })}
        </div>
        {claims.fields.length < catalog.blocks.length && (
          <button type="button" className="add-button" onClick={() => claims.append({ block: '', note: '', sources: [] })}>
            + Add a building block
          </button>
        )}
        <FieldError errors={errors} path="claims" />
      </Step>

      {result?.error && (
        <p className="form-error" role="alert">
          {result.error}
        </p>
      )}
      <footer className="form-actions">
        <button type="button" className="link-button" onClick={onDone}>
          Cancel
        </button>
        <button type="submit" className="primary-button" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting…' : 'Submit for review'}
        </button>
      </footer>
    </form>
  )
}
