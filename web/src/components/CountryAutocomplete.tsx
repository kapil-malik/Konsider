import {
  useId,
  useMemo,
  useState,
  type KeyboardEvent,
} from 'react'

import type { CatalogV2 } from '../api/types'
import { countryCode } from '../localityPresentation'

type CountryOption = {
  code: string
  name: string
  region?: string | null
}

const normalize = (value: string) => value.trim().toLocaleLowerCase()

const uniqueCodes = (codes: string[]) => [...new Set(codes.map((code) => code.toLocaleUpperCase()))]

const codesFromValue = (value: string) =>
  uniqueCodes(
    value
      .split(',')
      .map((item) => item.trim())
      .filter(Boolean),
  )

const activeToken = (value: string) => value.split(',').at(-1)?.trim() ?? ''

const replaceActiveToken = (value: string, code: string) => {
  const tokens = value.split(',')
  tokens.pop()
  return uniqueCodes([...tokens.map((item) => item.trim()).filter(Boolean), code]).join(', ')
}

const removeToken = (value: string, code: string) =>
  value
    .split(',')
    .map((item) => item.trim())
    .filter((item) => item && item.toLocaleUpperCase() !== code)
    .join(', ')

const countryOptions = (countries: CatalogV2['countries']): CountryOption[] =>
  countries
    .map((country) => ({
      code: country.country_codes[0] ?? countryCode(country.entity_id),
      name: country.display_name,
      region: country.region,
    }))
    .sort((first, second) => first.name.localeCompare(second.name))

const matchesStart = (option: CountryOption, query: string) => {
  const normalized = normalize(query)
  if (!normalized) return true
  return (
    normalize(option.name).startsWith(normalized) ||
    normalize(option.code).startsWith(normalized)
  )
}

function CountrySuggestions({
  id,
  options,
  activeIndex,
  onSelect,
}: {
  id: string
  options: CountryOption[]
  activeIndex: number
  onSelect: (option: CountryOption) => void
}) {
  if (!options.length) {
    return (
      <div className="country-suggestion-list is-empty" role="status">
        No countries match that entry.
      </div>
    )
  }

  return (
    <ul className="country-suggestion-list" id={id} role="listbox">
      {options.map((option, index) => (
        <li
          id={`${id}-${index}`}
          className={index === activeIndex ? 'is-active' : ''}
          role="option"
          aria-selected={index === activeIndex}
          key={option.code}
          onMouseDown={(event) => {
            event.preventDefault()
            onSelect(option)
          }}
        >
          <strong>{option.name}</strong>
          <span>{option.code}{option.region ? ` · ${option.region}` : ''}</span>
        </li>
      ))}
    </ul>
  )
}

export function CountrySearchAutocomplete({
  countries,
  value,
  placeholder,
  onChange,
}: {
  countries: CatalogV2['countries']
  value: string
  placeholder: string
  onChange: (value: string) => void
}) {
  const listId = useId()
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)
  const options = useMemo(
    () => countryOptions(countries).filter((option) => matchesStart(option, value)).slice(0, 8),
    [countries, value],
  )

  const selectOption = (option: CountryOption) => {
    onChange(option.code)
    setOpen(false)
    setActiveIndex(0)
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (!open && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      setOpen(true)
      return
    }
    if (!options.length) return
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((current) => Math.min(current + 1, options.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((current) => Math.max(current - 1, 0))
    } else if (event.key === 'Enter' && open) {
      event.preventDefault()
      selectOption(options[activeIndex])
    } else if (event.key === 'Escape') {
      setOpen(false)
    }
  }

  return (
    <div className="country-autocomplete">
      <input
        type="search"
        value={value}
        placeholder={placeholder}
        autoComplete="off"
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        aria-activedescendant={open && options[activeIndex] ? `${listId}-${activeIndex}` : undefined}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onChange={(event) => {
          onChange(event.currentTarget.value)
          setOpen(true)
          setActiveIndex(0)
        }}
        onKeyDown={handleKeyDown}
      />
      {open && (
        <CountrySuggestions
          id={listId}
          options={options}
          activeIndex={activeIndex}
          onSelect={selectOption}
        />
      )}
    </div>
  )
}

export function CountryCodeAutocomplete({
  countries,
  value,
  placeholder,
  onChange,
}: {
  countries: CatalogV2['countries']
  value: string
  placeholder: string
  onChange: (value: string) => void
}) {
  const listId = useId()
  const query = activeToken(value)
  const allOptions = useMemo(() => countryOptions(countries), [countries])
  const validCodes = useMemo(
    () => new Set(allOptions.map((option) => option.code.toLocaleUpperCase())),
    [allOptions],
  )
  const selectedCodes = useMemo(
    () => codesFromValue(value).filter((code) => validCodes.has(code)),
    [validCodes, value],
  )
  const [open, setOpen] = useState(false)
  const [activeIndex, setActiveIndex] = useState(0)
  const options = useMemo(
    () =>
      allOptions
        .filter((option) => !selectedCodes.includes(option.code.toLocaleUpperCase()))
        .filter((option) => matchesStart(option, query))
        .slice(0, 8),
    [allOptions, query, selectedCodes],
  )

  const selectOption = (option: CountryOption) => {
    onChange(replaceActiveToken(value, option.code))
    setOpen(false)
    setActiveIndex(0)
  }

  const removeCode = (code: string) => {
    onChange(removeToken(value, code))
  }

  const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
    if (!open && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
      setOpen(true)
      return
    }
    if (event.key === 'Backspace' && !query && selectedCodes.length) {
      removeCode(selectedCodes[selectedCodes.length - 1])
      return
    }
    if (!options.length) return
    if (event.key === 'ArrowDown') {
      event.preventDefault()
      setActiveIndex((current) => Math.min(current + 1, options.length - 1))
    } else if (event.key === 'ArrowUp') {
      event.preventDefault()
      setActiveIndex((current) => Math.max(current - 1, 0))
    } else if (event.key === 'Enter' && open) {
      event.preventDefault()
      selectOption(options[activeIndex])
    } else if (event.key === 'Escape') {
      setOpen(false)
    }
  }

  return (
    <div className="country-autocomplete country-code-autocomplete">
      {selectedCodes.length > 0 && (
        <div className="country-code-chips" aria-label="Selected country codes">
          {selectedCodes.map((code) => (
            <button type="button" key={code} onClick={() => removeCode(code)}>
              {code}
              <span aria-hidden="true">×</span>
            </button>
          ))}
        </div>
      )}
      <input
        value={value}
        placeholder={placeholder}
        autoComplete="off"
        role="combobox"
        aria-autocomplete="list"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        aria-activedescendant={open && options[activeIndex] ? `${listId}-${activeIndex}` : undefined}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
        onChange={(event) => {
          onChange(event.currentTarget.value)
          setOpen(true)
          setActiveIndex(0)
        }}
        onKeyDown={handleKeyDown}
      />
      {open && (
        <CountrySuggestions
          id={listId}
          options={options}
          activeIndex={activeIndex}
          onSelect={selectOption}
        />
      )}
    </div>
  )
}
