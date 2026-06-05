'use strict'

const fs = require('fs')
const path = require('path')

const INDEX_PATH = path.join(__dirname, '..', 'index.json')
const PROMPTS_ROOT = path.join(__dirname, '..', 'prompts')

let _index = null

function getIndex() {
  if (!_index) {
    _index = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf-8'))
  }
  return _index
}

class Prompt {
  constructor(meta, content) {
    this.name = meta.name
    this.category = meta.category
    this.description = meta.description
    this.path = meta.path
    this.content = content
  }

  toString() {
    return this.content
  }
}

/**
 * Load a prompt by name. Reads from disk only when called.
 * @param {string} name - Prompt name
 * @param {string} [category] - Optional: "claude" | "chatgpt" | "v0" | "cursor" | etc.
 * @returns {Prompt}
 * @example
 * const p = load('claude-5-06-2025')
 * console.log(p.content)
 */
function load(name, category = null) {
  const index = getIndex()
  const matches = index.prompts.filter(
    p => p.name === name && (category === null || p.category === category)
  )

  if (matches.length === 0) {
    throw new Error(
      `Prompt '${name}' not found. Use search('${name}') to find similar prompts.`
    )
  }

  if (matches.length > 1 && category === null) {
    const cats = matches.map(m => m.category)
    throw new Error(
      `Prompt '${name}' exists in multiple categories: ${cats.join(', ')}. ` +
      `Specify category, e.g. load('${name}', '${cats[0]}')`
    )
  }

  const meta = matches[0]
  const relPath = meta.path.replace(/^prompts\//, '')
  const promptPath = path.join(PROMPTS_ROOT, ...relPath.split('/'))
  const content = fs.readFileSync(promptPath, 'utf-8')
  return new Prompt(meta, content)
}

/**
 * Search prompts by keyword in name or description.
 * @param {string} query
 * @param {string} [category]
 * @param {number} [limit=10]
 * @returns {Array<{name: string, category: string, description: string}>}
 */
function search(query, category = null, limit = 10) {
  const index = getIndex()
  const q = query.toLowerCase()
  return index.prompts
    .filter(p =>
      (p.name.toLowerCase().includes(q) || p.description.toLowerCase().includes(q)) &&
      (category === null || p.category === category)
    )
    .slice(0, limit)
    .map(p => ({ name: p.name, category: p.category, description: p.description }))
}

/**
 * List all prompts, optionally filtered by category.
 * @param {string} [category]
 * @returns {Array<{name: string, category: string, description: string}>}
 */
function listPrompts(category = null) {
  const index = getIndex()
  return index.prompts
    .filter(p => category === null || p.category === category)
    .map(p => ({ name: p.name, category: p.category, description: p.description }))
}

/**
 * Return prompt counts per category.
 * @returns {Object}
 */
function categories() {
  const index = getIndex()
  const counts = {}
  for (const p of index.prompts) {
    counts[p.category] = (counts[p.category] || 0) + 1
  }
  counts.total = index.total
  return counts
}

module.exports = { load, search, listPrompts, categories, Prompt }
