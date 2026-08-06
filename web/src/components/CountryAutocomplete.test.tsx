import { render, screen, within } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { useState } from 'react'

import type { CatalogV2 } from '../api/types'
import {
  CountryCodeAutocomplete,
  CountrySearchAutocomplete,
} from './CountryAutocomplete'

const countries: CatalogV2['countries'] = [
  {
    entity_id: 'country:USA',
    entity_type: 'COUNTRY',
    display_name: 'United States',
    country_codes: ['USA'],
    region: 'North America',
  },
  {
    entity_id: 'country:URY',
    entity_type: 'COUNTRY',
    display_name: 'Uruguay',
    country_codes: ['URY'],
    region: 'South America',
  },
  {
    entity_id: 'country:DEU',
    entity_type: 'COUNTRY',
    display_name: 'Germany',
    country_codes: ['DEU'],
    region: 'Europe',
  },
]

function SearchHarness() {
  const [value, setValue] = useState('')
  return (
    <label>
      <span>Search countries</span>
      <CountrySearchAutocomplete
        countries={countries}
        value={value}
        placeholder="Country name or code"
        onChange={setValue}
      />
    </label>
  )
}

function CodeHarness() {
  const [value, setValue] = useState('')
  return (
    <label>
      <span>Target destinations</span>
      <CountryCodeAutocomplete
        countries={countries}
        value={value}
        placeholder="DEU, CAN"
        onChange={setValue}
      />
    </label>
  )
}

test('search suggestions match country names and codes by typed prefix case-insensitively', async () => {
  const user = userEvent.setup()
  render(<SearchHarness />)

  await user.type(screen.getByRole('combobox', { name: /Search countries/ }), 'u')

  const listbox = screen.getByRole('listbox')
  expect(within(listbox).getByRole('option', { name: /United States/ })).toBeInTheDocument()
  expect(within(listbox).getByRole('option', { name: /Uruguay/ })).toBeInTheDocument()
  expect(within(listbox).queryByRole('option', { name: /Germany/ })).not.toBeInTheDocument()
})

test('country code fields insert the selected country code from a filtered dropdown', async () => {
  const user = userEvent.setup()
  render(<CodeHarness />)

  const input = screen.getByRole('combobox', { name: /Target destinations/ })
  await user.type(input, 'u')
  expect(screen.queryByRole('button', { name: /^U/ })).not.toBeInTheDocument()
  await user.click(screen.getByRole('option', { name: /United States/ }))

  expect(input).toHaveValue('USA')
  expect(screen.getByRole('button', { name: /USA/ })).toBeInTheDocument()
})
