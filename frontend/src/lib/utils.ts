import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** Combina clases de Tailwind de forma segura (requerido por shadcn/ui) */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(...inputs))
}
