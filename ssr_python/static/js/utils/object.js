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
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:24',message:'deepMerge entry',data:{targetKeys:Object.keys(target),numSources:sources.length,source0Keys:sources[0]?Object.keys(sources[0]):'null',source1Keys:sources[1]?Object.keys(sources[1]):'null'},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
    // #endregion
    for (const source of sources) {
        if (!source || typeof source !== 'object') {
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:27',message:'deepMerge skipping source',data:{sourceType:typeof source,isNull:source===null,isUndefined:source===undefined},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            // #endregion
            continue;
        }
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:30',message:'deepMerge processing source',data:{sourceKeys:Object.keys(source),targetKeysBefore:Object.keys(target)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
        // #endregion
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
                // #region agent log
                fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:37',message:'deepMerge recursive merge',data:{key,base:JSON.stringify(base),incoming:JSON.stringify(incoming)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
                // #endregion
                target[key] = deepMerge(base, incoming);
                // #region agent log
                fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:42',message:'deepMerge after recursive merge',data:{key,result:JSON.stringify(target[key])},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
                // #endregion
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
    // #region agent log
    fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:71',message:'setNestedValue entry',data:{path:Array.isArray(path)?path:path,value,objKeys:Object.keys(obj||{})},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
    // #endregion
    if (!obj) {
        throw new Error('Cannot set path on undefined object');
    }
    const segments = Array.isArray(path) ? path : String(path).split('.').filter(Boolean);
    let cursor = obj;
    for (let index = 0; index < segments.length; index += 1) {
        const key = segments[index];
        // #region agent log
        fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:82',message:'setNestedValue loop',data:{index,key,isLast:index===segments.length-1,cursorKeys:Object.keys(cursor||{}),cursorValue:JSON.stringify(cursor[key])},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
        // #endregion
        if (index === segments.length - 1) {
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:85',message:'setNestedValue setting final value',data:{key,oldValue:cursor[key],newValue:value},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
            // #endregion
            cursor[key] = value;
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:88',message:'setNestedValue exit',data:{finalObj:JSON.stringify(obj)},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
            // #endregion
            return;
        }
        if (!cursor[key] || typeof cursor[key] !== 'object') {
            // #region agent log
            fetch('http://127.0.0.1:7242/ingest/f73c7dd3-dc04-444a-a31b-ff398b1c3504',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'object.js:91',message:'setNestedValue creating intermediate object',data:{key,wasObject:typeof cursor[key]==='object',oldValue:JSON.stringify(cursor[key])},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'})}).catch(()=>{});
            // #endregion
            cursor[key] = {};
        }
        cursor = cursor[key];
    }
}

