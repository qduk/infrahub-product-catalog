import { useState } from 'react'
import { useFieldArray, useForm, useWatch, type FieldErrors, type Resolver } from 'react-hook-form'
import { submitProduct, type Catalog } from '../api'
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
  return message ? <p className="field-error" role="alert">{message}</p> : null
}

interface SourcePickerProps {
  label: string
  sources: SubmissionForm['sources']
  value: string[]
  onChange: (value: string[]) => void
}

function SourcePicker({ label, sources, value, onChange }: SourcePickerProps) {
  const named = sources.filter((source) => source.title.trim() || source.url.trim())
  return (
    <fieldset className="source-picker">
      <legend>{label}</legend>
      {named.length === 0 && <p className="hint">Add sources above first.</p>}
      {named.map((source) => (
        <label key={source.key} className="toggle">
          <input
            type="checkbox"
            checked={value.includes(source.key)}
            onChange={() =>
              onChange(value.includes(source.key) ? value.filter((key) => key !== source.key) : [...value, source.key])
            }
          />
          {source.title || source.url}
        </label>
      ))}
    </fieldset>
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

  const onSubmit = async (form: SubmissionForm) => {
    const response = await submitProduct(toPayload(form))
    setResult(response.ok ? { reference: response.reference } : { error: response.message })
  }

  if (result?.reference) {
    return (
      <div className="submit-done">
        <h2>Thank you</h2>
        <p>
          Your submission was saved with the reference <code>{result.reference}</code>. A maintainer checks each fact
          against its source before it appears in the catalog.
        </p>
        <button type="button" onClick={onDone}>
          Back to the catalog
        </button>
      </div>
    )
  }

  const pickSources = (path: `factSources.${'publisher' | 'description' | 'license_model' | 'status'}` | `claims.${number}.sources`) =>
    (value: string[]) => setValue(path, value, { shouldDirty: true })

  return (
    <form className="submit-form" onSubmit={handleSubmit(onSubmit)} noValidate>
      <h2>Submit a product</h2>
      <p className="hint">
        Every fact needs a source, such as the vendor's documentation. A maintainer reviews each submission before it
        appears in the catalog.
      </p>

      <section>
        <h3>Product</h3>
        <label>
          Name
          <input {...register('product.name')} maxLength={100} />
        </label>
        <FieldError errors={errors} path="product.name" />
        <label>
          Description: what the product does, in neutral words
          <textarea {...register('product.description')} maxLength={1000} rows={3} />
        </label>
        <FieldError errors={errors} path="product.description" />
        <label>
          Home page
          <input {...register('product.homepage_url')} type="url" maxLength={500} placeholder="https://" />
        </label>
        <FieldError errors={errors} path="product.homepage_url" />
        <label>
          License model
          <select {...register('product.license_model')}>
            <option value="">Not stated by any source</option>
            <option value="open_source">Open source</option>
            <option value="open_core">Open core</option>
            <option value="commercial">Commercial</option>
          </select>
        </label>
        <label>
          Status
          <select {...register('product.status')}>
            <option value="active">Active</option>
            <option value="discontinued">Discontinued</option>
            <option value="acquired">Acquired</option>
          </select>
        </label>
        {values.product?.status !== 'active' && (
          <label>
            Status date (optional)
            <input {...register('product.status_date')} type="date" />
          </label>
        )}
      </section>

      <section>
        <h3>Publisher</h3>
        <label className="toggle">
          <input type="radio" value="existing" {...register('publisherMode')} />
          Already in the catalog
        </label>
        <label className="toggle">
          <input type="radio" value="new" {...register('publisherMode')} />
          New publisher
        </label>
        {values.publisherMode === 'existing' ? (
          <>
            <select {...register('publisherExisting')} aria-label="Publisher">
              <option value="">Choose a publisher</option>
              {catalog.publishers.map((publisher) => (
                <option key={publisher.name} value={publisher.name}>
                  {publisher.name}
                </option>
              ))}
            </select>
            <FieldError errors={errors} path="publisherExisting" />
          </>
        ) : (
          <>
            <label>
              Name
              <input {...register('publisherNew.name')} maxLength={100} />
            </label>
            <FieldError errors={errors} path="publisherNew.name" />
            <label>
              Home page
              <input {...register('publisherNew.homepage_url')} type="url" maxLength={500} placeholder="https://" />
            </label>
            <FieldError errors={errors} path="publisherNew.homepage_url" />
          </>
        )}
      </section>

      <section>
        <h3>Sources</h3>
        <p className="hint">List each page that states a fact about the product. You pick from this list below.</p>
        {sources.fields.map((field, index) => (
          <div key={field.id} className="source-row">
            <label>
              Title
              <input {...register(`sources.${index}.title`)} maxLength={200} />
            </label>
            <label>
              Link
              <input {...register(`sources.${index}.url`)} type="url" maxLength={500} placeholder="https://" />
            </label>
            {sources.fields.length > 1 && (
              <button type="button" className="link-button" onClick={() => sources.remove(index)}>
                Remove
              </button>
            )}
            <FieldError errors={errors} path={`sources.${index}.title`} />
            <FieldError errors={errors} path={`sources.${index}.url`} />
          </div>
        ))}
        {sources.fields.length < 20 && (
          <button type="button" onClick={() => sources.append({ key: newSourceKey(), title: '', url: '' })}>
            Add a source
          </button>
        )}
        <FieldError errors={errors} path="sources" />
      </section>

      <section>
        <h3>Which source states each fact</h3>
        <SourcePicker label="Publisher" sources={values.sources ?? []} value={values.factSources?.publisher ?? []} onChange={pickSources('factSources.publisher')} />
        <FieldError errors={errors} path="factSources.publisher" />
        <SourcePicker label="Description" sources={values.sources ?? []} value={values.factSources?.description ?? []} onChange={pickSources('factSources.description')} />
        <FieldError errors={errors} path="factSources.description" />
        {values.product?.license_model && (
          <>
            <SourcePicker label="License model" sources={values.sources ?? []} value={values.factSources?.license_model ?? []} onChange={pickSources('factSources.license_model')} />
            <FieldError errors={errors} path="factSources.license_model" />
          </>
        )}
        {values.product?.status !== 'active' && (
          <>
            <SourcePicker label="Status" sources={values.sources ?? []} value={values.factSources?.status ?? []} onChange={pickSources('factSources.status')} />
            <FieldError errors={errors} path="factSources.status" />
          </>
        )}
      </section>

      <section>
        <h3>Building blocks covered</h3>
        {claims.fields.map((field, index) => (
          <div key={field.id} className="claim-row">
            <label>
              Building block
              <select {...register(`claims.${index}.block`)}>
                <option value="">Choose a building block</option>
                {catalog.blocks.map((block) => (
                  <option key={block.name} value={block.name}>
                    {block.name}
                  </option>
                ))}
              </select>
            </label>
            <FieldError errors={errors} path={`claims.${index}.block`} />
            <label>
              Coverage
              <select {...register(`claims.${index}.extent`)}>
                <option value="full">Full: covers the whole building block</option>
                <option value="partial">Partial: covers part of it</option>
              </select>
            </label>
            <label>
              Note (optional)
              <textarea {...register(`claims.${index}.note`)} maxLength={1000} rows={2} />
            </label>
            <SourcePicker
              label="Source for this claim"
              sources={values.sources ?? []}
              value={values.claims?.[index]?.sources ?? []}
              onChange={pickSources(`claims.${index}.sources`)}
            />
            <FieldError errors={errors} path={`claims.${index}.sources`} />
            {claims.fields.length > 1 && (
              <button type="button" className="link-button" onClick={() => claims.remove(index)}>
                Remove this building block
              </button>
            )}
          </div>
        ))}
        {claims.fields.length < catalog.blocks.length && (
          <button type="button" onClick={() => claims.append({ block: '', extent: 'full', note: '', sources: [] })}>
            Add a building block
          </button>
        )}
        <FieldError errors={errors} path="claims" />
      </section>

      {result?.error && (
        <p className="form-error" role="alert">
          {result.error}
        </p>
      )}
      <div className="form-actions">
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Submitting…' : 'Submit for review'}
        </button>
        <button type="button" className="link-button" onClick={onDone}>
          Cancel
        </button>
      </div>
    </form>
  )
}
