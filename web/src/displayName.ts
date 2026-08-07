export type DisplayNamedDefinition = {
  displayName: string
  compactName: string | null
}

export type DisplayOrderedDefinition = {
  id: string
  sortOrder: number
}

export function byDisplayOrder(
  first: DisplayOrderedDefinition,
  second: DisplayOrderedDefinition,
): number {
  return first.sortOrder - second.sortOrder || first.id.localeCompare(second.id)
}

export function compactDisplayName(definition: DisplayNamedDefinition): string {
  return definition.compactName ?? definition.displayName
}

export function boundedCompactDisplayName(definition: DisplayNamedDefinition): string {
  const characters = Array.from(compactDisplayName(definition))
  return characters.length <= 22 ? characters.join('') : `${characters.slice(0, 19).join('')}...`
}

export function distinctDisplayName(
  definition: DisplayNamedDefinition,
): string | null {
  const compactName = compactDisplayName(definition)
  return compactName === definition.displayName ? null : definition.displayName
}
