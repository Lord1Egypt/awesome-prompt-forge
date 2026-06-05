#!/usr/bin/env node
'use strict'

const { load, search, listPrompts, categories } = require('../src/index')

const [,, command, ...args] = process.argv

function help() {
  console.log(`
awesome-prompt-forge CLI — 350+ lazy-loading AI system prompts

Usage:
  promptforge load <name> [--category <cat>]    Load and print a prompt
  promptforge search <query> [--category <cat>]  Search prompts
  promptforge list [--category <cat>]            List all prompts
  promptforge stats                              Show counts per category

Categories: claude, chatgpt, v0, cursor, copilot, grok, devin, perplexity, llama, writing, general, tools
`)
}

function getOpt(args, flag) {
  const i = args.indexOf(flag)
  return i !== -1 ? args[i + 1] : null
}

if (!command || command === '--help' || command === '-h') {
  help()
  process.exit(0)
}

if (command === 'load') {
  const name = args[0]
  if (!name) { console.error('Usage: promptforge load <name>'); process.exit(1) }
  const category = getOpt(args, '--category') || getOpt(args, '-c')
  try {
    const p = load(name, category)
    console.log(`# ${p.name} [${p.category}]\n`)
    console.log(p.content)
  } catch (e) {
    console.error('Error:', e.message)
    process.exit(1)
  }
}

else if (command === 'search') {
  const query = args[0]
  if (!query) { console.error('Usage: promptforge search <query>'); process.exit(1) }
  const category = getOpt(args, '--category') || getOpt(args, '-c')
  const limitArg = getOpt(args, '--limit') || getOpt(args, '-n')
  const limit = limitArg ? parseInt(limitArg) : 10
  const results = search(query, category, limit)
  if (!results.length) {
    console.log(`No prompts found for '${query}'`)
  } else {
    for (const r of results) {
      console.log(`[${r.category.padEnd(12)}] ${r.name}`)
      if (r.description) console.log(`               ${r.description.slice(0, 80)}`)
      console.log()
    }
  }
}

else if (command === 'list') {
  const category = getOpt(args, '--category') || getOpt(args, '-c')
  const prompts = listPrompts(category)
  for (const p of prompts) {
    console.log(`[${p.category.padEnd(12)}] ${p.name}`)
  }
}

else if (command === 'stats') {
  const stats = categories()
  for (const [k, v] of Object.entries(stats)) {
    console.log(`  ${k.padEnd(15)} ${v}`)
  }
}

else {
  console.error(`Unknown command: ${command}`)
  help()
  process.exit(1)
}
