import { type ClassValue, clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge class names with Tailwind CSS
 * Combines clsx and tailwind-merge for optimal class handling
 */
export function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

/**
 * Format a date to a human-readable string in Russian
 */
export function formatDate(date: Date | string | null | undefined): string {
    if (!date) return '—';

    try {
        const d = typeof date === 'string' ? new Date(date) : date;
        return new Intl.DateTimeFormat('ru-RU', {
            day: '2-digit',
            month: 'long',
            year: 'numeric'
        }).format(d);
    } catch {
        return '—';
    }
}

/**
 * Format a time string to MSK time
 */
export function formatTimeMSK(time: string | null | undefined): string {
    if (!time) return '';

    try {
        const date = new Date(time);
        return date.toLocaleTimeString('ru-RU', {
            hour: '2-digit',
            minute: '2-digit',
            timeZone: 'Europe/Moscow'
        });
    } catch {
        return '';
    }
}

/**
 * Truncate text to a specified length
 */
export function truncateText(text: string | null | undefined, maxLength: number = 100): string {
    if (!text) return '';

    if (text.length <= maxLength) return text;

    return text.substring(0, maxLength) + '...';
}

/**
 * Check if a value is a valid number
 */
export function isValidNumber(value: unknown): value is number {
    return typeof value === 'number' && !isNaN(value);
}

/**
 * Capitalize the first letter of a string
 */
export function capitalizeFirstLetter(str: string): string {
    if (!str) return str;
    return str.charAt(0).toUpperCase() + str.slice(1);
}