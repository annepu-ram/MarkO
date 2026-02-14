/**
 * Utility functions for object manipulation
 * Adapted from CSR version for SSR
 */

/**
 * Creates a deep clone of a value using JSON serialization.
 * @param {*} value The value to clone.
 * @returns {*} The cloned value.
 */
export function deepClone(value) {
    if (value === undefined) {
        return undefined;
    }
    return JSON.parse(JSON.stringify(value));
}

/**
 * Recursively merges properties of one or more source objects into a target object.
 * @param {object} target The object to merge into.
 * @param  {...object} sources The objects to merge from.
 * @returns {object} The merged object.
 */
export function deepMerge(target = {}, ...sources) {
    for (const source of sources) {
        if (!source || typeof source !== 'object') {
            continue;
        }
        for (const key of Object.keys(source)) {
            const incoming = source[key];
            if (Array.isArray(incoming)) {
                target[key] = incoming.map(item =>
                    typeof item === 'object' && item !== null ? deepClone(item) : item
                );
                continue;
            }
            if (incoming && typeof incoming === 'object') {
                const current = target[key];
                const base = current && typeof current === 'object' ? current : {};
                target[key] = deepMerge(base, incoming);
                continue;
            }
            if (incoming !== undefined) {
                target[key] = incoming;
            }
        }
    }
    return target;
}

/**
 * Gets a nested value from an object using a path array or dot-separated string.
 * @param {object} obj The object to get the value from.
 * @param {Array|string} path The path to the value.
 * @returns {*} The value at the path, or undefined if not found.
 */
export function getNestedValue(obj, path) {
    if (!obj) {
        return undefined;
    }
    const segments = Array.isArray(path) ? path : String(path).split('.').filter(Boolean);
    return segments.reduce((acc, segment) => (acc ? acc[segment] : undefined), obj);
}

/**
 * Sets a nested value in an object using a path array or dot-separated string.
 * @param {object} obj The object to set the value in.
 * @param {Array|string} path The path to set the value at.
 * @param {*} value The value to set.
 */
export function setNestedValue(obj, path, value) {
    if (!obj) {
        throw new Error('Cannot set path on undefined object');
    }
    const segments = Array.isArray(path) ? path : String(path).split('.').filter(Boolean);
    let cursor = obj;
    for (let index = 0; index < segments.length; index += 1) {
        const key = segments[index];
        if (index === segments.length - 1) {
            cursor[key] = value;
            return;
        }
        if (!cursor[key] || typeof cursor[key] !== 'object') {
            cursor[key] = {};
        }
        cursor = cursor[key];
    }
}
