/**
 * Test file to verify the refactored frontend components work correctly
 */

import { cn } from './lib/utils';
import { API_ENDPOINTS, QUERY_KEYS, DEFAULTS } from './lib/constants';
import { isApiError } from './lib/errors';

// Test utility functions
console.log('Testing cn utility:', cn('class1', 'class2'));
console.log('Testing constants:', API_ENDPOINTS.MOVIES);
console.log('Testing query keys:', QUERY_KEYS.MOVIES);
console.log('Testing defaults:', DEFAULTS.PAGE_SIZE);

// Test error utilities
const testError = new Error('Test error');
console.log('Testing isApiError:', isApiError(testError));

console.log('Frontend refactoring test completed successfully!');