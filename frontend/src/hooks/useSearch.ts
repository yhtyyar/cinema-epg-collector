import { useState, useEffect, useCallback } from 'react';
import { useDebounce } from './useDebounce';

/**
 * Хук для управления поисковым запросом с debounce
 */
export function useSearch(initialQuery: string = '') {
    const [query, setQuery] = useState(initialQuery);
    const [isSearching, setIsSearching] = useState(false);
    const debouncedQuery = useDebounce(query, 300);

    const handleSearch = useCallback((newQuery: string) => {
        setQuery(newQuery);
    }, []);

    const clearSearch = useCallback(() => {
        setQuery('');
    }, []);

    useEffect(() => {
        setIsSearching(debouncedQuery !== '');
    }, [debouncedQuery]);

    return {
        query,
        debouncedQuery,
        isSearching,
        handleSearch,
        clearSearch
    };
}