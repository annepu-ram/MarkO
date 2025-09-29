/**
 * Creates a deep clone of a value using JSON serialization.
 * This is a simple way to create a new object with no references to the original.
 * Note: This will not work for functions, undefined, or other non-JSON values.
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

export function getNestedValue(obj, path) {
    if (!obj) {
        return undefined;
    }
    const segments = Array.isArray(path) ? path : String(path).split('.');
    return segments.reduce((acc, segment) => (acc ? acc[segment] : undefined), obj);
}

export function setNestedValue(obj, path, value) {
    if (!obj) {
        throw new Error('Cannot set path on undefined object');
    }
    const segments = Array.isArray(path) ? path : String(path).split('.');
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

export function deleteNestedValue(obj, path) {
    if (!obj) {
        return;
    }
    const segments = Array.isArray(path) ? path : String(path).split('.');
    let cursor = obj;
    for (let index = 0; index < segments.length - 1; index += 1) {
        const key = segments[index];
        if (!cursor[key] || typeof cursor[key] !== 'object') {
            return;
        }
        cursor = cursor[key];
    }
    delete cursor[segments[segments.length - 1]];
}

export function pruneEmptyValues(target) {
    if (!target || typeof target !== 'object') {
        return;
    }
    Object.keys(target).forEach(key => {
        const value = target[key];
        if (value && typeof value === 'object') {
            pruneEmptyValues(value);
            if (Object.keys(value).length === 0) {
                delete target[key];
            }
        } else if (value === '' || value === null || value === undefined) {
            delete target[key];
        }
    });
}